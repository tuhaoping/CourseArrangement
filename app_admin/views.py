from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from app_getcontent.models import TeacherList, OpenCourse, CourseNeedToOpen, CourseList, CourseFor, PlaceList, CourseSetting, Semester1CourseOfGrade1, CourseRelatedPlace
from django.db import transaction, IntegrityError
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMultiAlternatives

import string, random, datetime
def random_generator(size=20, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def login(request):
	if 'next' in request.GET:
		next_url = request.GET['next']
	else:
		next_url = settings.ROOT_URL + '/admin'

	if request.user.is_authenticated() and request.user.is_staff:
		return HttpResponseRedirect(next_url)
	
	else:
	
		try:
			username = request.POST['username']
			password = request.POST['password']
			user = auth.authenticate(username=username, password=password)

			if user is not None and user.is_staff:
				auth.login(request, user)
				return HttpResponseRedirect(next_url)
	
			else:
				return render(request, 'registration/login_admin.html', {'next_url':next_url, 'no_perm':True})
		except:
			return render(request, 'registration/login_admin.html', {'next_url':next_url})

def logout(request):
	auth.logout(request)
	return render(request, 'registration/logout_admin.html')


# @staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_main(request):
	user_firstname = request.user.first_name
	teacher_info = TeacherList.objects.all().order_by('-isdirector', 'title_order')
	all_course = OpenCourse.objects.all()
	grade_total = [{'grade':'大一', 'num':0}, {'grade':'大二', 'num':0}]
	grade_week = [{'grade1':{'open':0}, 'grade2_girl':{'open':0}, 'grade2_boy':{'open':0}} for week in range(1,6)]
	need_open = CourseNeedToOpen.objects.all()

	for course in all_course:
		week = course.week-1
		if 1 <= course.forwhom.id <= 3:
			grade_total[0]['num'] += 1
			grade_week[week]['grade1']['open'] += 1
		elif course.forwhom.id == 4:
			grade_total[1]['num'] += 1
			grade_week[week]['grade2_boy']['open'] += 1
		elif course.forwhom.id == 5:
			grade_total[1]['num'] += 1
			grade_week[week]['grade2_girl']['open'] += 1
		elif course.forwhom.id == 6:
			grade_total[1]['num'] += 1
			grade_week[week]['grade2_boy']['open'] += 0.5
			grade_week[week]['grade2_girl']['open'] += 0.5

	if CourseSetting.objects.get(pk=1).value == '1':
		grade1_course = Semester1CourseOfGrade1.objects.exclude(teacher__isnull=True)
		for course in grade1_course:
			week = course.week -1 
			grade_total[0]['num'] += 1
			grade_week[week]['grade1']['open'] += 1

	for need in need_open:
		if need.grade == '大一':
			grade = 'grade1'
		elif need.grade == '二男':
			grade = 'grade2_boy'
		elif need.grade == '二女':
			grade = 'grade2_girl'

		grade_week[0][grade]['need'] = need.mon
		grade_week[1][grade]['need'] = need.tue
		grade_week[2][grade]['need'] = need.wed
		grade_week[3][grade]['need'] = need.thu
		grade_week[4][grade]['need'] = need.fri

	for i,day in enumerate(grade_week):
		grade_week[i]['total'] = day['grade1']['open'] + day['grade2_boy']['open'] + day['grade2_girl']['open']
		grade_week[i]['need_total'] = day['grade1']['need'] + day['grade2_boy']['need'] + day['grade2_girl']['need']

	render_dict = {
		'admin':True,
		'range5':range(5),
		'teacher_info':teacher_info,
		'open_course_grade':grade_total,
		'open_course_perday':grade_week,
		# 'test':test
	}
	# print(user_firstname)
	return render(request, 'admin_index.html', render_dict)

@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_arrange_teachers(request):
	teachers = TeacherList.objects.all()
	try:
		checked = request.GET['next']
	except:
		checked = None
	
	render_dict = {
		'admin':True,
		'teachers':teachers,
		'checked':checked,
	}

	return render(request, 'admin_arrange_teachers.html', render_dict)
@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_arrange_teachers_table(request):
	teacherid = request.GET['teacherid']
	teacher = TeacherList.objects.get(userid__id=teacherid)
	semester = CourseSetting.objects.get(pk=1).value

	courses = teacher.open_course.all()

	num_grade1 = courses.filter(forwhom__lte=3).count()
	num_grade2 = courses.filter(forwhom__gte=4).count()
	grade_num = [{'grade':'大一','num':num_grade1}, {'grade':'大二','num':num_grade2}]
	
	place = PlaceList.objects.all()
	
	already_arrange = [[],[],[],[],[]]
	for course in courses:
		already_arrange[course.week-1].append(course.time)

	if semester == '1':
		del grade_num[0]
		course_for = CourseFor.objects.exclude(id__in=[1,2,3])
		g_course = Semester1CourseOfGrade1.objects.filter(teacher=teacher)
		for course in g_course:
			already_arrange[course.week-1].append(course.time)
	else:
		course_for = CourseFor.objects.all()


	# courses = teachers[0].open_course.all()
	render_dict = {
		'admin':True,
		'semester': semester,
		'teacher':teacher,
		'course_for':course_for,
		'places':place,
		'r5':range(5),
		'courses':courses,
		'grade_num':grade_num,
		'already_arrange':already_arrange,
	}

	return render(request, 'admin_arrange_teachers_table.html', render_dict)
	# print(teacher.open_course.all())
	# return HttpResponse(status=200)


@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_arrange_places(request):
	place = PlaceList.objects.filter(valid=True)
	render_dict = {
		'admin':True,
		'places':place,
		'r5':range(5),
	}

	return render(request, 'admin_arrange_places.html', render_dict)
@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_place_use(request):
	placeid = request.GET['placeid']
	places = PlaceList.objects.get(pk=placeid)
	data = []
	for p in places.open_course.all():
		data.append({
			'teacher':p.user_id.userid.last_name + p.user_id.userid.first_name,
			'course':p.course.course_name,
			'week':p.week,
			'time':p.time,
			})
	return JsonResponse({'data':data})

@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_data_teachers(request, method=None):
	if method == 'remove':
		teacherid = request.POST['teacherid']
		user = User.objects.get(id=teacherid)
		user.delete()

		teachers = TeacherList.objects.all().order_by('order')
		order = 0
		for teacher in teachers:
			order += 1
			teacher.order = order
			teacher.save()
	elif method == 'add':
		title_list = ['特聘教授', '教授', '副教授', '助理教授', '講師', '兼任副教授', '兼任助理教授', '兼任講師']
		last_name = request.POST['name'][0]
		first_name = request.POST['name'][1:]
		title = request.POST['title']
		title_order = title_list.index(title)
		isdirector = int(request.POST['isdirector'])
		account = random_generator(10)
		pwd = random_generator(20)
		email = request.POST['mail']
		
		user = User.objects.create_user(
			username=account,
			password=pwd,
			first_name=first_name,
			last_name=last_name,
			email=email,
		)
		count = TeacherList.objects.all().count()
		if isdirector:
			TeacherList.objects.all().update(isdirector=0)
		TeacherList.objects.create(
			userid=user,
			title_teacher=title,
			isdirector=isdirector,
			order=count+1,
			title_order=title_order
		)
	elif method == 'modify':
		title_list = ['特聘教授', '教授', '副教授', '助理教授', '講師', '兼任副教授', '兼任助理教授', '兼任講師']
		teacherid = request.POST['teacherid']
		teacher = TeacherList.objects.get(userid__id=teacherid)
		teacher.userid.last_name = request.POST['name'][0]
		teacher.userid.first_name = request.POST['name'][1:]
		teacher.userid.email = request.POST['mail']
		teacher.userid.save()

		isdirector = int(request.POST['isdirector'])

		if isdirector:
			TeacherList.objects.all().update(isdirector=0)

		title = request.POST['title']
		teacher.title_teacher = title
		title_order = title_list.index(title)
		teacher.isdirector = isdirector
		teacher.save()

	else:
		teachers = TeacherList.objects.all().order_by('order')

		render_dict = {
			'admin':True,
			'teachers':teachers,
		}
		return render(request, 'admin_data_teachers.html', render_dict)

	return HttpResponseRedirect(settings.ROOT_URL+'/admin/data/teachers/')
@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_data_places(request, method=None):
	if method == 'remove':
		placeid = request.POST['placeid']
		place = PlaceList.objects.get(id=placeid)
		place.delete()

	elif method == 'add':
		first_num = request.POST['firstTitle']
		second_num = request.POST['secondTitle']
		place = request.POST['name']
		note = request.POST['note']

		new_place = PlaceList.objects.create(
			first_num = first_num,
			second_num = second_num,
			place = place,
			note = note,
			valid = 1
		)
	elif method == 'modify':
		placeid = request.POST['placeid']
		place = PlaceList.objects.get(id=placeid)
		place.first_num = request.POST['firstTitle']
		place.second_num = request.POST['secondTitle']
		place.place = request.POST['name']
		place.note = request.POST['note']
		place.save()

	else:
		place = PlaceList.objects.filter(valid=True)

		render_dict = {
			'admin':True,
			'places':place,
			'r5':range(5),
		}
		return render(request, 'admin_data_places.html', render_dict)
	
	return HttpResponseRedirect(settings.ROOT_URL+'/admin/data/places/')
@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_data_courses(request, method=None):
	if method == 'remove':
		courseid = request.POST['courseid']
		course = CourseList.objects.get(id=courseid)
		course.delete()

	elif method == 'add':
		courseName = request.POST['courseName']
		courseType = request.POST['courseType']
		grade = request.POST['grade']
		course_place = request.POST.getlist('course_place')

		new_course = CourseList.objects.create(
			course_name=courseName,
			course_type=courseType,
			course_grade=grade
		)

		for place in course_place:
			place = PlaceList.objects.get(pk=place)
			CourseRelatedPlace.objects.create(course=new_course, place=place)

	elif method == 'modify':
		courseid = request.POST['courseid']
		courseName = request.POST['courseName']
		courseType = request.POST['courseType']
		grade = request.POST['grade']
		course_place = request.POST.getlist('course_place')
		
		course = CourseList.objects.get(pk=courseid)
		course.course_name = courseName
		course.course_type = courseType
		course.course_grade = grade
		course.save()

		CourseRelatedPlace.objects.filter(course=course).delete()
		for place in course_place:
			place = PlaceList.objects.get(pk=place)
			CourseRelatedPlace.objects.create(course=course, place=place)


	else:
		courses = CourseList.objects.all().order_by('course_grade', 'course_name')
		places = PlaceList.objects.filter(valid=True)
		render_dict = {
			'admin':True,
			'courses':courses,
			'r5':range(5),
			'places':places
		}
		return render(request, 'admin_data_courses.html', render_dict)
	return HttpResponseRedirect(settings.ROOT_URL+'/admin/data/courses/')

def admin_courses_place(request, method=None):
	courseid = request.GET['courseid']
	course = CourseList.objects.get(pk=courseid)
	course_place = course.places.filter(valid=True).values_list('id', flat=True)
	d = {
		'place':list(course_place),
		'name':course.course_name,
		'type':course.course_type,
		'grade':course.course_grade
	}
	return JsonResponse(d)



@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_coursesetting(request, method=None):
	if method == 'update':
		need_open = CourseNeedToOpen.objects.all()
		grade1_courses = Semester1CourseOfGrade1.objects.all().order_by('-dep')

		teachers = request.POST.getlist('teacher')
		week = request.POST.getlist('grade_week')
		time = request.POST.getlist('grade_time')

		for i,(teacher,week,time) in enumerate(zip(teachers,week,time)):
			teacher = TeacherList.objects.get(pk=teacher) if teacher != '0' else None
			course = grade1_courses[i]
			course.teacher = teacher
			course.week = week
			course.time = time
			course.save()

		need = [
			request.POST.getlist('need1'),
			request.POST.getlist('need2'),
			request.POST.getlist('need3')
		]
		
		count = 0
		for n in need_open:
			n.mon = need[count][0]
			n.tue = need[count][1]
			n.wed = need[count][2]
			n.thu = need[count][3]
			n.fri = need[count][4]
			n.save()
			count += 1


	else:
		need_open = CourseNeedToOpen.objects.all()
		semester = CourseSetting.objects.get(pk=1).value
		grade1_course = Semester1CourseOfGrade1.objects.all().order_by('-dep') if semester else None
		teachers = TeacherList.objects.all()
		automail = True if CourseSetting.objects.get(pk=2).value == '1' else False

		render_dict = {
			'admin':True,
			'automail':automail,
			'semester': semester,
			'teachers':teachers,
			'grade1_course':grade1_course,
			'need_open':need_open,
			'r5':range(5),
		}
		return render(request, 'admin_coursesetting.html', render_dict)
	
	return HttpResponseRedirect(settings.ROOT_URL+'/admin/coursesetting/')

@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
def admin_change_permission(request):
	group = Group.objects.get(name='CanOpenCourse')
	try:
		ori_teacher = User.objects.get(pk=request.POST['ori'])
		ori_teacher.groups.remove(group)
	except:
		# return HttpResponse(status=500)
		pass

	try:
		new_teacher = User.objects.get(pk=request.POST['new'])
		new_teacher.groups.add(group)
	except:
		pass

	return HttpResponse(status=200)



@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
@transaction.atomic
def admin_change_setting(request):
	item = request.POST['item']
	val = request.POST['value']
	setting = CourseSettingChange()

	setting.change(item, val)
	if item == '1':
		Semester1CourseOfGrade1.objects.all().update(teacher=None)
		need_open = CourseNeedToOpen.objects.all().update(mon=0, tue=0, wed=0, thu=0, fri=0)
		OpenCourse.objects.all().delete()
	
	return HttpResponse(status=200)


@staff_member_required(login_url = settings.ROOT_URL+'/admin/accounts/login/')
@transaction.atomic
def admin_mail(request):
	teacherid = request.POST['teacherid']
	teacher = User.objects.get(pk=teacherid)
	account = random_generator(10)
	pwd = random_generator(20)
	teacher.username = account
	teacher.set_password(pwd)
	teacher.save()

	try:
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
			'''.format(teacher.last_name + teacher.first_name, account, pwd)
		mail_from = settings.DEFAULT_FROM_EMAIL
		mail_to = "{} <{}>".format(teacher.last_name + teacher.first_name, teacher.email)

		msg = EmailMultiAlternatives(mail_subject, mail_content, mail_from, [mail_to], bcc=[mail_from])
		msg.attach_alternative(mail_content, "text/html")
		msg.send()
		return HttpResponse("success", status=200)
	except:
		return HttpResponseBadRequest("fail")
	






class CourseSettingChange(object):
	def __init__(self):
		self.setting = CourseSetting.objects.all()
	
	def change(self, item, val):
		s = self.setting.get(pk=item)
		s.value = str(val)
		s.save()

	def get_value(self, item):
		s = self.setting.get(pk=item)
		return s.value