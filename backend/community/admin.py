from django.contrib import admin
from .models import Post, Comment

# ✅ Post management configuration
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')  # ✅ Fields displayed in the list view
    search_fields = ('title', 'author__username')  # ✅ Enable search by title and author
    list_filter = ('created_at',)  # ✅ Add filter (creation date)
    ordering = ('-created_at',)  # ✅ Sort with newest posts at the top

# ✅ Comment management configuration
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'author', 'post', 'created_at')  # ✅ Fields displayed in the list view
    search_fields = ('content', 'author__username', 'post__title')  # ✅ Enable search by content, author, and post title
    list_filter = ('created_at',)  # ✅ Add filter (creation date)
    ordering = ('-created_at',)  # ✅ Sort with newest comments at the top
