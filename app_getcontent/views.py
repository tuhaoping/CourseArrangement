from django.shortcuts import render, redirect
from .models import TeacherList, PlaceList, CourseFor, CourseList, OpenCourse, CourseSetting, Semester1CourseOfGrade1
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

import string, random

def not_staff(func):
	def wrapper(request, *args, **kwargs):
		if request.user.is_staff:
			return HttpResponseRedirect(settings.ROOT_URL + '/admin/')
		return func(request, *args, **kwargs)
	return wrapper

def get_arrange_table(request):
	teacher_info = TeacherList.objects.all()
	course_data = []

	for teacher in  teacher_info:
		# print(teacher, teacher.open_course.all())
		courses = teacher.open_course.all()
		for course in courses:
			course_data.append({
				'userid':teacher.userid.id,
				'course_time':(course.week-1)*5+course.time,
				'course_type':course.course.course_type,
				'course_for':course.forwhom.forwhom,
				'course_place':course.place.first_num
			})

	if CourseSetting.objects.get(pk=1).value == '1':
		grade1_courses = Semester1CourseOfGrade1.objects.exclude(teacher__isnull=True)
		for course in grade1_courses:
			course_data.append({
				'userid':course.teacher.userid.id,
				'course_time':(course.week-1)*5+course.time,
				'course_type':'',
				'course_for':'大一',
				'course_place':course.dep
			})

	return JsonResponse({'course_data':course_data})


def get_available_place(request):
	# pass
	teacher = request.user.teacherlist
	place = request.GET['place']
	# print(place)
	place_data = []
	unavailable_place = PlaceList.objects.get(pk=place).open_course.all()
	semester = CourseSetting.objects.get(pk=1).value

	for un_place in unavailable_place:
		place_data.append({'week':un_place.week, 'time':un_place.time, 'type':'place'})
	
	return JsonResponse({'place_data':place_data})
   

def get_course_with_grade(request):
	# pass
	forwhom = int(request.GET['whom'])
	grade = 1 if 1<=forwhom<=3 else 2

	course = CourseList.objects.filter(course_grade=grade)
	if forwhom in [1,4]:
		course = course.exclude(course_name__contains='女')
	elif forwhom in [2,5]:
		course = course.exclude(course_name__contains='男')
	else:
		course = course.exclude(course_name__regex=r'.+（(男|女)?）')

	return JsonResponse({'data':list(course.values('id', 'course_name'))})

def get_course_place(request):
	courseid = int(request.GET['courseid'])
	places = CourseList.objects.get(pk=courseid).places.filter(valid=True)
	# place_list = []
	# for place in places:
	# 	place_list.append({
	# 		'id':place.id,
	# 		'num':place.first_num,
	# 		'name':place.place,
	# 		'note':place.note})
	# print(place)
	return JsonResponse({'data':list(places.values('id','first_num','place','note'))})


@login_required(login_url=settings.LOGIN_URL)
@not_staff
def get_mycourse(request):
	user = request.user
	user_firstname = user.first_name
	course_name = CourseList.objects.all()
	place = PlaceList.objects.filter(valid=True)

	courses = user.teacherlist.open_course.all()
	num_grade1 = courses.filter(forwhom__lte=3).count()
	num_grade2 = courses.filter(forwhom__gte=4).count()
	grade_num = [{'grade':'大一','num':num_grade1}, {'grade':'大二','num':num_grade2}]
	semester = CourseSetting.objects.get(pk=1).value
	
	already_arrange = [[],[],[],[],[]]
	for course in courses:
		already_arrange[course.week-1].append(course.time)

	if semester == '1':
		del grade_num[0]
		course_for = CourseFor.objects.exclude(id__in=[1,2,3])
		g_course = Semester1CourseOfGrade1.objects.filter(teacher=user.teacherlist)
		for course in g_course:
			already_arrange[course.week-1].append(course.time)
	else:
		course_for = CourseFor.objects.all()

	render_dict = {
		'semester': semester,
		'user_firstname':user_firstname,
		'course_name':course_name,
		'course_for':course_for,
		'already_arrange':already_arrange,
		'places':place,
		'r5':range(5),
		'courses':courses,
		'grade_num':grade_num
	}

	return render(request, 'mycourse.html', render_dict)

@login_required(login_url=settings.LOGIN_URL)
@not_staff
def get_grade1_course(request):
	user = request.user
	user_firstname = user.first_name
	courses = user.teacherlist.grade1_course.all()
	grade1_course = Semester1CourseOfGrade1.objects.all().order_by('time', 'week')
	grade2_course = OpenCourse.objects.filter(user_id=user.teacherlist)
	course_list = [
		[[],[],[],[],[]],
		[[],[],[],[],[]],
		[[],[],[],[],[]],
		[[],[],[],[],[]],
		[[],[],[],[],[]],
	]
	for course in grade1_course:
		course_list[course.time-1][course.week-1].append(course)
	
	render_dict = {
		'semester': CourseSetting.objects.get(pk=1).value,
		'user_firstname':user_firstname,
		'grade1_courses':course_list,
		'grade2_courses':grade2_course,
		'courses':courses,
		'r5':range(5),
	}

	return render(request, 'mycourse.semester1.html', render_dict)

def update_grade1_course(request):
	user = request.user
	courses = request.POST.getlist('courseid')
	iseng = request.POST.get('iseng')
	Semester1CourseOfGrade1.objects.filter(id__in=courses).update(teacher=user.teacherlist, isEng=iseng)
	return HttpResponseRedirect(settings.ROOT_URL+'/mycourse/grade1/')

def del_grade1_course(request):
	user = request.user
	courses = request.POST.getlist('courseid')
	Semester1CourseOfGrade1.objects.filter(id__in=courses).update(teacher=None)
	
	return HttpResponseRedirect(settings.ROOT_URL+'/mycourse/grade1/')


def get_course_info(request):
	course = OpenCourseInfo(request.GET['openid'])
	info = course.info(True)
	return JsonResponse(info)

@login_required(login_url=settings.LOGIN_URL)
def create_new_course(request):
	try:
		user = TeacherList.objects.get(userid=request.POST['teacherid']).userid
	except:
		user = request.user

	course = OpenCourseInfo()

	course.create_course(user, **request.POST)
	if 'next' in request.POST:
		return HttpResponseRedirect(settings.ROOT_URL+'/admin/arrange/teachers?next=' + request.POST['next'])
	return HttpResponseRedirect(settings.ROOT_URL+'/mycourse/')

@login_required(login_url=settings.LOGIN_URL)
def modify_open_course(request):
	user = request.user
	openid = request.POST['openid']
	course = OpenCourseInfo(openid)
	course.modify_course(**request.POST)
	# print(course.info())

	# course.create_course(user, **request.POST)
	if 'next' in request.POST:
		return HttpResponseRedirect(settings.ROOT_URL+'/admin/arrange/teachers?next=' + request.POST['next'])
	return HttpResponseRedirect(settings.ROOT_URL+'/mycourse/')

@login_required(login_url=settings.LOGIN_URL)
def delete_open_course(request):
	user = request.user
	course = OpenCourseInfo(request.POST['openid'])
	course.delete_course()

	if 'next' in request.POST:
		return HttpResponseRedirect(settings.ROOT_URL+'/admin/arrange/teachers?next=' + request.POST['next'])
	return HttpResponseRedirect(settings.ROOT_URL+'/mycourse/')


@login_required(login_url=settings.LOGIN_URL)
def arrange_done(request):
	import datetime
	def random_generator(size=20, chars=string.ascii_letters + string.digits):
			return ''.join(random.choice(chars) for _ in range(size))

	g = Group.objects.get(name='CanOpenCourse')
	user = request.user
	user.groups.remove(g)

	try:
		next_teacher = TeacherList.objects.get(order=user.teacherlist.order+1).userid
		next_teacher.groups.add(g)
		account = random_generator(10)
		pwd = random_generator(20)
		next_teacher.username = account
		next_teacher.set_password(pwd)
		next_teacher.save()
 
		now = datetime.datetime.now()
		if 3<=now.month<=8:
			mail_subject = "{}學年度第1學期排課通知".format(now.year-1911)
		elif now.month in [1,2]:
			mail_subject = "{}學年度第2學期排課通知".format(now.year-1912)
		else:
			mail_subject = "{}學年度第2學期排課通知".format(now.year-1911)

		mail_content = '''
			{} 老師您好：<br><br>

			請點擊前往下方連結，並盡快完成排課，謝謝 <br>
			<a href="http://140.116.219.103/CourseArrangement/home/">http://140.116.219.103/CourseArrangement/home/</a> <br><br>
			帳號：{} <br>
			密碼：{} <br>
			'''.format(next_teacher.last_name + next_teacher.first_name, account, pwd)
		mail_from = settings.DEFAULT_FROM_EMAIL
		mail_to = "{} <{}>".format(next_teacher.last_name + next_teacher.first_name, next_teacher.email)

		if CourseSetting.objects.get(pk=2).value == '1':
			msg = EmailMultiAlternatives(mail_subject, mail_content, mail_from, [mail_to], bcc=[mail_from])
		else:
			msg = EmailMultiAlternatives(mail_subject, mail_content, mail_from, [mail_from])

		msg.attach_alternative(mail_content, "text/html")
		msg.send()
	except:
		pass
	

	return HttpResponseRedirect(settings.ROOT_URL+'/confirm/')


@login_required(login_url=settings.LOGIN_URL)
@not_staff
def confirm(request, teacherID=None):
	user = request.user
	teacher = user.teacherlist
	semester = CourseSetting.objects.get(pk=1).value
	courses = teacher.open_course.all()

	render_dict = {
		'semester':semester,
		'user_firstname':user.first_name,
		'courses': courses,
		'r5':range(5)
	}

	if semester == '1':
		grade1_course = teacher.grade1_course.all()
		render_dict.update({'grade1_courses':grade1_course})
	else:
		num_grade1 = courses.filter(forwhom__lte=3).count()
		num_grade2 = courses.filter(forwhom__gte=4).count()
		grade_num = [{'grade':'大一','num':num_grade1}, {'grade':'大二','num':num_grade2}]
		render_dict.update({'grade_num':grade_num})


	return render(request, 'confirm.html', render_dict)
	

class OpenCourseInfo(object):
	def __init__(self, openid=None):
		if openid:
			self.course = OpenCourse.objects.get(pk=openid)
			self.name = self.course.course
			self.place = self.course.place
			self.forwhom = self.course.forwhom
			self.isEng = self.course.isEng
			self.week = self.course.week
			self.time = self.course.time
		else:
			self.course = "Haven't create a OpenCourseInfo class"
			self.name = ''
			self.place = ''
			self.forwhom = ''
			self.isEng = ''
			self.week = ''
			self.time = ''
	
	def __str__(self):
		return self.course

	def info(self, useid=False):
		if useid:
			info = {
				'courseid':self.course.course.id,
				'forwhom':self.course.forwhom.id,
				'isEng':self.isEng,
				'place':self.course.place.id,
				'week':self.course.week,
				'time':self.course.time,
			}
			return info
		else:
			info = {
				'courseid':self.course.course,
				'forwhom':self.course.forwhom,
				'place':self.course.place,
				'week':self.course.week,
				'time':self.course.time,
			}
			return info
		# print(self.name,self.place,self.forwhom,self.week,self.time)

	def create_course(self, user, **karg):
		self.name = CourseList.objects.get(pk=karg['course.name'][0])
		self.place = PlaceList.objects.get(pk=karg['course.place'][0])
		self.forwhom = CourseFor.objects.get(pk=karg['course.forwhom'][0])
		self.isEng = karg['course.isEng'][0]
		self.week = karg['course.week'][0]
		self.time = karg['course.time'][0]

		self.course = OpenCourse.objects.create(
			course = self.name,
			place = self.place,
			forwhom = self.forwhom,
			isEng = self.isEng,
			week = self.week,
			time = self.time,
			user_id = TeacherList.objects.get(pk=user.id)
		)
		return self.course

	def modify_course(self, **karg):
		self.course.course = self.name = CourseList.objects.get(pk=int(karg['course.name'][0]))
		self.course.place = self.place = PlaceList.objects.get(pk=int(karg['course.place'][0]))
		self.course.forwhom = self.forwhom = CourseFor.objects.get(pk=int(karg['course.forwhom'][0]))
		self.course.isEng = self.isEng = pk=karg['course.isEng'][0]
		self.course.week = self.week = karg['course.week'][0]
		self.course.time = self.time = karg['course.time'][0]

		self.course.save()
		return self.course

	def delete_course(self):
		self.course.delete()