from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, Follow
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from yatube.settings import LIMIT_POSTS, CACHE_TIMEOUT
from .forms import PostForm, CommentForm


# Главная страница
@cache_page(CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


# Страница с постами группы
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'posts': posts,
        'paginator': paginator,
    }
    return render(request, template, context)


# Все посты в профиле пользователя
def profile(request, username):

    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'author': author,
        "posts_count": author.posts.count()
    }

    if request.user.is_authenticated:
        following_exist = request.user.follower.filter(author=author).exists()
        context["following"] = following_exist

    return render(request, 'posts/profile.html', context)


# Раскрыть пост полностью
def post_detail(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    comments = post.comment.all()
    comment_form = CommentForm(request.POST or None)

    context = {
        "post": post,
        "author": post.author,
        "posts_count": post.author.posts.count(),
        'comment_form': comment_form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


# создать новый пост
@login_required
def post_create(request):

    user = request.user
    form = PostForm(request.POST or None)

    if form.is_valid():
        post = form.save(False)
        post.author = user
        post.save()
        return redirect("posts:profile", user.username)

    context = {
        "form": form,
    }

    return render(request, "posts/post_edit.html", context)


# Отредактировать пост
@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    context = {
        'post': post,
        'form': form,
        'post_id': post_id,
        'is_edit': True,
    }
    if request.user == post.author and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(f'/posts/{post.id}', id=post_id)
    return render(request, 'posts/post_edit.html', context)


# Удалить пост
@login_required
def delete_post(request, post_id):
    remove_post = Post.objects.filter(pk=post_id)
    remove_post.delete()

    return redirect('posts:index')


# Добавить комментарий
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


# Вывод постов, на которых подписан текущий пользователь
@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user)
    paginator = Paginator(posts, settings.LIMIT_POSTS)
    page_number = request.GET.get('page_obj')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
    }
    return render(request, 'posts/follow.html', context)


# Добавить подписку на автора
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


# Удалить подписку на автора
@login_required
def profile_unfollow(request, username):
    user_follower = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    user_follower.delete()
    return redirect('posts:profile', username)
