import os
import random
from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def random_rp_image(image_dir):

    if image_dir:
        rel_dir = image_dir
    else:
        rel_dir = 'images/portfolio-1'
    rand_dir = os.path.join(settings.STATIC_ROOT, rel_dir)
    path = os.path.join('/static_files/', rel_dir, random.choice(os.listdir(rand_dir)))
    return path