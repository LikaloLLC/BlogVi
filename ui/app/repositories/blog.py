from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from supabase import Client


POSTS_TABLE_NAME = 'blogvi_posts'
CATEGORIES_TABLE_NAME = 'blogvi_categories'
COLLABORATORS_TABLE_NAME = 'blogvi_post_collaborators'


class IBlogRepository(ABC):
    @abstractmethod
    def create_post(self, data: dict, organization_id: str, author_id: str) -> dict:
        """Create a new post"""

    @abstractmethod
    def get_post(self, post_id: str, organization_id: str) -> dict:
        """Get a post by ID within an organization"""

    @abstractmethod
    def list_posts(self, organization_id: str, filters: Optional[dict] = None) -> List[dict]:
        """List posts with optional filters within an organization"""

    @abstractmethod
    def update_post(self, post_id: str, organization_id: str, data: dict, updated_by_id: str) -> dict:
        """Update a post"""

    @abstractmethod
    def delete_post(self, post_id: str, organization_id: str) -> None:
        """Delete a post"""

    @abstractmethod
    def bulk_create_posts(self, posts: List[dict], organization_id: str, created_by_id: str) -> List[dict]:
        """Create multiple posts at once"""

    @abstractmethod
    def bulk_update_posts(self, post_ids: List[str], organization_id: str, data: dict, updated_by_id: str) -> List[dict]:
        """Update multiple posts at once"""

    @abstractmethod
    def add_collaborator(self, post_id: str, user_id: str, role: str) -> dict:
        """Add a collaborator to a post"""

    @abstractmethod
    def list_collaborators(self, post_id: str) -> List[dict]:
        """List collaborators for a post"""


class BlogSupabaseRepository(IBlogRepository):
    def __init__(self, supabase_client: Client):
        self._supabase = supabase_client

    def create_post(self, data: dict, organization_id: str, author_id: str) -> dict:
        post_data = {
            **data,
            'logto_organization_id': organization_id,
            'author_id': author_id,
            'created_by_id': author_id,
            'updated_by_id': author_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(POSTS_TABLE_NAME).insert(post_data).execute()
        return result.data[0] if result.data else None

    def get_post(self, post_id: str, organization_id: str) -> dict:
        result = self._supabase.table(POSTS_TABLE_NAME)\
            .select("*")\
            .eq('id', post_id)\
            .eq('logto_organization_id', organization_id)\
            .execute()
        return result.data[0] if result.data else None

    def list_posts(self, organization_id: str, filters: Optional[dict] = None) -> List[dict]:
        query = self._supabase.table(POSTS_TABLE_NAME)\
            .select("*")\
            .eq('logto_organization_id', organization_id)
        
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

        result = query.order('created_at', desc=True).execute()
        return result.data if result.data else []

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

    def bulk_create_posts(self, posts: List[dict], organization_id: str, created_by_id: str) -> List[dict]:
        now = datetime.utcnow().isoformat()
        post_data = []
        for post in posts:
            post_data.append({
                **post,
                'logto_organization_id': organization_id,
                'created_by_id': created_by_id,
                'updated_by_id': created_by_id,
                'created_at': now,
                'updated_at': now
            })
        result = self._supabase.table(POSTS_TABLE_NAME).insert(post_data).execute()
        return result.data if result.data else []

    def bulk_update_posts(self, post_ids: List[str], organization_id: str, data: dict, updated_by_id: str) -> List[dict]:
        update_data = {
            **data,
            'updated_by_id': updated_by_id,
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(POSTS_TABLE_NAME)\
            .update(update_data)\
            .in_('id', post_ids)\
            .eq('logto_organization_id', organization_id)\
            .execute()
        return result.data if result.data else []

    def add_collaborator(self, post_id: str, user_id: str, role: str) -> dict:
        collab_data = {
            'post_id': post_id,
            'user_id': user_id,
            'role': role,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        result = self._supabase.table(COLLABORATORS_TABLE_NAME).insert(collab_data).execute()
        return result.data[0] if result.data else None

    def list_collaborators(self, post_id: str) -> List[dict]:
        result = self._supabase.table(COLLABORATORS_TABLE_NAME)\
            .select("*")\
            .eq('post_id', post_id)\
            .execute()
        return result.data if result.data else [] 