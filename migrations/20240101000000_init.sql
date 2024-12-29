-- Enable necessary extensions
create extension if not exists "uuid-ossp";

-- Create posts table
create table if not exists blogvi_posts (
    id uuid primary key default uuid_generate_v4(),
    title text not null,
    content text not null,
    status text not null default 'draft',
    excerpt text,
    categories text[] default array[]::text[],
    hero_image text,
    header_image text,
    slug text unique,
    legacy_slugs text[] default array[]::text[],
    metadata jsonb,
    logto_organization_id text not null,
    created_by_id text not null,
    updated_by_id text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Create categories table
create table if not exists blogvi_categories (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    description text,
    logto_organization_id text not null,
    created_by_id text not null,
    updated_by_id text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(name, logto_organization_id)
);

-- Create post_collaborators table for tracking authors and other collaborators
create table if not exists blogvi_post_collaborators (
    id uuid primary key default uuid_generate_v4(),
    post_id uuid not null references blogvi_posts(id),
    logto_user_id text,  -- Optional link to LogTO user
    role text not null check (role in ('author', 'editor', 'reviewer', 'viewer')),
    name text not null,  -- Author/collaborator name
    email text not null,  -- Author/collaborator email
    avatar_url text,     -- Profile picture URL
    bio text,           -- About the author/collaborator
    social_urls text[], -- Array of social media URLs
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique(post_id, email)  -- Changed from user_id to email for uniqueness
);

-- Create indexes
create index if not exists blogvi_posts_status_idx on blogvi_posts(status);
create index if not exists blogvi_posts_created_at_idx on blogvi_posts(created_at);
create index if not exists blogvi_posts_organization_id_idx on blogvi_posts(logto_organization_id);
create index if not exists blogvi_posts_categories_idx on blogvi_posts using gin(categories);
create index if not exists blogvi_categories_organization_id_idx on blogvi_categories(logto_organization_id);
create index if not exists blogvi_post_collaborators_post_id_idx on blogvi_post_collaborators(post_id);
create index if not exists blogvi_post_collaborators_email_idx on blogvi_post_collaborators(email);
create index if not exists blogvi_post_collaborators_logto_user_id_idx on blogvi_post_collaborators(logto_user_id);
create index if not exists blogvi_post_collaborators_role_idx on blogvi_post_collaborators(role);

-- Create functions
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Create triggers
create trigger handle_updated_at_blogvi_posts
    before update on blogvi_posts
    for each row
    execute procedure handle_updated_at();

create trigger handle_updated_at_blogvi_categories
    before update on blogvi_categories
    for each row
    execute procedure handle_updated_at();

create trigger handle_updated_at_blogvi_post_collaborators
    before update on blogvi_post_collaborators
    for each row
    execute procedure handle_updated_at(); 