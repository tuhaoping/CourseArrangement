from django.conf.urls import url
from django.contrib import admin
from .views import homePage
from django.contrib.auth.views import login, logout
import app_admin.views as app_admin
import app_getcontent.views as app_getcontent
import app_download.views as app_download

admin.autodiscover()

urlpatterns = [
    url(r'django_admin',admin.site.urls),
    
    url(r'admin/accounts/login/$', app_admin.login),
    url(r'admin/accounts/logout/$', app_admin.logout),
    
    url(r'accounts/login/$', login),
    url(r'accounts/logout/$', logout),

    
    url(r'^home/$', homePage),



    url(r'^admin/$', app_admin.admin_main),
    url(r'^admin/arrange/teachers', app_admin.admin_arrange_teachers),
    url(r'^admin/teachercourse$', app_admin.admin_arrange_teachers_table),
    url(r'^admin/arrange/places/$', app_admin.admin_arrange_places),
    url(r'^admin/placeuse$', app_admin.admin_place_use),

    url(r'^admin/data/teachers/$', app_admin.admin_data_teachers),
    url(r'^admin/data/teachers/(add|remove|modify)/$', app_admin.admin_data_teachers),
    url(r'^admin/data/places/$', app_admin.admin_data_places),
    url(r'^admin/data/places/(add|remove|modify)/$', app_admin.admin_data_places),
    url(r'^admin/data/courses/$', app_admin.admin_data_courses),
    url(r'^admin/data/courses/(add|remove|modify)/$', app_admin.admin_data_courses),
    url(r'^admin/courses_place/$', app_admin.admin_courses_place),
    url(r'^admin/coursesetting/$', app_admin.admin_coursesetting),
    url(r'^admin/coursesetting/(update)/$', app_admin.admin_coursesetting),
    url(r'^admin/changeperm/$', app_admin.admin_change_permission),
    url(r'^admin/changesetting/$', app_admin.admin_change_setting),
    url(r'^admin/mail/$', app_admin.admin_mail),
    

    url(r'^content/arrange_table/$', app_getcontent.get_arrange_table),
    url(r'^content/available_place/$', app_getcontent.get_available_place),
    url(r'^content/grade_course/$', app_getcontent.get_course_with_grade),
    url(r'^content/course_place/$', app_getcontent.get_course_place),
    url(r'^mycourse/$', app_getcontent.get_mycourse),
    url(r'^mycourse/grade1/$', app_getcontent.get_grade1_course),
    url(r'^mycourse/grade1/update/$', app_getcontent.update_grade1_course),
    url(r'^mycourse/grade1/delete/$', app_getcontent.del_grade1_course),
    url(r'^arrangedone/$', app_getcontent.arrange_done),
    url(r'^confirm/$', app_getcontent.confirm),
 
    url(r'^course/info/', app_getcontent.get_course_info),
    url(r'^test/', app_getcontent.create_new_course),
    url(r'^course/update', app_getcontent.modify_open_course),
    url(r'^course/delete', app_getcontent.delete_open_course),

    url(r'download/$', app_download.download_main_excel)

]
