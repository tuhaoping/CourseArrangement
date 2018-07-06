from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from app_getcontent.models import TeacherList, OpenCourse, CourseNeedToOpen, CourseSetting, Semester1CourseOfGrade1
from django.conf import settings
from collections import Counter

def not_staff(func):
	def wrapper(request, *args, **kwargs):
		if request.user.is_staff:
			return HttpResponseRedirect(settings.ROOT_URL + '/admin/')
		return func(request, *args, **kwargs)
	return wrapper

@login_required(login_url=settings.LOGIN_URL)
@not_staff
def homePage(request):
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
		'semester': CourseSetting.objects.get(pk=1).value,
		'user_firstname':user_firstname,
		'range5':range(5),
		'teacher_info':teacher_info,
		'open_course_grade':grade_total,
		'open_course_perday':grade_week,
		# 'test':test
	}
	# print(user_firstname)
	return render(request, 'index.html', render_dict)

