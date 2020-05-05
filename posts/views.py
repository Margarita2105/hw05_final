from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) 
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "index.html", {"page": page, "paginator": paginator, "profile": profile})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post, 12)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect("index")
    return render(request, "new.html", {"form": form, "text_head": "Добавить запись", "text_button": "Добавить"})


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    profile = Post.objects.filter(author=post_author).order_by("-pub_date").all()
    paginator = Paginator(profile, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(author=post_author, user=request.user).count()   
    else:
        following = 0
    count = profile.count()
    follow_count = Follow.objects.filter(user=post_author).count()
    f_count = Follow.objects.filter(author=post_author).count()
    return render(request,"profile.html", {"post_author": post_author, "paginator": paginator,"page": page, "count": count, "follow_count" : follow_count, "following" : following, "f_count" : f_count}) 


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, pk=post_id)
    count = Post.objects.filter(author=author).count()
    com = Comment.objects.filter(post=post)
    form = CommentForm()
    return render(request, "post.html", {"author" : author, "post": post, "count": count, "com" : com, "form" : form})


@login_required
def post_edit(request, username, post_id):
    post_author = get_object_or_404(User, username=username)
    id_post = get_object_or_404(Post, id=post_id, author=post_author)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=id_post)
    if request.user != post_author:
        return redirect(post_view, username, post_id)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(post_view, username, post_id)
    return render(request, "new.html", {"form": form, "id_post": id_post, "text_head": "Изменить запись", "text_button": "Сохранить"})

    
def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post_author = get_object_or_404(User, username=username) 
    post = get_object_or_404(Post, author=post_author, id=post_id) 
    form = CommentForm(request.POST)
    if request.method == "POST": 
        if form.is_valid(): 
            text = form.cleaned_data["text"] 
            author = request.user 
            Comment.objects.create(text=text, post=post, author=author) 
            return redirect(post_view, username, post_id) 
    return render(request, "comments.html", {"form": form, "post": post}) 
     
    
@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user).values_list("author_id", flat=True)
    count = Follow.objects.filter(user=request.user).count()
    post_list = Post.objects.filter(author_id__in=follow).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page, "paginator": paginator, "count": count})

  
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    if not follow.exists() and author != request.user:
        Follow.objects.create(user=request.user, author=author)
    return redirect(follow_index)


@login_required
def profile_unfollow(request, username):
    post_author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=post_author).delete()
    return redirect(profile, username)
