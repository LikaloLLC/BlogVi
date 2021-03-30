#TaSaB - Tailwindcss Static Blog (with Search)
import markdown
from jinja2 import Template
from utils import ImgExtExtension, H1H2Extension
import pandas as pd
import requests
#https://docs.google.com/spreadsheets/d/1deKANndKOOmOdQUQWDK6-zC7P6J25SzBrUx2RX9lvkY/gviz/tq?tqx=out:csv&sheet=Form%20Responses%201
from io import StringIO



class Blog():
    def generate_categories(self):
        pass


    def generate_landing_page(self):

        md = markdown.Markdown(extensions=[ImgExtExtension(), H1H2Extension()])

        file = md.convertFile('articles/ciaran_1.md')

        header_image = file.images[0]
        name_image = md.h2s



    def generate_articles(self):
        pass


    def generate_rss(self):
        pass


    def create_search_index(self):
        pass






if __name__ == '__main__':
    pass

