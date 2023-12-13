from django import template
from random import randint
# from chatbot.models import  
from django.utils import timezone
import math

from django.contrib.auth import get_user_model

register = template.Library()


User = get_user_model()

@register.simple_tag
def random_number():
    return randint(0, 999)


@register.simple_tag
def gold():
    return "Gold"

@register.simple_tag
def current_user(request):
    return request.user





@register.simple_tag
def time_ago(created_at):
    now = timezone.now()

    diff = now - created_at

    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        seconds = diff.seconds

        if seconds == 1:
            return str(seconds) + " second ago"

        else:
            return str(seconds) + " seconds ago"

    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        minutes = math.floor(diff.seconds/60)

        if minutes == 1:
            return str(minutes) + " minute ago"

        else:
            return str(minutes) + " minutes ago"

    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        hours = math.floor(diff.seconds/3600)

        if hours == 1:
            return str(hours) + " hour ago"

        else:
            return str(hours) + " hours ago"

    # 1 day to 30 days
    if diff.days >= 1 and diff.days < 30:
        days = diff.days

        if days == 1:
            return str(days) + " day ago"

        else:
            return str(days) + " days ago"

    if diff.days >= 30 and diff.days < 365:
        months = math.floor(diff.days/30)

        if months == 1:
            return str(months) + " month ago"

        else:
            return str(months) + " months ago"

    if diff.days >= 365:
        years = math.floor(diff.days/365)

        if years == 1:
            return str(years) + " year ago"

        else:
            return str(years) + " years ago"


