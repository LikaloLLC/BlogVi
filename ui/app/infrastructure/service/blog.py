import csv
from io import StringIO
from typing import List, Optional, Dict, Tuple
import streamlit as st
import pandas as pd

from repositories.blog import IBlogRepository


class BlogService:
    def __init__(self, blog_repo: IBlogRepository):
        self._blog_repo = blog_repo

    def _get_or_create_author(self, author_data: dict) -> str:
        """Get existing author or create a new one. Returns author ID."""
        # Try to find existing author by email
        existing_author = self._blog_repo.get_author_by_email(author_data['email'])
        if existing_author:
            return existing_author['id']
        
        # Create new author if not found
        new_author = self._blog_repo.create_author({
            'name': author_data['name'],
            'email': author_data['email'],
            'avatar_url': author_data.get('avatar_url', ''),
            'bio': author_data.get('bio', ''),
            'social_urls': author_data.get('social_urls', [])
        })
        return new_author['id']

    def import_from_csv(self, csv_content: str) -> Tuple[List[dict], List[dict]]:
        """Import posts from CSV content"""
        try:
            # Get current user info from session
            if 'user_info' not in st.session_state:
                raise ValueError("User not authenticated")
            user_info = st.session_state.user_info
            if not user_info:
                raise ValueError("User not authenticated")
            
            # Read CSV content
            df = pd.read_csv(StringIO(csv_content))
            successful_imports = []
            failed_imports = []
            
            # Process each row
            posts_to_create = []
            for _, row in df.iterrows():
                try:
                    # Convert row to dict and clean up data
                    post_data = row.to_dict()
                    post_data = {k: v for k, v in post_data.items() if pd.notna(v)}
                    
                    # Extract author data
                    author_data = {
                        'name': post_data.pop('Author Name', None),
                        'email': post_data.pop('Author email', None),
                        'avatar_url': post_data.pop('Author image', None),
                        'bio': post_data.pop('About the Author', None),
                        'social_urls': [url.strip() for url in post_data.pop('Social URLs', '').split(',') if url.strip()]
                    }
                    
                    # Map CSV fields to post fields
                    post = {
                        'title': post_data.get('Title'),
                        'content': post_data.get('Markdown'),
                        'excerpt': post_data.get('Excerpt/Short Summary'),
                        'status': 'published' if post_data.get('Status', '1') == '1' else 'draft',
                        'categories': [cat.strip() for cat in post_data.get('Categories', '').split(',') if cat.strip()],
                        'header_image': post_data.get('Header Image'),
                        'slug': post_data.get('Slug'),
                        'metadata': {
                            'timestamp': post_data.get('Timestamp'),
                            'author_image': post_data.get('Author image', '')
                        },
                        'author': author_data
                    }
                    
                    posts_to_create.append(post)
                    successful_imports.append(row)
                except Exception as e:
                    failed_imports.append({'row': row, 'error': str(e)})
            
            # Bulk create all posts
            if posts_to_create:
                self._blog_repo.bulk_create_posts(posts_to_create, created_by_id=user_info.id)
            
            return successful_imports, failed_imports
        except Exception as e:
            raise ValueError(f"Failed to import CSV: {str(e)}")

    def create_post(self, data: dict) -> dict:
        """Create a new post"""
        if 'user_info' not in st.session_state:
            raise ValueError("User not authenticated")
            
        user_info = st.session_state.user_info
        if not user_info:
            raise ValueError("User not authenticated")

        # Handle author creation/lookup if author info is provided
        if 'author' in data:
            author_id = self._get_or_create_author(data['author'])
            data['author_id'] = author_id
            del data['author']

        return self._blog_repo.create_post(
            data,
            organization_id=None,  # Make organization optional
            created_by_id=user_info.id
        )

    def get_post(self, post_id: str) -> dict:
        """Get a post by ID"""
        return self._blog_repo.get_post(post_id)

    def list_posts(self, filters: Optional[dict] = None) -> List[dict]:
        """List posts with optional filters"""
        # Get current user info from session
        if 'user_info' not in st.session_state:
            raise ValueError("User not authenticated")
        user_info = st.session_state.user_info
        if not user_info:
            raise ValueError("User not authenticated")
        
        if not filters:
            filters = {}
        
        # Add user filter
        filters['created_by_id'] = user_info.id
        
        return self._blog_repo.list_posts(filters)

    def update_post(self, post_id: str, data: dict) -> dict:
        """Update a post"""
        return self._blog_repo.update_post(post_id, data)

    def delete_post(self, post_id: str) -> None:
        """Delete a post"""
        return self._blog_repo.delete_post(post_id)

    def bulk_update_posts(self, post_ids: List[str], data: dict) -> List[dict]:
        """Update multiple posts at once"""
        return self._blog_repo.bulk_update_posts(post_ids, data)

    def export_to_csv(self, posts: List[dict]) -> str:
        """Export posts to CSV format"""
        output = StringIO()
        fieldnames = [
            'Timestamp', 'Author Name', 'Markdown', 'Author email', 'Author Avatar Image URL',
            'Excerpt/Short Summary', 'Categories', 'About the Author', 'Social URLs',
            'Header Image (will be used in RSS feed)', 'Author Image', 'Title', 'Status',
            'Hero Image (Used for RSS)', 'Legacy Slugs', 'Slug'
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for post in posts:
            writer.writerow({
                'Timestamp': post['metadata'].get('timestamp', ''),
                'Author Name': post['author']['name'],
                'Markdown': post['content'],
                'Author email': post['author']['email'],
                'Author Avatar Image URL': post['author']['avatar_url'],
                'Excerpt/Short Summary': post['excerpt'],
                'Categories': ','.join(post['categories']),
                'About the Author': post['author']['bio'],
                'Social URLs': ','.join(post['author']['social_urls']),
                'Header Image (will be used in RSS feed)': post['header_image'],
                'Author Image': post['metadata'].get('author_image', ''),
                'Title': post['title'],
                'Status': post['status'],
                'Hero Image (Used for RSS)': post['hero_image'],
                'Legacy Slugs': ','.join(post['legacy_slugs']),
                'Slug': post['slug'] or ''
            })

        return output.getvalue() 