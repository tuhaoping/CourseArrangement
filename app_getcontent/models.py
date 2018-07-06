from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class TeacherList(models.Model):
	userid = models.OneToOneField(User, db_column='id', on_delete=models.CASCADE, primary_key=True)
	title_teacher = models.CharField(db_column='教師職稱', max_length=10)
	isdirector = models.IntegerField(db_column='主任')
	order = models.IntegerField(db_column='順序')
	title_order = models.IntegerField(db_column='title_order')

	def __str__(self):
		return self.userid.last_name + self.userid.first_name
	class Meta:
		managed = False
		db_table = '列表_教師'

class CourseFor(models.Model):
	forwhom = models.CharField(db_column='課程對象', max_length=5)
	order = models.IntegerField(db_column='順序')

	def __str__(self):
		return self.forwhom
	class Meta:
		managed = False
		db_table = '列表_課程對象'

class CourseList(models.Model):
	course_name = models.CharField(db_column='課程名稱', max_length=20)
	course_type = models.CharField(db_column='課程類型', max_length=5)
	course_grade = models.IntegerField(db_column='年級')

	def __str__(self):
		return self.course_name
	class Meta:
		managed = False
		db_table = '列表_課程名稱'

class PlaceList(models.Model):
	first_num = models.CharField(db_column='場地代號', max_length=2)
	second_num = models.CharField(db_column='場地編號', max_length=5)
	place = models.CharField(db_column='場地名稱', max_length=10)
	note = models.CharField(db_column='備註', max_length=50, blank=True, null=True)
	valid = models.IntegerField(db_column='valid')
	course = models.ManyToManyField(CourseList, through='CourseRelatedPlace', related_name='places')

	def __str__(self):
		return self.place

	class Meta:
		managed = False
		db_table = '列表_場地'


class OpenCourse(models.Model):
	course = models.ForeignKey(CourseList, db_column='課程', on_delete=models.CASCADE, related_name='open_course')
	place = models.ForeignKey(PlaceList, db_column='場地', on_delete=models.CASCADE, related_name='open_course')
	forwhom = models.ForeignKey(CourseFor, db_column='對象', on_delete=models.CASCADE)
	isEng = models.IntegerField(db_column='英授')
	week = models.IntegerField(db_column='星期')
	time = models.IntegerField(db_column='節次')
	user_id = models.ForeignKey(TeacherList, db_column='user_id', on_delete=models.CASCADE, related_name='open_course')

	def __str__(self):
		return self.course.course_name
	class Meta:
		managed = False
		db_table = '排課紀錄_開設課程'


class CourseNeedToOpen(models.Model):
	grade = models.CharField(db_column='年級', max_length=5)
	mon = models.IntegerField(db_column='Mon')  # Field name made lowercase.
	tue = models.IntegerField(db_column='Tue')  # Field name made lowercase.
	wed = models.IntegerField(db_column='Wed')  # Field name made lowercase.
	thu = models.IntegerField(db_column='Thu')  # Field name made lowercase.
	fri = models.IntegerField(db_column='Fri')  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = '排課紀錄_開課數量'


class CourseSetting (models.Model):
	content = models.CharField(max_length=50, db_column='設定內容')
	value = models.CharField(max_length=3, db_column='設定值')

	class Meta:
		managed = False
		db_table = '排課設定'


class Semester1CourseOfGrade1(models.Model):
	dep = models.CharField(max_length=10,db_column='系所')
	teacher = models.ForeignKey(TeacherList, db_column='教師', related_name='grade1_course', null=True, on_delete=models.SET_NULL)
	week = models.IntegerField(blank=True, null=True,db_column='星期')
	time = models.IntegerField(blank=True, null=True,db_column='節次')
	isEng = models.IntegerField(db_column='英授')

	def __str__(self):
		return self.dep

	class Meta:
		managed = False
		db_table = '列表_大一體育'

class CourseRelatedPlace(models.Model):
	course = models.ForeignKey(CourseList, db_column='課程')  # Field name made lowercase.
	place = models.ForeignKey(PlaceList, db_column='場地')  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = '列表_課程使用場地'