from django.template.defaulttags import register

@register.filter
def check_perm(t):
    return t.userid.has_perm('app_getcontent.add_opencourse')

@register.filter
def places(course):
    course_place = course.places.filter(valid=True).values_list('place', flat=True)
    return "、".join(course_place)