from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import UserRegistrationSerializer, UserLoginSerializer, PostSerializer, UserProfileSerializer, FollowSerializer, LikeSerializer, CommentSerializer
from rest_framework.authtoken.models import Token
from .models import UserLoginHistory, UserProfile, UserPost, Follow, LikePost, CommentPost
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model


User = get_user_model()
# to register user
@api_view(['POST'])
def user_registration_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "message": "User registration successful. Please explore our app to engage with communities",
            "registration_time": user.created_at, 
            "token": token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to login user
@api_view(['POST'])
def user_login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        if user:
            # Log the login timestamp
            UserLoginHistory.objects.create(user=user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful. See what is going on with your family and friends.",
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response({"error": "Username Or Password is incorrect."}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to create post by logged in user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        # Attach the authenticated user as the publisher
        serializer.save(publisher=request.user)
        return Response({
            "message": "Post created successfully",
            "post": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to get posts of logged in users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    user = request.user
    # Filter posts by the logged-in user
    user_posts = UserPost.objects.filter(publisher=user)
    serializer = PostSerializer(user_posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# to create profile for his/her account and to get profile of any other user account by any logged in user
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        # Check if the logged-in user already has a profile
        if hasattr(user, 'profile'):
            return Response({"error": "You can not create profile more than once!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        # Check if a username query parameter is provided
        username = request.query_params.get('username')
        if username:
            try:
                # Fetch the profile of the user with the given username
                profile = UserProfile.objects.get(user__username=username)
                serializer = UserProfileSerializer(profile)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except UserProfile.DoesNotExist:
                return Response({"error": "Profile not found!"}, status=status.HTTP_404_NOT_FOUND)

        # If no username is provided, return the logged-in user's profile
        try:
            profile = user.profile
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "Your profile does not exist!"}, status=status.HTTP_404_NOT_FOUND)

#to edit profile by logged in user
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_user_profile(request):
    user = request.user
    try:
        # Retrieve the user's existing profile
        profile = user.profile
    except UserProfile.DoesNotExist:
        return Response({"error": "Profile does not exist!"}, status=status.HTTP_404_NOT_FOUND)

    # Use the serializer to validate and update the profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# to follow any user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request):
    user = request.user
    data = request.data
    try:
        following_user = User.objects.get(username=data.get('username'))  # Username of the user to follow
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if user == following_user:
        return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the follow relationship
    follow, created = Follow.objects.get_or_create(follower=user, following=following_user)

    if created:
        serializer = FollowSerializer(follow)
        return Response({"message": "Successfully followed the user.", "data": serializer.data}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)
  
#get the list of followers of logged in users  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followers(request):
    user = request.user
    # Query to get all users following the logged-in user
    followers = Follow.objects.filter(following=user)
    # Serialize the data
    data = [
        {
            "follower_username": follow.follower.username,
            "created_at": follow.created_at
        }
        for follow in followers
    ]
    return Response(data, status=status.HTTP_200_OK)

#get the list of following of logged in user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followings(request):
    user = request.user
    # Query to get all users the logged-in user is following
    followings = Follow.objects.filter(follower=user)
    # Serialize the data
    data = [
        {
            "following_username": follow.following.username,
            "created_at": follow.created_at
        }
        for follow in followings
    ]
    return Response(data, status=status.HTTP_200_OK)

#to unfollow other by any logged in user
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_follower(request):
    user = request.user
    data = request.data
    try:
        follower = User.objects.get(username=data.get('username'))  # Username of the follower to remove
    except User.DoesNotExist:
        return Response({"error": "Follower not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the logged-in user is the one being followed
    try:
        follow = Follow.objects.get(follower=follower, following=user)
        follow.delete()  # Remove the follow relationship
        return Response({"message": f"{follower.username} has been removed from your followers."}, status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        return Response({"error": "You are not followed by this user."}, status=status.HTTP_400_BAD_REQUEST)

#to remove following
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_following(request):
    user = request.user
    data = request.data
    try:
        following_user = User.objects.get(username=data.get('username'))  # Username of the user to unfollow
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the logged-in user is following the specified user
    try:
        follow = Follow.objects.get(follower=user, following=following_user)
        follow.delete()  # Remove the follow relationship
        return Response({"message": f"You have unfollowed {following_user.username}."}, status=status.HTTP_200_OK)
    except Follow.DoesNotExist:
        return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

#to get posts of target user by logged in user, but for that logged in user must follow target user.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_posts_by_followed_users(request):
    user = request.user
    data = request.data
    try:
        target_user = User.objects.get(username=data.get('username'))  # Username of the user whose posts to fetch
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the logged-in user is following the target user
    try:
        Follow.objects.get(follower=user, following=target_user)
    except Follow.DoesNotExist:
        return Response({"error": "You must follow this user to view their posts."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch posts by the followed user
    posts = UserPost.objects.filter(publisher=target_user)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#to get list of followers and followings by the logged in user, but for that logged in user must follow target user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followers_and_followings(request):
    user = request.user
    data = request.data
    try:
        target_user = User.objects.get(username=data.get('username'))  # Username of the user whose followers/followings to fetch
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the logged-in user is following the target user
    try:
        Follow.objects.get(follower=user, following=target_user)
    except Follow.DoesNotExist:
        return Response({"error": "You must follow this user to view their followers and followings."}, status=status.HTTP_400_BAD_REQUEST)

    # Get the followers of the target user
    followers = Follow.objects.filter(following=target_user)
    followers_data = [
        {"follower_username": follow.follower.username, "created_at": follow.created_at}
        for follow in followers
    ]

    # Get the followings of the target user
    followings = Follow.objects.filter(follower=target_user)
    followings_data = [
        {"following_username": follow.following.username, "created_at": follow.created_at}
        for follow in followings
    ]

    return Response({
        "followers": followers_data,
        "followings": followings_data
    }, status=status.HTTP_200_OK)

# to like a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request):
    post_id = request.data.get('post_id')
    if not post_id:
        return Response({"error": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = UserPost.objects.get(id=post_id)
    except UserPost.DoesNotExist:
        return Response({"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Allow liking own post
    if post.publisher != request.user:
        # Check if the logged-in user follows the post's publisher
        if not Follow.objects.filter(follower=request.user, following=post.publisher).exists():
            return Response({"error": "You must follow the user to like their post"}, status=status.HTTP_403_FORBIDDEN)

    # Check if the user has already liked the post
    if LikePost.objects.filter(user=request.user, post=post).exists():
        return Response({"error": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)

    # Create the like
    like = LikePost.objects.create(user=request.user, post=post)
    serializer = LikeSerializer(like)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# to comment on a post
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_on_post(request):
    post_id = request.data.get('post_id')
    text = request.data.get('text')

    if not post_id or not text:
        return Response({"error": "Post ID and text are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = UserPost.objects.get(id=post_id)
    except UserPost.DoesNotExist:
        return Response({"error": "Post does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Allow commenting on own post
    if post.publisher != request.user:
        # Check if the logged-in user follows the post's publisher
        if not Follow.objects.filter(follower=request.user, following=post.publisher).exists():
            return Response({"error": "You must follow the user to comment on their post"}, status=status.HTTP_403_FORBIDDEN)
    # Create the comment
    comment = CommentPost.objects.create(user=request.user, post=post, text=text)
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

#to get list of likes on a post

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def users_who_liked_post(request):

    post_id = request.data.get('post_id')
    
    if not post_id:
        return Response(
            {"error": "post_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get the post
    post = get_object_or_404(UserPost, id=post_id)

    # Check if the logged-in user follows the publisher or is the publisher themselves
    follows_publisher = Follow.objects.filter(
        follower=request.user,
        following=post.publisher
    ).exists()

    if not follows_publisher and post.publisher != request.user:
        return Response(
            {"error": "You must follow the publisher to access this data."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Fetch the list of users who liked the post
    likes = LikePost.objects.filter(post=post).select_related('user')
    liked_users = [{"username": like.user.username, "liked_at": like.created_at} for like in likes]
    
    return Response(
        {"post_id": post_id, "likes": liked_users},
        status=status.HTTP_200_OK
    )

# to get the list of user who commented.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def users_who_commented_post(request):

    post_id = request.data.get('post_id')
    
    if not post_id:
        return Response(
            {"error": "post_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get the post
    post = get_object_or_404(UserPost, id=post_id)
    
    # Check if the logged-in user follows the publisher or is the publisher themselves
    follows_publisher = Follow.objects.filter(
        follower=request.user,
        following=post.publisher
    ).exists()

    if not follows_publisher and post.publisher != request.user:
        return Response(
            {"error": "You must follow the publisher to access this data."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Fetch the list of users who commented on the post
    comments = CommentPost.objects.filter(post=post).select_related('user')
    commented_users = [
        {"username": comment.user.username, "comment_text": comment.text, "commented_at": comment.created_at}
        for comment in comments
    ]
    
    return Response(
        {"post_id": post_id, "comments": commented_users},
        status=status.HTTP_200_OK
    )

# to implement user feed
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    # Get the list of users the logged-in user is following
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    
    # Get posts from the followed users, in reverse chronological order
    posts = UserPost.objects.filter(publisher__in=following_users).order_by('-datetime_posted', '-id')

    # Pagination setup
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Limit to 10 posts per page
    paginated_posts = paginator.paginate_queryset(posts, request)
    
    # Serialize the posts
    serializer = PostSerializer(paginated_posts, many=True)
    
    # Return paginated response
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """
    Search for users based on a substring in their username, with pagination.
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response(
            {"error": "Query parameter 'q' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Perform a case-insensitive search
    matching_users = User.objects.filter(username__icontains=query).order_by('username')
    
    # Pagination setup
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Adjust page size as needed
    paginated_users = paginator.paginate_queryset(matching_users, request)
    
    return paginator.get_paginated_response({"query": query, "results": [user.username for user in paginated_users]})
