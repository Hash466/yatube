from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post
from yatube.settings import COUNT_POSTS  # type: ignore

User = get_user_model()


def get_paginator_page(request, objects):
    paginator = Paginator(objects, COUNT_POSTS)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return page


def index(request):
    posts = Post.objects.all()
    page = get_paginator_page(request, posts)
    return render(request, "posts/index.html", {"page": page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page = get_paginator_page(request, posts)
    return render(request, "posts/group.html",
                  {"group": group, "page": page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        n_post = form.save(commit=False)
        n_post.author = request.user
        n_post.save()
        return redirect("index")

    return render(request, "posts/new_post.html", {"form": form,
                                                   "edit": False})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page = get_paginator_page(request, posts)

    following = False
    if request.user.is_authenticated and request.user.username != username:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()

    return render(
        request, "posts/profile.html",
        {
            "page": page,
            "author": author,
            "following": following,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request, "posts/post.html",
        {
            "author": post.author,
            "post": post,
            "comments": comments,
            "form": form
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect("post", username, post_id)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username, post_id)

    return render(
        request, "posts/new_post.html",
        {
            "form": form,
            "edit": True,
            "post": post
        }
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = post.author
        new_comment.post = post
        new_comment.save()
        return redirect("post", username, post_id)

    return render(request, "posts/comments.html", {"form": form})


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    page = get_paginator_page(request, posts)
    return render(request, "posts/follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = get_object_or_404(Follow, user=request.user, author=author)
    following.delete()
    return redirect("profile", username=username)
