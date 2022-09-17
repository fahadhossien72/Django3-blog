import mailbox
from multiprocessing import context
from re import I
from turtle import title
from unittest import result
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from . forms import *
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.db.models import Q

def post_list(request, tag_slug=None):
    posts = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    paginator = Paginator(posts, 2) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    context = {'posts':posts, 'tag':tag}
    return render(request,'blog/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,  slug=post, publish__year=year, publish__month=month, publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    comment_form = CommentForm()
    comment = None
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
             # Create Comment object but don't save to database yet
             comment = comment_form.save(commit=False)
             # Assign the current post to the comment
             comment.post = post
             comment.save()
        else:
            comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

    context = {'post':post, 'comments':comments, 'comment':comment, 'comment_form':comment_form, 'similar_posts':similar_posts}
    return render(request,'blog/detail.html', context)


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    form = EmailPostForm()
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'fahadhossien72@gmail.com',
                      [cd['to']])
            sent = True
        else:
            form = EmailPostForm()

    context = {'post':post, 'sent':sent, 'form':form}
    return render(request, 'blog/share.html', context)

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.distinct().filter(
                Q(title__icontains=query)|
                Q(body__icontains=query)
            )
    context = {'form':form, 'query':query, 'results':results}
    return render(request, 'blog/search.html', context )

