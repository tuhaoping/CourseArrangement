from django.shortcuts import render
from django.http import HttpResponse
from app_getcontent.models import OpenCourse, Semester1CourseOfGrade1, Semester1CourseOfGrade1, CourseSetting, TeacherList, PlaceList

import pandas as pd
import numpy as np
import datetime
from urllib.parse import quote

def download_main_excel(request):
	now = datetime.datetime.now()
	# print(now.year,now.month)
	if 3<=now.month<=8:
		title = "{} 學年度第1學期 體育課程配當表".format(now.year-1911)
		sheet = "{}-1".format(now.year-1911)
	elif now.month in [1,2]:
		title = "{} 學年度第2學期 體育課程配當表".format(now.year-1912)
		sheet = "{}-2".format(now.year-1912)
	else:
		title = "{} 學年度第2學期 體育課程配當表".format(now.year-1911)
		sheet = "{}-2".format(now.year-1911)



	teachers = TeacherList.objects.all().order_by('-isdirector', 'title_order')
	response = HttpResponse(content_type='application/application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
	response['Content-Disposition'] = 'attachment; filename="{}{} ({}.{}.{}).xlsx"'.format(sheet, quote('配當表'), now.year, now.month, now.day)
	writer = pd.ExcelWriter(response, engine='xlsxwriter')
	# return response
	headers = ['職稱', '姓名 \\ 節次', *['一二', '三四', '五六', '七八', '九十']*5]
	# sheet = '107-1'
	pd.DataFrame().to_excel(writer, sheet)
	df = pd.DataFrame(np.full((teachers.count(), 27), np.nan))
	# print(type(writer))
	workbook = writer.book
	worksheet = writer.sheets[sheet]
	worksheet.conditional_format(
		'A1:AA{}'.format(teachers.count()+3), 
		{
			'type':'no_errors',
			# 'criteria':'>=',
			# 'value':0,
			'format': workbook.add_format({'border':1})
		}
	)

	week_header_format = workbook.add_format({'fg_color':'#99CCFF','align':'center', 'valign':'vcenter'})
	
	format1 = workbook.add_format({'align':'center', 'valign':'vcenter'})
	worksheet.merge_range('A1:AA1',title, workbook.add_format({'font_size':16, 'align':'center', 'valign':'vcenter'}))
	worksheet.write(1,1,'星期',format1)
	worksheet.merge_range(1,0,2,0, '職稱', format1)
	for i,week in enumerate(['一', '二', '三', '四', '五']):
		worksheet.merge_range(1,i*5+2,1,i*5+6, '星期'+week, week_header_format)



	worksheet.set_zoom(80)
	cell_format = workbook.add_format({'text_wrap':True,'align':'center', 'valign':'vcenter'})
	worksheet.set_column('A:B', 15, cell_format)
	worksheet.set_column('C:AA', 9, cell_format)
	worksheet.set_column('AC:AC', 30, cell_format)
	
	for row in range(teachers.count()+3):
		height = 20 if row in [1,2] else 50
		worksheet.set_row(row,height)
	# courses = OpenCourse.objects.all()
	

	row = 0
	for teacher in teachers:
		if teacher.isdirector:
			df.iloc[row, 0] = teacher.title_teacher + "\n兼主任"
		else:
			df.iloc[row, 0] = teacher.title_teacher
		
		df.iloc[row, 1] = teacher.userid.last_name + teacher.userid.first_name

		for course in teacher.open_course.all():
			week = course.week
			time = course.time
			df.iloc[row,(week-1)*5+time+1] = course.forwhom.forwhom + "\n" + course.course.course_type + "\n" + course.place.first_num

		row += 1

	# print(CourseSetting.objects.get(pk=1))
	if CourseSetting.objects.get(pk=1).value == '1':
		grade1_courses = Semester1CourseOfGrade1.objects.exclude(teacher__isnull=True)
		for course in grade1_courses:
			teacher_full_name = course.teacher.userid.last_name + course.teacher.userid.first_name
			week = course.week
			time = course.time
			# print(df.ix[df[1]==teacher_full_name,:])
			# print(df[0])
			df.ix[df[1]==teacher_full_name, (week-1)*5+time+1] = "大一\n"+course.dep
			# print(df.ix[df[1]==teacher_full_name, (week-1)*5+time+1])


	df.to_excel(writer, sheet, startrow=2, index=False, header=headers)

	place_list = []
	for place in PlaceList.objects.all():
		place_list.append("{}. {}".format(place.first_num, place.place))
	
	worksheet.merge_range(4, 28, 14, 28, "\n".join(place_list), workbook.add_format({'valign':'top', 'align':'left', 'text_wrap':True}))

	writer.save()

	return response