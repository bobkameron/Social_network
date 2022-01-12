
from django.urls import path

from . import views

urlpatterns = [
    # returns all posts with GET request. Also accepts POST requests for composing new posts. 
    path("", views.index, name="index"),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    
    # returns view of all posts made by people logged in user is following 
    path('following', views.following, name = 'following'),
    
    # returns view of all posts made by the user 
    path('users/<int:user_id>', views.profile , name = 'profile'),

    # responds with JSON object for PUT/DELETE request (returns success or failure of follow/unfollow). 
    path('users/<int:user_id>/follow', views.user, name = 'follow'), 

    # responds with JSON object for GET request returning user info including username,
    # number of posts, number of followers, number following.
    # if user is logged in also returns if user follows the requested user. 
    path('users/<int:user_id>/info', views.user, name = 'user_info'), 

    # allows PUT json request which allows logged in user to modify the post if they own it.
    # also allows GET request which simply returns the content of the post, number of likes,
    # and if user is logged in whether user likes the post. 
    path('posts/<int:post_id>', views.post, name = 'post'),

    # allows logged in user to like/unlike the post with PUT/DELETE request. Returns json object
    # true/false depending on if the request was successful or not. 
    path('posts/<int:post_id>/like' , views.like_post, name = 'like'),
]

'''
User should be able to see all posts in the default '' index url

User should be able to see the posts made by any particular user in users/user_id path 

User should be able to see all the posts made by people they are following in following path 

User should be able to add posts. This is done by a call to the compose function of posts. 

User should be able to edit or add likes to existing posts. This is done with a post or put request to 
posts/post_id 

'''