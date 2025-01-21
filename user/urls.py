from django.urls import path
from . import views
urlpatterns = [
    path('register', views.user_registration_view, name='user_register'),
    path('login', views.user_login_view, name='user_login'),
    path('post', views.create_post, name='user_post'),
    path('get_user_posts', views.get_user_posts, name='get_user_posts'),
    path('profile', views.user_profile, name='user_profile'),
    path('profile/edit', views.edit_user_profile, name='edit_user_profile'),
    path('follow', views.follow_user, name='follow_user'),
    path('get_personal_followers', views.get_followers, name='get_personal_followers'),
    path('get_personal_followings', views.get_followings, name='get_personal_followings'),
    path('remove_follower', views.remove_follower, name='remove_follower'),
    path('remove_following', views.remove_following, name='remove_following'),
    path('get_posts', views.get_posts_by_followed_users, name='get_posts'),
    path('get_list_followers_following', views.get_followers_and_followings, name='get_list_followers_followings'),
    path('post/like', views.like_post, name='like_post'),
    path('post/comment', views.comment_on_post, name='comment_post'),
]
