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

from timeit import default_timer as timer 

from .models import User, Follow, Post, Like 
from . forms import NewPostForm 

from .cache import * 
cache = Cache(CACHE_ALIAS)

POSTS_PER_PAGE = 10 

def getPageNumber (request):
    # assumes request is an HTTP GET request
    return request.GET.get('page') or 1

def getPageObject (listPosts, request ):
    orderedPosts = listPosts.order_by('-datetime_created')
    paginator = Paginator(orderedPosts, POSTS_PER_PAGE)

    pageNumber = getPageNumber(request)
    pageObj = paginator.get_page(pageNumber)
    return pageObj

def testPosts(listPosts):
    return HttpResponse( [ post.serialize() for post in listPosts ])

def printTimer(start,end, page, cached = True ):
    result = "Time to load page " + page + " that: " + str(cached) + " was cached was " + str(end-start)
    print (result)
    
def index(request):
    '''
    Should return view for all posts. This is a get request.
    Should also accept POST requests for composing. 
    '''
    if request.method == "POST" and request.user.is_authenticated:
        post_form = NewPostForm(request.POST)
        if post_form.is_valid() :
            new_post = Post(user = request.user, text = post_form.cleaned_data['text'])
            new_post.save() 
            # clear the whole cache if there is a new post 
            cache.clear()

    start = timer() 

    pageNumber = getPageNumber(request)

    if request.user.is_authenticated:
        cacheResult = cache.get(INDEX, pageNumber, request.user.id)
    else:
        cacheResult = cache.get(INDEX, pageNumber)
    if cacheResult is not None:
        end = timer()
        printTimer(start,end, INDEX, True )
        return cacheResult 

    post_form = NewPostForm()
    listPosts = Post.objects.all()
    result =  render(request, "network/index.html", {'page_obj': getPageObject(listPosts, request) ,
    'post_form': post_form})

    if request.user.is_authenticated:
        cache.add(result,INDEX,pageNumber,request.user.id)
    else:
        cache.add(result,INDEX,pageNumber)

    end = timer() 
    printTimer(start,end,INDEX,False)

    return result


def profile(request, user_id):
    '''
    GET request: 
    Should be able to see all the posts made by user_id. This should show the profile page of the user.
    This is a separate page from index page.  
    '''
    page_number = getPageNumber(request)
    if request.user.is_authenticated:
        cache_result = cache.get(PROFILE,page_number, request.user.id, user_id)
    else:
        cache_result = cache.get(PROFILE, page_number, user_id)
    
    if cache_result is not None:
        return cache_result 

    try:
        user = User.objects.get(pk = user_id)
        listPosts = Post.objects.filter(user = user)
        result =  render(request, 'network/profile.html', { 'profile_user': user, 
            'page_obj' : getPageObject(listPosts, request)}) 
    except User.DoesNotExist: 
        result = render (request, 'network/profile.html', { 'message': 'User Does Not Exist'})

    if request.user.is_authenticated:
        cache.add(result,PROFILE,page_number, request.user.id, user_id)
    else:
        cache.add(result,PROFILE,page_number, user_id)

    return result


@login_required
def following(request):
    '''
    Should show all posts from the users that the logged in user follows. This is a separate page from
    the index page. 
    '''
    page_number = getPageNumber(request)
    cache_result = cache.get(FOLLOWING,page_number, request.user.id)
    if cache_result is not None:
        return cache_result 

    user = User.objects.get(pk = request.user.id )

    set_following = set() 
    for follow in user.following.all():
        set_following.add (follow.follows_user) 
    listPosts = Post.objects.filter(user__in = set_following )
    result= render ( request, 'network/following.html', {'page_obj' :getPageObject(listPosts, request)})

    cache.add(result, PROFILE,page_number,request.user.id)
    return result 

def user (request,user_id):

    if request.method != "PUT" and request.method != "GET" and request.method != "DELETE":
        return JsonResponse({"error": "Wrong request method"} ,status = 400)

    if request.method == "PUT" or request.method == 'DELETE':
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Cannot (un)follow a user without being a logged in"} ,status = 401)
        elif request.user.id == user_id:
            return JsonResponse({"error": "Cannot follow or unfollow oneself"} ,status = 400)
    
    try:
        otherUser = User.objects.get(pk= user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid user ID requested"} ,status = 404)

    if request.method == "GET":
        followers = otherUser.followers.count()
        following = otherUser.following.count()
        response = False   
        if request.user.is_authenticated:
            try:
                Follow.objects.get(follower_user = request.user, follows_user = otherUser)
                response = True 
            except: 
                response = False 
        return JsonResponse({'user_follows':response, 'number_followers': followers, 
        'number_following':following}, status = 200)

    if request.method == "PUT":
        try:
            newFollow = Follow(follower_user = request.user, follows_user = otherUser)
            newFollow.save() 
            cache.clear()
            return JsonResponse({"status": "Successfully followed user"}, status = 201)
        except:
            return JsonResponse({"error": "Cannot follow someone you already follow" }, status = 400)

    elif request.method == "DELETE":
        try:
            existingFollow = Follow.objects.get(follower_user = request.user, follows_user = otherUser ) 
            existingFollow.delete()
            cache.clear() 
            return JsonResponse({"status": "Successfully unfollowed user"}, status = 204)
        except:
            return JsonResponse({"error": "Cannot unfollow someone you don't follow" }, status = 400)

def post(request, post_id):
    ''' 
    Should only allow edits of the specified posts via POST requests or likes/unlikes via PUT requests. 
    Returns a JSON response indicating success or failure of post/put request. 

    Also should allow get requests to return the content of the post. 
    '''
    method = request.method 
    if method != "PUT" and method != "GET":
        return JsonResponse({"error": "Wrong request method."}, status=400)

    try:
        postObject = Post.objects.get(id = post_id) 
    except Post.DoesNotExist:
        return JsonResponse({"error": "The post for this post id does not exist."}, status=404)

    user = request.user 

    if method == "GET":
        likes = None 
        if user.is_authenticated:
            likes = len( postObject.likes.filter (user = user) ) > 0
        print(likes)
        return JsonResponse({ 'text': postObject.text, 'user_likes': likes, 
        'number_likes': postObject.likes.count() } , status =201 )

    if method == "PUT":
        if not user.is_authenticated:
            return JsonResponse({"error": "Cannot edit post without being a logged in"} ,status = 401)

        if postObject.user.id != user.id :
            return JsonResponse({"error": "Access unauthorized- users may only edit their posts"}, status=401)
        data = json.loads(request.body)
        post_text = data.get('text').strip() 
        if len(post_text) > 0:
            postObject.text = post_text
            postObject.save()
            return JsonResponse({"message": "Post successfully edited"}, status = 201 )
        else:
            return JsonResponse({"error": "Edited post must have at least one non-whitespace character"}, status=400)

@login_required 
def like_post(request, post_id):
    method = request.method

    try:
        postObject = Post.objects.get(id = post_id) 
    except Post.DoesNotExist:
        return JsonResponse({"error": "The post for this post id does not exist."}, status=404)

    user = request.user 

    if method == "PUT":
        try:
            Like.objects.get(user = user, post = postObject)
            return JsonResponse({"error": "Cannot like a post multiple times" }, status = 400)
        except:
            newLike = Like(user = user, post = postObject )
            newLike.save() 
            return JsonResponse({"message": "Successfully liked post" } ,status = 201   )
    
    elif method == 'DELETE':
        try:
            currentLike = Like.objects.get(user = user, post = postObject)
            currentLike.delete() 
            return JsonResponse({"message": "Successfully unliked post"}, status = 201  ) 
        except:
            return JsonResponse({"error": "Cannot unlike a post you don't like" }, status = 401)
    else:
        return JsonResponse({'error': "Wrong request method type" }, status = 400)

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
            cache_login_failure = cache.get ( LOGIN, 'failure')
            if cache_login_failure is not None: return cache_login_failure

            result =  render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
            cache.add(result,LOGIN,'failure')
    else:
        cache_result = cache.get(LOGIN)
        if cache_result is not None: return cache_result 

        result =  render(request, "network/login.html")
        cache.add(result, LOGIN)
    
    return result 

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
            cache_passwords_noMatch = cache.get(REGISTER,'passwordsNoMatch')
            if cache_passwords_noMatch is not None:
                return cache_passwords_noMatch
            result =  render(request, "network/register.html", {
                "message": "Passwords must match."
            })
            cache.add(result,REGISTER, 'passwordsNoMatch')
            return result 

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            cache.clear() 

        except IntegrityError:
            cache_username_taken = cache.get(REGISTER, 'username_taken')
            if cache_username_taken is not None: return cache_username_taken
            result =  render(request, "network/register.html", {
                "message": "Username already taken."
            })
            cache.add(result,REGISTER,'username_taken')
            return result 

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        cache_result = cache.get(REGISTER)
        if cache_result is not None: return cache_result
        result =  render(request, "network/register.html")
        
        cache.add(result,REGISTER)
        return result 