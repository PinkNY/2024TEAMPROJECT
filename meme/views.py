# main/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.files.storage import FileSystemStorage

def home(request):
    return render(request, 'meme/home.html')

# 회원가입
def signup_view(request):
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['confirm_password']

        # 유효성 검사
        if password != password_confirm :
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect('signup')
        
        if len(username) < 6 :
            messages.error(request, '아이디는 6자 이상이여야 합니다.')
            return redirect('signup')
        
        if len(password) < 8 :
            messages.error(request, '비밀번호는 8자 이상이여야 합니다.')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists() :
            messages.error(request, '이미 존재하는 아이디입니다.')
            return redirect('signup')
        
        # 사용자 생성
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    else :
        return render(request, 'meme/signup.html')
    
# 로그인
def login_view(request):
    if request.method == 'POST' :
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None :
            login(request, user)
            return redirect('home')
        else :
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
            return redirect('login')
    else :
        return render(request, 'meme/login.html')

# 로그아웃
def logout_view(request) :
    logout(request)
    return redirect('home')

def upload_view(request):
    return render(request, 'meme/upload.html')

@login_required
def board_view(request):
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'meme/board.html', {'page_obj' : page_obj})

@login_required
def search_board(request) :
    query = request.GET.get('query', '')
    posts_list = Post.objects.filter(title__icontains=query)
    paginator = Paginator(posts_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'meme/board.html', {'page_obj':page_obj})

@login_required
def create_post(request):
    if request.method == 'POST' :
        title = request.POST['title']
        content = request.POST['content']
        author = request.user

        Post.objects.create(title=title, content=content, author=author)
        messages.success(request, '글이 성공적으로 작성되었습니다.')
        return redirect('board')
    else :
        return render(request, 'meme/create_post.html')
    
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST' :
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else :
        comment_form = CommentForm()
    return render(request, 'meme/post_detail.html', {'post':post, 'comment_form':comment_form})

@login_required
def post_delete(request, post_id) :
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author :
        return HttpResponseForbidden("해당 권한이 없는 아이디입니다.")
    if request.method == 'POST' :
        post.delete()
        return redirect('board')
    return render(request, 'meme/post_confirm_delete.html', {'post':post})

@login_required
def post_edit(request, post_id) :
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author :
        return HttpResponseForbidden("해당 권한이 없습니다.")
    if request.method == 'POST' :
        form = PostForm(request.POST, instance=post)
        if form.is_valid() :
            form.save()
            return redirect('post_detail', post_id=post.id)
    else :
        form = PostForm(instance=post)
    return render(request, 'meme/post_edit.html', {'form':form, 'post':post})