import random
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def random_color():
    color_style = random.choice(["red","blue","orange","redorange","redgreen","bluewhite","bluegreen","pinkyellow","purple"])
    return color_style