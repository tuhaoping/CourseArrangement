from django.shortcuts import render, redirect
from .models import TeacherList, PlaceList, CourseFor, CourseList, OpenCourse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.conf import settings

from pprint import pprint

def get_arrange_table(request):
    teacher_info = TeacherList.objects.all()
    course_data = []
    for teacher in  teacher_info:
    	# print(teacher, teacher.opencourse_set.all())
    	courses = teacher.opencourse_set.all()
    	for course in courses:
    		course_data.append({
    			'userid':teacher.userid.id,
    			'course_time':(course.week-1)*5+course.time,
    			'course_type':course.course.course_type,
    			'course_for':course.forwhom.forwhom,
    			'course_place':course.place.first_num
			})

    return JsonResponse({'course_data':course_data})
   

def get_available_place(request):
	# pass
	place = request.GET['place']
	# print(place)
	place_data = []
	unavailable_place = PlaceList.objects.get(pk=place).opencourse_set.all()
	for un_place in unavailable_place:
		place_data.append({'week':un_place.week, 'time':un_place.time})

	return JsonResponse({'place_data':place_data})

@login_required
def get_mycourse(request):
	user = request.user
	user_firstname = user.first_name
	course_name = CourseList.objects.all()
	course_for = CourseFor.objects.all()
	place = PlaceList.objects.all()

	courses = user.teacherlist.opencourse_set.all()

	render_dict = {
		'user_firstname':user_firstname,
		'course_name':course_name,
		'course_for':course_for,
		'places':place,
		'r5':range(5),
		'courses':courses
	}

	return render(request, 'mycourse.html', render_dict)


@login_required
def test(request):
	user = request.user
	course = CourseInfo(**request.POST)

	course.info
	# print(user.id)
	# print(TeacherList.objects.get(pk=user.id))
	course.create_course(user)

	return HttpResponseRedirect(settings.ROOT_URL+'/mycourse/')
	# return HttpResponse(status=200)



class CourseInfo():
	def __init__(self, **arg):
		self.name = CourseList.objects.get(pk=arg['course.name'][0])
		self.place = PlaceList.objects.get(pk=arg['course.place'][0])
		self.forwhom = CourseFor.objects.get(pk=arg['course.forwhom'][0])
		self.week = arg['course.week'][0]
		self.time = arg['course.time'][0]
	
	@property
	def info(self):
		print(type(self.name),self.place,self.forwhom,self.week,self.time)

	def create_course(self, user):
		OpenCourse.objects.create(
			course = self.name,
			place = self.place,
			forwhom = self.forwhom,
			week = self.week,
			time = self.time,
			user_id = TeacherList.objects.get(pk=user.id)
		)