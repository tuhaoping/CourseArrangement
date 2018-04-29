from django.template.defaulttags import register

@register.filter
def course_time(w):
    time_list = ['一二', '三四', '五六', '七八', '九十']
    return time_list[w-1]
