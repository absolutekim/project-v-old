from django.urls import path
from .views import PostListCreateView, PostDetailDeleteView, create_comment, delete_comment, get_comments, search_posts, get_user_posts, get_user_comments

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailDeleteView.as_view(), name='post-detail-delete'),
    path('posts/<int:post_id>/comments/', create_comment, name='create-comment'),  # ✅ For POST requests
    path('posts/<int:post_id>/comments/all/', get_comments, name='get-comments'),  # ✅ For GET requests
    path('comments/<int:comment_id>/', delete_comment, name='delete-comment'),
    path('posts/search/', search_posts, name='search-posts'),  # ✅ Added search URL
    path('user/posts/', get_user_posts, name='user-posts'),  # ✅ Get user's posts
    path('user/comments/', get_user_comments, name='user-comments'),  # ✅ Get user's comments
]