from django import template

register = template.Library()


@register.filter()
def is_manager(user):
    print(user)
    return user.groups.filter(name__in=['manager']).exists()
