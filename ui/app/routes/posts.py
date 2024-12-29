import streamlit as st
from dependency_injector.wiring import inject, Provide
import pandas as pd
from io import StringIO

from infrastructure.service.blog import BlogService
from infrastructure.service.user import UserService


@inject
def main(
    blog_service: BlogService = Provide['blog_service'],
    user_service: UserService = Provide['user_service'],
):
    st.markdown(f'''
        # Blog Posts
        ''')
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Post Library", "Create Post", "Import/Export"])
    
    with tab1:
        show_post_library(blog_service, user_service)
    
    with tab2:
        show_create_post(blog_service)
        
    with tab3:
        show_import_export(blog_service)


def show_post_library(blog_service: BlogService, user_service: UserService):
    """Show the post library with search and filters"""
    # Search and filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search = st.text_input("Search posts", key="post_search")
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "Draft", "Published", "Review", "Revision", "Approved", "Archived"],
            key="status_filter"
        )
    
    with col3:
        # Get all unique authors from posts
        all_posts = blog_service.list_posts()
        authors = {(post['author']['name'], post['author']['email']) 
                  for post in all_posts if post.get('author')}
        author_options = ["All"] + [f"{name} ({email})" for name, email in authors]
        author_filter = st.selectbox("Author", author_options, key="author_filter")
    
    with col4:
        date_range = st.date_input(
            "Date range",
            value=[],
            key="date_filter"
        )

    # Build filters
    filters = {}
    if search:
        filters['search'] = search
    if status_filter != "All":
        filters['status'] = status_filter.lower()
    if author_filter != "All":
        # Extract email from author filter
        author_email = author_filter.split('(')[-1].rstrip(')')
        filters['author_email'] = author_email
    if date_range:
        if len(date_range) == 2:
            filters['from_date'] = date_range[0].isoformat()
            filters['to_date'] = date_range[1].isoformat()

    # Get posts
    posts = blog_service.list_posts(filters)

    # Display posts
    if not posts:
        st.info("No posts found")
        return

    # Convert to DataFrame for better display
    df = pd.DataFrame([
        {
            'Title': post['title'],
            'Author': f"{post['author']['name']} ({post['author']['email']})",
            'Status': post['status'].capitalize(),
            'Categories': ', '.join(post['categories']),
            'Created': pd.to_datetime(post['created_at']).strftime('%Y-%m-%d'),
            'ID': post['id']
        }
        for post in posts
    ])

    # Show table with selection
    selected = st.data_editor(
        df,
        hide_index=True,
        column_config={
            'ID': st.column_config.Column(
                'ID',
                help='Post ID',
                width='small',
                required=True,
            ),
            'Author': st.column_config.Column(
                'Author',
                help='Post author',
                width='medium',
            ),
            'Title': st.column_config.Column(
                'Title',
                help='Post title',
                width='large',
            ),
        },
        use_container_width=True
    )

    # Bulk actions
    if len(selected) > 0:
        st.markdown("### Bulk Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_status = st.selectbox(
                "Change status to",
                ["Draft", "Published", "Review", "Revision", "Approved", "Archived"]
            )
        
        with col2:
            # Get all authors for reassignment
            author_reassign = st.selectbox(
                "Reassign to author",
                ["Keep current"] + [f"{name} ({email})" for name, email in authors]
            )
        
        with col3:
            if st.button("Apply Changes"):
                post_ids = selected['ID'].tolist()
                update_data = {'status': new_status.lower()}
                
                # Add author reassignment if selected
                if author_reassign != "Keep current":
                    author_email = author_reassign.split('(')[-1].rstrip(')')
                    author_name = author_reassign.split('(')[0].strip()
                    update_data['author'] = {
                        'name': author_name,
                        'email': author_email
                    }
                
                blog_service.bulk_update_posts(post_ids, update_data)
                st.success(f"Updated {len(post_ids)} posts")
                st.rerun()


def show_import_export(blog_service: BlogService):
    """Show import/export functionality"""
    st.markdown("### Import Posts")
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            # Read file based on type
            file_type = uploaded_file.name.split('.')[-1].lower()
            if file_type == 'csv':
                df = pd.read_csv(uploaded_file)
                # Get CSV content for import
                uploaded_file.seek(0)
                csv_content = uploaded_file.getvalue().decode()
            else:  # Excel files
                df = pd.read_excel(uploaded_file)
                # Convert Excel to CSV format
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_content = csv_buffer.getvalue()
            
            # Show preview
            st.markdown("#### Preview")
            st.dataframe(df.head())
            
            # Import button
            if st.button("Import Posts"):
                with st.spinner("Importing posts..."):
                    successful, failed = blog_service.import_from_csv(csv_content)
                    
                    if successful:
                        st.success(f"Successfully imported {len(successful)} posts")
                    if failed:
                        st.error(f"Failed to import {len(failed)} posts")
                        with st.expander("Show errors"):
                            for fail in failed:
                                st.write(f"Row: {fail['row']}")
                                st.write(f"Error: {fail['error']}")
                                st.markdown("---")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

    st.markdown("### Export Posts")
    if st.button("Export All Posts"):
        # Get all posts
        posts = blog_service.list_posts()
        if not posts:
            st.info("No posts to export")
            return
        
        # Convert to CSV
        csv_content = blog_service.export_to_csv(posts)
        
        # Offer download
        st.download_button(
            "Download CSV",
            csv_content,
            "posts_export.csv",
            "text/csv",
            key='download-csv'
        ) 


def show_create_post(blog_service: BlogService):
    """Show the create post form"""
    st.markdown("### Create New Post")
    
    with st.form("create_post_form"):
        # Basic Information
        title = st.text_input("Title", key="new_post_title")
        content = st.text_area("Content (Markdown)", height=300, key="new_post_content")
        excerpt = st.text_area("Excerpt/Short Summary", key="new_post_excerpt")
        
        # Author Information
        st.subheader("Author Information")
        col1, col2 = st.columns(2)
        with col1:
            author_name = st.text_input("Author Name", key="new_post_author_name")
            author_email = st.text_input("Author Email", key="new_post_author_email")
            author_avatar = st.text_input("Author Avatar URL", key="new_post_author_avatar")
        with col2:
            author_bio = st.text_area("About the Author", key="new_post_author_bio")
            author_social = st.text_input("Social URLs (comma-separated)", key="new_post_author_social")
        
        # Categories and Status
        col1, col2 = st.columns(2)
        with col1:
            categories = st.text_input("Categories (comma-separated)", key="new_post_categories")
        with col2:
            status = st.selectbox(
                "Status",
                ["draft", "published", "review", "revision", "approved", "archived"],
                key="new_post_status"
            )
        
        # Images
        st.subheader("Images")
        col1, col2 = st.columns(2)
        with col1:
            hero_image = st.text_input("Hero Image URL", key="new_post_hero_image")
        with col2:
            header_image = st.text_input("Header Image URL", key="new_post_header_image")
        
        # URL Configuration
        st.subheader("URL Configuration")
        slug = st.text_input("Slug (optional)", key="new_post_slug")
        legacy_slugs = st.text_input("Legacy Slugs (comma-separated, optional)", key="new_post_legacy_slugs")
        
        # Submit button
        submitted = st.form_submit_button("Create Post")
        
        if submitted:
            if not all([title, content, author_name, author_email]):
                st.error("Please fill in all required fields: Title, Content, Author Name, and Author Email")
                return
            
            # Prepare post data
            post_data = {
                'title': title,
                'content': content,
                'status': status,
                'author': {
                    'name': author_name,
                    'email': author_email,
                    'avatar_url': author_avatar,
                    'bio': author_bio,
                    'social_urls': [url.strip() for url in author_social.split(',')] if author_social else []
                },
                'excerpt': excerpt,
                'categories': [cat.strip() for cat in categories.split(',')] if categories else [],
                'hero_image': hero_image,
                'header_image': header_image,
                'slug': slug if slug else None,
                'legacy_slugs': [s.strip() for s in legacy_slugs.split(',')] if legacy_slugs else [],
                'metadata': {
                    'timestamp': pd.Timestamp.now().isoformat()
                }
            }
            
            try:
                blog_service.create_post(post_data)
                st.success("Post created successfully!")
                # Clear form
                for key in st.session_state.keys():
                    if key.startswith("new_post_"):
                        st.session_state[key] = ""
            except Exception as e:
                st.error(f"Error creating post: {str(e)}") 