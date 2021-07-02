# BlogVi - Tailwind Static Blog with Search (No backend)
 by [Docsie](https://www.docsie.io).
 
# 👋 Reason for this Project

I tried to setup a static blog for my company, but I quickly found out that it's really difficult to get a nice looking *free blog with search and comments* without:
1. ❌ Paying a monthly Subscription for a SaaS commercial Blog
2. ❌ Hosting a search backend/opensource blog
3. ❌ Paying for third party search solution

The goal of this project is to be a free static blog:
1.  ✅ That can be hosted on github pages
2.  ✅ That supports search, comments, analytics and custom javascripts out of the box with minimal configuration
3.  ✅ That looks nice and modern and supports beautiful responsive theming with tailwind CSS
4.  ✅ That costs 0 dollars to host and maintain
5.  ✅ Provides it's administrator with a simple workflow to create, approve and publish blog posts from other contributors
6.  ✅ Provides me with a fun side project to contirbute to in my spare time

See example here: www.docsie.io/blog/

# Quick start

#### 1. Clone the project and enter


    git clone https://github.com/LikaloLLC/BlogVi.git
    cd BlogVi


or

    git clone git@github.com:LikaloLLC/BlogVi.git
    cd BlogVi

#### 2. create virtual environment


Linux OS(Ubuntu)


    python3 -m venv venv


Windows OS

    virtualenv venv

#### 3. Activate environment

Linux OS(Ubuntu)

    source venv/bin/activate

Windows OS

    venv\Scripts\activate

#### 4. Install requirements

Linux OS(Ubuntu)

    pip3 install -r requirements.txt

Windows OS

    pip install -r requirements.txt

#### 5. Run the `2_generate.py` file

Linux OS(Ubuntu)

    python3 2_generate.py

Windows OS

    python 2_generate.py

#### 6. Open index.html file in browser

