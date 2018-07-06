from django.db import models

# Create your models here.

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

class CourseRelatedPlace(models.Model):
	course = models.ForeignKey(CourseList, db_column='課程')  # Field name made lowercase.
	place = models.ForeignKey(PlaceList, db_column='場地')  # Field name made lowercase.

	class Meta:
		managed = False
		db_table = '列表_課程使用場地'