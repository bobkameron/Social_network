from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Follow(models.Model):
    follower_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'following')
    follows_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'followers')
    class Meta:
        unique_together = ('follower_user', 'follows_user')
        constraints = [models.CheckConstraint(check=~models.Q(follower_user =models.F('follows_user')), name='not_follow_self') ]

class Post(models.Model):
    datetime_created = models.DateTimeField( auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "posts")

    text = models.TextField()

    def serialize(self):
        return {'datetime_created':self.datetime_created, 'user' : self.user.username , 'text': self.text}


class Like ( models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "likes")
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name = 'likes')
    class Meta:
        unique_together = ('user','post')
        
        