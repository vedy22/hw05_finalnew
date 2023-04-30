from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from yatube.settings import LIMIT_POSTS
from .forms import PostForm


# Главная страница
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
    posts = group.posts.all()
    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
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

    return render(request, 'posts/profile.html', context)


# Раскрыть пост полностью
def post_detail(request, post_id):

    post = get_object_or_404(Post, pk=post_id)

    context = {
        "post": post,
        "author": post.author,
        "posts_count": post.author.posts.count()
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

    if request.user == post.author:
        form = PostForm(instance=post, data=request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)

        context = {
            'form': form,
        }
        return render(request, 'posts/post_edit.html', context)

    return redirect('posts:post_detail', post_id=post_id)
