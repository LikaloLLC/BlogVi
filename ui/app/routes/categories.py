import streamlit as st
from dependency_injector.wiring import inject, Provide

from infrastructure.service.blog import BlogService


@inject
def main(
    blog_service: BlogService = Provide['blog_service'],
):
    st.markdown(f'''
        # Categories
        ''')
    
    st.write("Categories management coming soon...") 