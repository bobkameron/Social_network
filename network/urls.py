
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path('users/<int:user_id>', views.profile , name = 'profile'),
    path('users/<int:user_id>/follow', views.follow, name = 'follow'), 

    path('following', views.following, name = 'following'),
    path('posts/<int:post_id>', views.post, name = 'post')
]

'''
User should be able to see all posts in the default '' index url

User should be able to see the posts made by any particular user in users/user_id path 

User should be able to see all the posts made by people they are following in following path 

User should be able to add posts. This is done by a call to the compose function of posts. 

User should be able to edit or add likes to existing posts. This is done with a post or put request to 
posts/post_id 

'''