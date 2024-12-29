from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import NewType

from pydantic import BaseModel

from domain.model.iam import User

PostId = NewType('PostId', str)
CategoryId = NewType('CategoryId', str)


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Category(BaseModel):
    id: CategoryId
    name: str
    slug: str
    description: str | None = None


class BlogPost(BaseModel):
    id: PostId | None = None
    title: str
    content: str
    excerpt: str | None = None
    author: User
    categories: list[Category] = []
    status: PostStatus = PostStatus.DRAFT
    hero_image: str | None = None
    slug: str | None = None
    legacy_slugs: list[str] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class IBlogRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_: PostId) -> BlogPost | None:
        """Get a blog post by ID"""

    @abstractmethod
    def list_posts(self, *, status: PostStatus | None = None) -> list[BlogPost]:
        """List all blog posts"""

    @abstractmethod
    def save(self, post: BlogPost) -> None:
        """Save a blog post"""

    @abstractmethod
    def delete(self, id_: PostId) -> None:
        """Delete a blog post"""

    @abstractmethod
    def list_categories(self) -> list[Category]:
        """List all categories"""

    @abstractmethod
    def save_category(self, category: Category) -> None:
        """Save a category"""

    @abstractmethod
    def delete_category(self, id_: CategoryId) -> None:
        """Delete a category""" 