from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from supabase import Client


POSTS_TABLE_NAME = 'blogvi_posts'
CATEGORIES_TABLE_NAME = 'blogvi_categories'
COLLABORATORS_TABLE_NAME = 'blogvi_post_collaborators'


class IBlogRepository(ABC):
    @abstractmethod
    def create_post(self, data: dict, organization_id: str, created_by_id: str) -> dict:
        """Create a new post"""

    @abstractmethod
    def get_post(self, post_id: str) -> dict:
        """Get a post by ID"""

    @abstractmethod
    def list_posts(self, filters: Optional[dict] = None) -> List[dict]:
        """List posts with optional filters"""

    @abstractmethod
    def update_post(self, post_id: str, data: dict) -> dict:
        """Update a post"""

    @abstractmethod
    def delete_post(self, post_id: str) -> None:
        """Delete a post"""

    @abstractmethod
    def bulk_create_posts(self, posts: List[dict], organization_id: str = None, created_by_id: str = None) -> List[dict]:
        """Create multiple posts and their authors"""

    @abstractmethod
    def bulk_update_posts(self, post_ids: List[str], data: dict) -> List[dict]:
        """Update multiple posts at once"""

    @abstractmethod
    def get_author_by_email(self, email: str) -> Optional[dict]:
        """Get author by email"""

    @abstractmethod
    def create_author(self, data: dict) -> dict:
        """Create a new author"""


class BlogSupabaseRepository(IBlogRepository):
    def __init__(self, supabase_client: Client):
        self._supabase = supabase_client

    def get_author_by_email(self, email: str) -> Optional[dict]:
        """Get author by email (if email is provided)"""
        if not email:
            return None
            
        result = self._supabase.table(COLLABORATORS_TABLE_NAME)\
            .select("*")\
            .eq('email', email)\
            .eq('role', 'author')\
            .limit(1)\
            .execute()
        return result.data[0] if result.data else None

    def create_author(self, data: dict) -> dict:
        """Create a new author. Only name is required."""
        if 'name' not in data:
            raise ValueError("Author name is required")
            
        collab_data = {
            'name': data['name'],
            'role': 'author',
            'email': data.get('email'),  # Optional
            'avatar_url': data.get('avatar_url'),
            'bio': data.get('bio'),
            'social_urls': data.get('social_urls', []),
            'logto_user_id': data.get('logto_user_id'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(COLLABORATORS_TABLE_NAME).insert(collab_data).execute()
        return result.data[0] if result.data else None

    def create_post(self, data: dict, organization_id: str, created_by_id: str) -> dict:
        """Create a post and add author as collaborator"""
        # First create the post
        post_data = {
            **data,
            'logto_organization_id': organization_id,
            'created_by_id': created_by_id,
            'updated_by_id': created_by_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(POSTS_TABLE_NAME).insert(post_data).execute()
        post = result.data[0] if result.data else None
        
        # Add author information if provided
        if post and 'author' in data:
            author_data = data['author']
            author_data['post_id'] = post['id']
            author_data['role'] = 'author'
            self.add_collaborator(post['id'], author_data)
        
        return post

    def get_post(self, post_id: str, organization_id: str) -> dict:
        result = self._supabase.table(POSTS_TABLE_NAME)\
            .select("*")\
            .eq('id', post_id)\
            .eq('logto_organization_id', organization_id)\
            .execute()
        return result.data[0] if result.data else None

    def list_posts(self, filters: Optional[dict] = None) -> List[dict]:
        """List posts with optional filters"""
        # First get all posts
        query = self._supabase.table(POSTS_TABLE_NAME).select("*")
        
        if filters:
            if 'status' in filters:
                query = query.eq('status', filters['status'])
            if 'author_id' in filters:
                query = query.eq('author_id', filters['author_id'])
            if 'category_id' in filters:
                query = query.contains('category_ids', [filters['category_id']])
            if 'search' in filters:
                query = query.or_(f"title.ilike.%{filters['search']}%,content.ilike.%{filters['search']}%")
            if 'from_date' in filters:
                query = query.gte('created_at', filters['from_date'])
            if 'to_date' in filters:
                query = query.lte('created_at', filters['to_date'])
            if 'organization_id' in filters:
                query = query.eq('logto_organization_id', filters['organization_id'])
            if 'created_by_id' in filters:
                query = query.eq('created_by_id', filters['created_by_id'])

        result = query.order('created_at', desc=True).execute()
        posts = result.data if result.data else []
        
        # Then get authors for each post
        for post in posts:
            author_query = self._supabase.table(COLLABORATORS_TABLE_NAME)\
                .select("name, email, avatar_url, bio, social_urls")\
                .eq('post_id', post['id'])\
                .eq('role', 'author')\
                .limit(1)\
                .execute()
            
            author = author_query.data[0] if author_query.data else {
                'name': 'Unknown',
                'email': '',
                'avatar_url': '',
                'bio': '',
                'social_urls': []
            }
            post['author'] = author
            
        return posts

    def update_post(self, post_id: str, organization_id: str, data: dict, updated_by_id: str) -> dict:
        update_data = {
            **data,
            'updated_by_id': updated_by_id,
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(POSTS_TABLE_NAME)\
            .update(update_data)\
            .eq('id', post_id)\
            .eq('logto_organization_id', organization_id)\
            .execute()
        return result.data[0] if result.data else None

    def delete_post(self, post_id: str, organization_id: str) -> None:
        self._supabase.table(POSTS_TABLE_NAME)\
            .delete()\
            .eq('id', post_id)\
            .eq('logto_organization_id', organization_id)\
            .execute()

    def bulk_create_posts(self, posts: List[dict], organization_id: str = None, created_by_id: str = None) -> List[dict]:
        """Create multiple posts and their authors"""
        now = datetime.utcnow().isoformat()
        post_data = []
        author_map = {}  # To keep track of authors we've already processed

        # First create posts
        for post in posts:
            # Remove author data from post before creation
            post_copy = post.copy()
            author_data = post_copy.pop('author', None)
            
            # Store author data for later use
            if author_data:
                author_map[post_copy['title']] = author_data

            post_data.append({
                **post_copy,
                'logto_organization_id': organization_id,  # Can be None
                'created_by_id': created_by_id or 'system',  # Default to system if no user
                'updated_by_id': created_by_id or 'system',
                'created_at': now,
                'updated_at': now
            })
        
        # Create all posts first
        result = self._supabase.table(POSTS_TABLE_NAME).insert(post_data).execute()
        created_posts = result.data if result.data else []
        
        # Now add authors as collaborators
        for post in created_posts:
            author_data = author_map.get(post['title'])
            if author_data:
                # Check if author already exists (only if email is provided)
                existing_author = None
                if author_data.get('email'):
                    existing_author = self.get_author_by_email(author_data['email'])
                
                if existing_author:
                    # Link existing author to this post
                    self.add_collaborator(post['id'], existing_author)
                else:
                    # Create new author and link to post
                    author_data['post_id'] = post['id']
                    self.add_collaborator(post['id'], author_data)
        
        return created_posts

    def bulk_update_posts(self, post_ids: List[str], data: dict, updated_by_id: str) -> List[dict]:
        update_data = {
            **data,
            'updated_by_id': updated_by_id,
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(POSTS_TABLE_NAME)\
            .update(update_data)\
            .in_('id', post_ids)\
            .execute()
        return result.data if result.data else []

    def add_collaborator(self, post_id: str, data: dict) -> dict:
        """Add a collaborator (including authors) to a post"""
        if 'name' not in data:
            raise ValueError("Collaborator name is required")
            
        collab_data = {
            'post_id': post_id,  # Can be None for standalone authors
            'name': data['name'],
            'role': data.get('role', 'author'),  # Default to author role
            'email': data.get('email'),  # Optional
            'avatar_url': data.get('avatar_url'),
            'bio': data.get('bio'),
            'social_urls': data.get('social_urls', []),
            'logto_user_id': data.get('logto_user_id'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(COLLABORATORS_TABLE_NAME).insert(collab_data).execute()
        return result.data[0] if result.data else None

    def list_collaborators(self, post_id: str = None) -> List[dict]:
        """List collaborators, optionally filtered by post_id"""
        query = self._supabase.table(COLLABORATORS_TABLE_NAME).select("*")
        if post_id:
            query = query.eq('post_id', post_id)
        result = query.execute()
        return result.data if result.data else [] 