# BlogVi Manager - Design Document

## Overview
BlogVi Manager is a Streamlit-based application for managing blog content with a focus on CSV compatibility and efficient content management. The application integrates with Logto for authentication and Chargebee for billing/credits management.

## Core Features

### Authentication & User Management
- [x] Logto-based authentication
- [x] User profile management
- [x] Organization support
- [x] Credits system integration

### Post Management
- [ ] Create/Edit/Delete blog posts
  - Rich Markdown editor with preview
  - Image upload and management
  - Post status (Draft/Published)
  - SEO metadata fields
- [ ] CSV Import/Export
  - Import from Google Forms CSV
  - Export in BlogVi-compatible format
  - Bulk import validation
  - Error reporting
- [ ] Post Library
  - Searchable interface
  - Advanced filtering (status, author, category, date)
  - Bulk operations
  - List and grid views
- [ ] Collaboration Workflow
  - Post status stages:
    - Draft (Author writing)
    - Review (Ready for editorial review)
    - Revision (Changes requested)
    - Approved (Ready for publishing)
    - Published
    - Archived
  - Role-based permissions:
    - Author: Create, Edit own posts
    - Editor: Review, Request changes
    - Publisher: Approve, Publish
    - Admin: All permissions
  - Review comments and annotations
  - Change tracking
  - Email notifications for status changes
  - Audit trail of post history

### Category Management
- [ ] Create/Edit/Delete categories
- [ ] Category hierarchy
- [ ] Category descriptions
- [ ] Post count tracking
- [ ] Category-based filtering

### Author Management
- [ ] Author profiles
  - Name
  - Email
  - Avatar
  - Bio
  - Social links
- [ ] Author-based post filtering
- [ ] Author statistics

### Media Management
- [ ] Image upload
- [ ] Image optimization
- [ ] Image gallery
- [ ] Usage tracking
- [ ] Storage management

### Settings & Configuration
- [x] API key management
- [x] Credits display
- [ ] Export settings
- [ ] Default preferences
- [ ] Workflow configuration
  - Custom status stages
  - Role permissions
  - Notification settings

## Technical Architecture

### Frontend (Streamlit)
- Main navigation
- Form components
- Markdown editor
- Image previews
- Real-time updates
- Advanced search interface
- Workflow status board

### Backend Services
- Supabase for data storage
- Logto for authentication
- Chargebee for billing
- S3/CloudFront for media
- Email service for notifications

### Data Models
- Posts
  - title: string
  - content: text (markdown)
  - status: enum (draft/review/revision/approved/published/archived)
  - author_id: foreign key
  - category_ids: array
  - created_at: timestamp
  - updated_at: timestamp
  - published_at: timestamp
  - metadata: jsonb
  - workflow_data: jsonb
    - current_stage
    - assigned_reviewer
    - review_comments
    - revision_history

- Categories
  - name: string
  - slug: string
  - description: text
  - parent_id: foreign key
  - created_at: timestamp

- Authors
  - name: string
  - email: string
  - avatar_url: string
  - bio: text
  - social_links: jsonb
  - created_at: timestamp
  - role: enum (author/editor/publisher/admin)

- Comments
  - post_id: foreign key
  - user_id: foreign key
  - content: text
  - created_at: timestamp
  - type: enum (review/general)

## Implementation Plan

### Phase 1 - Core Setup (Completed)
- [x] Basic application structure
- [x] Logto authentication
- [x] Credits system
- [x] Basic routing

### Phase 2 - Content Management
- [ ] CSV Import/Export
  - CSV upload interface
  - Validation and error handling
  - Import progress tracking
  - Export functionality
- [ ] Post Library Interface
  - Search and filter implementation
  - List/Grid view toggle
  - Bulk operations UI
- [ ] Basic Post Management
  - Create/Edit forms
  - Status management
  - Category assignment
- [ ] Author Management
  - Profile CRUD
  - Role assignment

### Phase 3 - Collaboration Features
- [ ] Workflow Implementation
  - Status stages
  - Role permissions
  - Review system
  - Comments
- [ ] Notification System
  - Email integration
  - In-app notifications
- [ ] Audit Trail
  - Change tracking
  - History view

### Phase 4 - Polish & Optimization
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Error handling
- [ ] Documentation

## CSV Format Support
The application will support the following CSV format:
```
Timestamp,Author Name,Markdown,Author email,Author Avatar Image URL,Excerpt,Categories,About the Author,Social URLs,Header Image,Author Image,Title,Status,Hero Image,Legacy Slugs,Slug
```

## Future Considerations
- Real-time collaboration
- Version control for posts
- Advanced SEO tools
- Analytics integration
- API access
- Webhook support
- AI-assisted content suggestions
- Automated content quality checks 