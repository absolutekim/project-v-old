from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

# ✅ List and create posts
class PostListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating community posts.
    Provides GET (list all posts) and POST (create new post) functionality.
    
    GET: Returns a list of all posts ordered by creation date (newest first)
    POST: Creates a new post with the authenticated user as author
    """
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        """
        pass request object to serializer
        """
        context = super().get_serializer_context()
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  # Automatically set the author


# ✅ Retrieve, update and delete posts
class PostDetailDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting specific posts.
    Provides GET (view details), PUT/PATCH (update), and DELETE functionality for individual posts.
    
    GET: Returns post details along with its comments
    PUT/PATCH: Updates post contents (only allowed for the post author)
    DELETE: Removes a post (only allowed for the post author)
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method that includes post comments.
        Enhances the standard retrieve by including related comments.
        
        Returns:
            Response with post data including associated comments
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # ✅ Add comments list
        comments = Comment.objects.filter(post=instance).order_by('-created_at')
        comment_serializer = CommentSerializer(comments, many=True, context={'request': request})

        data = serializer.data
        data['comments'] = comment_serializer.data  # ✅ Add comments to post data

        return Response(data)
        
    def update(self, request, *args, **kwargs):
        """
        Custom update method with author verification.
        Only allows post update by the original author.
        
        Returns:
            Response with updated data or permission error
        """
        instance = self.get_object()
        
        # ✅ Prevent update if not the author
        if request.user != instance.author:
            return Response({'error': 'You can only edit your own posts.'}, status=status.HTTP_403_FORBIDDEN)
            
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method with author verification.
        Only allows post deletion by the original author.
        
        Returns:
            Response with success status or permission error
        """
        instance = self.get_object()

        # ✅ Prevent deletion if not the author
        if request.user != instance.author:
            return Response({'error': 'You can only delete your own posts.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ✅ Create comment
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, post_id):
    """
    Create comment API endpoint.
    Adds a new comment to a specific post.
    
    Parameters:
        request: HTTP request with comment data
        post_id: ID of the post to comment on
        
    Returns:
        Response with created comment or error details
    """
    post = get_object_or_404(Post, id=post_id)
    serializer = CommentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(post=post, author=request.user)  # Automatically set post and author
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Delete comment
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    """
    Delete comment API endpoint.
    Removes a comment if the requester is the comment author.
    
    Parameters:
        request: HTTP request from authenticated user
        comment_id: ID of the comment to delete
        
    Returns:
        Response with success status or permission error
    """
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        return Response({'error': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# ✅ Get user comments
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_comments(request, post_id):
    """
    Get comments API endpoint.
    Retrieves all comments for a specific post.
    
    Parameters:
        request: HTTP request
        post_id: ID of the post to get comments for
        
    Returns:
        Response with list of comments for the post
    """
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    serializer = CommentSerializer(comments, many=True, context={'request': request})
    return Response(serializer.data)

# ✅ Search posts
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def search_posts(request):
    """
    Search posts API endpoint.
    Searches for posts by title, author username, or both based on search_type.
    
    Parameters:
        request: HTTP request with query and search_type parameters
        
    Returns:
        Response with list of matching posts
    """
    query = request.GET.get('query', '')
    search_type = request.GET.get('search_type', 'all')  # Default to 'all'
    
    if not query:
        return Response({'error': 'Please provide a search query'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filter posts based on search type
    if search_type == 'title':
        # Search only in post titles
        posts = Post.objects.filter(title__icontains=query).order_by('-created_at')
    elif search_type == 'author':
        # Search only by author username
        posts = Post.objects.filter(author__username__icontains=query).order_by('-created_at')
    else:
        # Search in both title and author (default)
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(author__username__icontains=query)
        ).order_by('-created_at')
    
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

# ✅ Get user posts
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    """
    User posts API endpoint.
    Retrieves all posts created by the authenticated user.
    
    Parameters:
        request: HTTP request from authenticated user
        
    Returns:
        Response with list of user's posts
    """
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)

# ✅ Get user comments
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_comments(request):
    """
    User comments API endpoint.
    Retrieves all comments created by the authenticated user.
    
    Parameters:
        request: HTTP request from authenticated user
        
    Returns:
        Response with list of user's comments including post information
    """
    comments = Comment.objects.filter(author=request.user).order_by('-created_at')
    
    # Create a custom response with post information
    result = []
    for comment in comments:
        comment_data = CommentSerializer(comment, context={'request': request}).data
        # Add post information to help navigation
        comment_data['post_id'] = comment.post.id
        comment_data['post_title'] = comment.post.title
        result.append(comment_data)
    
    return Response(result)
