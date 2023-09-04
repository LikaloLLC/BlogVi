# BlogVi - Tailwind Static Blog with Search (Backendless)
 by [Docsie](https://www.docsie.io)
 
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

# Installation

#### 1. Install the package:

```shell
    pip install git+https://github.com/LikaloLLC/BlogVi
```

#### 2. Create a folder for the blog:

```shell
    mkdir blog
    cd blog
```
    

#### 3. Create a settings file:

**Note:** `1_settings.yaml` is the required filename.

```shell
    touch 1_settings.yaml
```

#### 4. Fill the settings:

```yaml
# mandatory
blog_name: "Docsie.io Blog"
blog_post_location_url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vR2Unb1VTOB1upja915Rp7N6MJnqtLLOPYUlrJW7R0qybH_kGWB1wPozgjAf6X5JD-Bv_XldO9yKSLU/pub?output=csv"
domain_url: "https://www.docsie.io/"
blog_root_url: "blog/"

# optional
link_menu:
  - link: "https://www.docsie.io"
    text: "Docsie"
  - link: "https://www.docsie.io/pricing/"
    text: "Docsie Pricing"
  - link: "https://www.docsie.io/try_docsie/"
    text: "Try Docsie"

search_config:
  title:
    weight: 8
  summary:
    weight: 6
  author_name:
    weight: 5
  categories:
    weight: 3

comments:
  enabled: true
  commentbox_project_id: "5725910686760960-proj"

subscribe:
  enabled: true
  title: "Subscribe to the newsletter"
  summary: "Stay up to date with our latest news and products"
  button_text: "Subscribe"

sharect:
  enabled: true
  twitter: true
  facebook: true
  twitterUsername: ""
  backgroundColor: "#333333"
  iconColor: "#FFFFFF"
  selectableElements:
    - body

landing_meta:
  title: ""
  description: ""
  image: ""
  keywords: ""
  url: ""
  author: ""

```

#### 4. Generate your awesome blog:

```shell
    blogvi .
```

### 5. Open `index.html` file in browser

# Settings

## Mandatory

***blog_name***  
    The name of the blog, which will be shown on the home page.

***blog_post_location_url***  
    A URL to the CSV table, containing content and meta of all articles.

***domain_url***  
    Domain name. Used in generating internal links.

***blog_root_url***  
    Blog path under the specified domain. Used in generating internal links.

## Optional

***link_menu***  
    The list of external links in the header and footer

***search_config***  
    The search config.  
    Each key is an article field name, and wight gives them higher (or lower) values in search results.

***comments***  
    Enable or disable comment system on the blog. It uses [commentbox](https://commentbox.io/) as a provider.  
    You need to provide `commentbox_project_id`, available after registration a project,
in order to enable this functionality.

***google_tag_manager***  
    Enable or disable [Google Tag Manager](https://marketingplatform.google.com/about/tag-manager/) on the blog. This is handy if you have lots of marketing, analytics and other tags that you need to add to your blog. 
You need to provide `google_tag_manager_projectid`, which you can get [by following this guide](https://support.google.com/tagmanager/answer/6103696?hl=en),in order to enable this functionality.


***subscribe***  
    Enable or disable "subscribe to the newsletter" form.

***sharect***  
    Enable or disable sharing system. Uses [sharect](https://estevanmaito.github.io/sharect/) as a provider.  
    It mirrors settings from sharect.

***landing_meta***  
    Meta info for the blog.