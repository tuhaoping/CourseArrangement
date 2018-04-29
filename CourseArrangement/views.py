from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from app_getcontent.models import TeacherList

@login_required
def homePage(request):
	user_firstname = request.user.first_name
	teacher_info = TeacherList.objects.all()

	render_dict = {
		'user_firstname':user_firstname,
		'range5':range(5),
		'teacher_info':teacher_info
	}
	# print(user_firstname)
	return render(request, 'index.html', render_dict)


@login_required
def get_mycourser(request):
	user_firstname = request.user.first_name
	return render(request, 'mycourse.html', {'user_firstname':user_firstname})
