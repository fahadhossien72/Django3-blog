from atexit import register
from turtle import RawTurtle
from django import template
from ..models  import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.simple_tag
def total_post():
    return Post.objects.count()

@register.inclusion_tag('blog/latest_posts.html')
def show_latest_post(count=5):
    latest_post = Post.objects.order_by('-publish')[:count]
    return {'latest_post':latest_post}

@register.simple_tag
def most_commented_post(count=5):
    return Post.objects.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))