from typing import Any, Dict, Optional, Union

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def get_page_obj(post_list: QuerySet, page_number: Optional[str]) -> Page:
    """Возвращает объект класса Page для пагинации"""
    paginator: Paginator = Paginator(post_list, settings.LIMIT_OF_RECORDS)
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    """Обработчик для главной страницы приложения"""
    post_list: QuerySet = Post.objects.select_related(
        'author',
        'group',
    )
    page_obj: Page = get_page_obj(
        post_list,
        request.GET.get('page'),
    )

    context: Dict[str, Union[str, Any]] = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте',
        'index': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """Обработчик для страницы постов определенной группы"""
    group: Group = get_object_or_404(Group, slug=slug)

    post_list: QuerySet = group.posts.select_related(
        'author',
    )
    page_obj: Page = get_page_obj(
        post_list,
        request.GET.get('page'),
    )

    context: Dict[str, Any] = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Возвращает страницу с профайлом пользователя"""
    author = get_object_or_404(User, username=username)

    post_list: QuerySet = author.posts.select_related(
        'group',
    )
    page_obj: Page = get_page_obj(
        post_list,
        request.GET.get('page'),
    )

    if request.user.is_authenticated:
        following: bool = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following: bool = False

    context: Dict[str, Any] = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Возвращает страницу с информацией о публикации"""
    post: Post = get_object_or_404(Post.objects.select_related(
        'author',
        'group',
    ), pk=post_id)

    context: Dict[str, Any] = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Возвращает страницу для создания публикации"""
    form: PostForm = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        new_post: Post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Возвращает страницу для редактирования публикации"""
    post_for_edit: Post = get_object_or_404(Post.objects.select_related(
        'author',
        'group'
    ), pk=post_id)

    if post_for_edit.author != request.user:
        return redirect('posts:post_detail', post_id)

    form_for_edit: PostForm = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_for_edit,
    )

    if form_for_edit.is_valid():
        form_for_edit.save()
        return redirect('posts:post_detail', post_id)

    return render(
        request,
        'posts/create_post.html',
        {'form': form_for_edit, 'is_edit': True},
    )


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Функция для обработки отправленного комментария"""
    post: Post = get_object_or_404(Post, pk=post_id)
    form: CommentForm = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):

    authors: list[Optional[User]] = [
        follow.author for follow in request.user.follower.all()
    ]

    post_list: QuerySet = Post.objects.select_related(
        'author',
        'group',
    ).filter(author__in=authors)

    page_obj: Page = get_page_obj(
        post_list,
        request.GET.get('page'),
    )

    context: Dict[str, Union[str, Any]] = {
        'page_obj': page_obj,
        'index': True,
        'follow': True,
    }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    author: User = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    author: User = get_object_or_404(User, username=username)

    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()

    return redirect('posts:follow_index')
