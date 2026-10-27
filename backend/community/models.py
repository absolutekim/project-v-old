from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    """
    Community post model.
    
    Stores user-created posts and includes title, content, creation time, update time, 
    and author information. Posts can have multiple comments.
    """
    title = models.CharField(max_length=255)  # Post title
    content = models.TextField()  # Post content
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp (auto-saved)
    updated_at = models.DateTimeField(auto_now=True)  # Update timestamp (auto-updated)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")  # Post author (cascade delete with user)

    def __str__(self):
        return self.title

class Comment(models.Model):
    """
    Post comment model.
    
    Stores user comments on posts and includes the related post, author, content, 
    and creation time. Comments are deleted when the related post or user is deleted.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")  # Related post (cascade delete with post)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")  # Comment author
    content = models.TextField()  # Comment content
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp (auto-saved)

    def __str__(self):
        return f"{self.author.username} - {self.content[:20]}"  # First 20 chars of content for readability

