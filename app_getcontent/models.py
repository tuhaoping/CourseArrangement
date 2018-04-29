from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class TeacherList(models.Model):
    userid = models.OneToOneField(User, db_column='id', on_delete=models.CASCADE, primary_key=True)
    title_teacher = models.CharField(db_column='教師職稱', max_length=10)
    title_peoffice = models.CharField(db_column='行政職稱', max_length=10, blank=True, null=True)

    def __str__(self):
        return self.userid.last_name + self.userid.first_name
    class Meta:
        managed = False
        db_table = '列表_教師'

class CourseFor(models.Model):
    forwhom = models.CharField(db_column='課程對象', max_length=5)

    def __str__(self):
        return self.forwhom
    class Meta:
        managed = False
        db_table = '列表_課程對象'

class CourseList(models.Model):
    course_name = models.CharField(db_column='課程名稱', max_length=20)
    course_type = models.CharField(db_column='課程類型', max_length=5)

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

    def __str__(self):
        return self.place

    class Meta:
        managed = False
        db_table = '列表_場地'


class OpenCourse(models.Model):
    course = models.ForeignKey(CourseList, db_column='課程', on_delete=models.CASCADE)
    place = models.ForeignKey(PlaceList, db_column='場地', on_delete=models.CASCADE)
    forwhom = models.ForeignKey(CourseFor, db_column='對象', on_delete=models.CASCADE)
    week = models.IntegerField(db_column='星期')
    time = models.IntegerField(db_column='節次')
    user_id = models.ForeignKey(TeacherList, db_column='user_id', on_delete=models.CASCADE)

    def __str__(self):
        return self.course.course_name + '/' 
    class Meta:
        managed = False
        db_table = '排課紀錄_開設課程'