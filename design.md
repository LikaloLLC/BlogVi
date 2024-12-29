Based on further analysis, here's a more detailed breakdown of the system:
Core Functionality:
Article Management:
Articles are loaded from a CSV source
Supports legacy URL slugs with redirects
Article status tracking
Landing Page:
Generates index/landing pages
Handles article listing and organization
Translation System:
Built-in translation support
Uses DeepL as the translation provider
Configurable source/target languages
Content Processing:
Markdown processing for content
Template-based rendering using Jinja2
RSS feed generation
URL slug management]



Key Features:
Rich Markdown editor with preview
Image upload and management
Post status management (Draft/Published)
Category management
Author profile management
Export to CSV (for BlogVi compatibility)
Real-time preview of blog posts
Search and filter capabilities
Bulk operations


so what I wanted to do was add a streamlit server component to it that we can deploy to manage our blogs and submisions using a UI instead. Currently everything is managed in a csv and it is becoming very combersome to manage these entries. We can use mongodb  as a database to store and manage the actual submissions. The idea would be to create a ui component for it that we will be able to deploy to a kubernetes cluster. I've added the csv file example Likalo Blog Submissions - Form Responses 1.csv. We would need to first design the UI app and how it will work and than we can test it how it works with the blogvi itself. I have also added a sample streamlit UI app. It has an authentication system tied to fusion auth that already works. So we could leverage its existing authentication system and build the UI app on top of it. 