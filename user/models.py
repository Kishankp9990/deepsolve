from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.timezone import now

# To register user and save the timestamp to register.
class CustomUser(AbstractUser):
    created_at = models.DateTimeField(default=now)

# To maintain login history
class UserLoginHistory(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='login_history',
        to_field='username'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

# To make user post  
class UserPost(models.Model):
    caption = models.TextField()
    post_url = models.URLField()
    background_music_url = models.URLField(blank=True, null=True)  # Optional
    category = models.CharField(max_length=50, choices=[
        ('Tech', 'Tech'),
        ('Entertainment', 'Entertainment'),
        ('Business', 'Business'),
        ('Other', 'Other'),
    ])
    datetime_posted = models.DateTimeField(auto_now_add=True)
    publisher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        to_field='username'
    )
    is_public = models.BooleanField(default=True)  # Additional helpful attribute

# To create user profile  
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        to_field='username'
    )
    name = models.CharField(max_length=100)
    profile_pic = models.URLField(max_length=300, blank=True, null=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username

# To follow users
class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_set',
        to_field='username'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_set',
        to_field='username'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Prevent duplicate follow records

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

    
# to like a post
class LikePost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
        to_field='username'
    )
    post = models.ForeignKey(
        UserPost,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Ensure a user can like a post only once

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"

# to comment on a post
class CommentPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        to_field='username'
    )
    post = models.ForeignKey(
        UserPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.id}: {self.text}"


    

