import csv
from io import StringIO
from typing import List, Optional
from datetime import datetime

from repositories.blog import IBlogRepository


class BlogService:
    def __init__(self, blog_repo: IBlogRepository):
        self._blog_repo = blog_repo

    def import_from_csv(self, csv_content: str) -> tuple[List[dict], List[dict]]:
        """Import posts from CSV content. Returns (successful_imports, failed_imports)"""
        reader = csv.DictReader(StringIO(csv_content))
        successful = []
        failed = []

        for row in reader:
            try:
                post_data = {
                    'title': row['Title'],
                    'content': row['Markdown'],
                    'status': row['Status'],
                    'author': {
                        'name': row['Author Name'],
                        'email': row['Author email'],
                        'avatar_url': row['Author Avatar Image URL'],
                        'bio': row['About the Author'],
                        'social_urls': row['Social URLs'].split(',') if row['Social URLs'] else []
                    },
                    'excerpt': row['Excerpt/Short Summary'],
                    'categories': row['Categories'].split(',') if row['Categories'] else [],
                    'hero_image': row['Hero Image (Used for RSS)'],
                    'header_image': row['Header Image (will be used in RSS feed)'],
                    'slug': row['Slug'] if row['Slug'] else None,
                    'legacy_slugs': row['Legacy Slugs'].split(',') if row['Legacy Slugs'] else [],
                    'metadata': {
                        'timestamp': row['Timestamp'],
                        'author_image': row['Author Image'],
                    }
                }
                successful.append(post_data)
            except Exception as e:
                failed.append({
                    'row': row,
                    'error': str(e)
                })

        if successful:
            self._blog_repo.bulk_create_posts(successful)

        return successful, failed

    def create_post(self, data: dict) -> dict:
        """Create a new post"""
        return self._blog_repo.create_post(data)

    def get_post(self, post_id: str) -> dict:
        """Get a post by ID"""
        return self._blog_repo.get_post(post_id)

    def list_posts(self, filters: Optional[dict] = None) -> List[dict]:
        """List posts with optional filters"""
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