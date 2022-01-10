import json 
import datetime 
from math import inf 

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator

from .models import User, Follow, Post, Like 

from . forms import NewPostForm 

POSTS_PER_PAGE = 10 

def getPageObject (listPosts, request ):
    orderedPosts = listPosts.order_by('-datetime_created')
    paginator = Paginator(orderedPosts, POSTS_PER_PAGE)

    pageNumber = request.GET.get('page') or 1 
    pageObj = paginator.get_page(pageNumber)
    return pageObj

def index(request):
    '''
    Should return view for all posts. This is a get request.
    Should also accept POST requests for composing. 
    '''
    post_form = NewPostForm() 

    if request.method == "POST" and request.user.is_authenticated:
        post_form = NewPostForm(request.POST)
        if post_form.is_valid() :
            new_post = Post(user = request.user, text = post_form.cleaned_data['text'])
            new_post.save() 
            post_form = NewPostForm()

    listPosts = Post.objects.all()
    return render(request, "network/index.html", {'page_obj': getPageObject(listPosts, request) ,
    'post_form': post_form})

def testPosts(listPosts):
    return HttpResponse( [ post.serialize() for post in listPosts ])

def profile(request, user_id):
    '''
    GET request: 
    Should be able to see all the posts made by user_id. This should show the profile page of the user.
    This is a separate page from index page.  
    '''
    try:
        user = User.objects.get(pk = user_id)
    except User.DoesNotExist: 
        return render (request, 'network/profile.html', { 'message': 'User Does Not Exist'})

    listPosts = Post.objects.filter(user = user)
    return render(request, 'network/profile.html', { 'profile_user': user, 
        'page_obj' : getPageObject(listPosts, request)}) 

@login_required
def following(request):
    '''
    Should show all posts from the users that the logged in user follows. This is a separate page from
    the index page. 
    '''
    user = User.objects.get(pk = request.user.id )

    set_following = set() 
    for follow in user.following.all():
        set_following.add (follow.follows_user) 
    listPosts = Post.objects.filter(user__in = set_following )
    return render ( request, 'network/following.html', {'page_obj' :getPageObject(listPosts, request)})

@login_required
def follow (request,user_id):

    if request.method != "PUT" and request.method != "GET":
        return JsonResponse({"error": "Only GET and POST request methods allowed"} ,status = 400)

    if request.method == "PUT" and request.user.id == user_id:
        return JsonResponse({"error": "Cannot follow or unfollow oneself"} ,status = 400)
    try:
        otherUser = User.objects.get(pk= user_id)
    except User.DoesNotExist:
        JsonResponse({"error": "Invalid user ID"} ,status = 400)

    if request.method == "GET":
        try:
            Follow.objects.get(follower_user = request.user, follows_user = otherUser ) 
            return JsonResponse({'follows':True}, status = 201)
        except Follow.DoesNotExist:
            return JsonResponse({'follows':False}, status = 201)

    data = json.loads(request.body)
    follow = data.get('follow')

    if follow is None:
        return JsonResponse({"error": "Put request must have attribute of 'follow' "} ,status = 400)

    if follow:
        try:
            newFollow = Follow(follower_user = request.user, follows_user = otherUser)
            newFollow.save() 
        except:
            pass 
    else:
        try:
            existingFollow = Follow.objects.get(follower_user = request.user, follows_user = otherUser ) 
            existingFollow.delete() 
        except:
            pass 
    followers = otherUser.followers.count()
    following = otherUser.following.count()
    return JsonResponse({"followers":followers, "following":following}, status = 201)


@login_required
def post(request, post_id):
    ''' 
    Should only allow edits of the specified posts via POST requests or likes/unlikes via PUT requests. 
    Returns a JSON response indicating success or failure of post/put request. 

    Also should allow get requests to return the content of the post. 
    '''
    method = request.method 
    if method != "POST" and method != "PUT" and method != "GET":
        return JsonResponse({"error": "PUT or POST request required."}, status=400)

    try:
        post = Post.objects.get(id = post_id) 
    except Post.DoesNotExist:
        return JsonResponse({"error": "The post for this post id does not exist."}, status=400)

    user = request.user 

    if method == "GET":
        likes = len( post.likes.filter (user = user) ) > 0
        return JsonResponse({ 'text': post.text, 'user_likes': likes, 'likes': post.likes.count() } , status =201 )

    if method == "POST":
        if post.user.id != user.id :
            return JsonResponse({"error": "Access unauthorized- users may only edit their posts"}, status=400)
        data = json.loads(request.body)
        post_text = data.get('text').strip() 
        if len(post_text) > 0:
            post.text = post_text
            post.save()
            return JsonResponse({"message": "Post successfully edited" ,
            'text': post.text}, status = 201 )
        else:
            return JsonResponse({"error": "Edited post must have at least one non-whitespace character"}, status=400)

    if method == "PUT":
        data = json.loads(request.body)
        like = data.get('like')
        if like is None :
            return JsonResponse({"error": "The PUT request must have like attribute" }, status = 400)
        try: 
            current = Like.objects.get(user = user, post = post )       
        except Like.DoesNotExist:
            # if like does not exist, then we need to create a new like if like is true 
            if like:
                newLike = Like(user = user, post = post )
                newLike.save() 
                numberLikes = post.likes.count()
                return JsonResponse({"message": "Successfully liked post" ,
                "number_likes": numberLikes}, status = 201  )
            else: 
                return JsonResponse({"error": "Cannot unlike a post that you don't like" }, status = 400)
        # if the current like exist, then only delete if like is false 
        if not like:
            current.delete()
            numberLikes = post.likes.count() 
            return JsonResponse({"message": "Successfully unliked post",
            "number_likes": numberLikes }, status = 201  )
        else:
            return JsonResponse({"error": "Cannot like a post multiple times" }, status = 400)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
