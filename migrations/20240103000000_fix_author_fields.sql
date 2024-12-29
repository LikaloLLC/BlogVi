-- First drop existing constraints
ALTER TABLE blogvi_post_collaborators
    DROP CONSTRAINT IF EXISTS blogvi_post_collaborators_post_id_fkey,
    ALTER COLUMN post_id DROP NOT NULL,
    ALTER COLUMN email DROP NOT NULL,
    ALTER COLUMN user_id DROP NOT NULL;

-- Make only name mandatory
ALTER TABLE blogvi_post_collaborators
    ALTER COLUMN name SET NOT NULL;

-- Drop old unique constraint if exists (post_id, email)
ALTER TABLE blogvi_post_collaborators
    DROP CONSTRAINT IF EXISTS blogvi_post_collaborators_post_id_email_key;

-- Add new unique constraint only if both post_id and email are present
CREATE UNIQUE INDEX IF NOT EXISTS blogvi_post_collaborators_post_email_idx 
    ON blogvi_post_collaborators (post_id, email) 
    WHERE post_id IS NOT NULL AND email IS NOT NULL;

-- Update role check constraint
ALTER TABLE blogvi_post_collaborators
    DROP CONSTRAINT IF EXISTS blogvi_post_collaborators_role_check,
    ADD CONSTRAINT blogvi_post_collaborators_role_check 
    CHECK (role IN ('author', 'editor', 'reviewer', 'viewer'));

-- Add missing columns to posts table
ALTER TABLE blogvi_posts
    ADD COLUMN IF NOT EXISTS excerpt text,
    ADD COLUMN IF NOT EXISTS header_image text,
    ADD COLUMN IF NOT EXISTS hero_image text,
    ADD COLUMN IF NOT EXISTS slug text,
    ADD COLUMN IF NOT EXISTS legacy_slugs text[] DEFAULT array[]::text[],
    ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb;

-- Make organization optional in posts
ALTER TABLE blogvi_posts
    ALTER COLUMN logto_organization_id DROP NOT NULL;

-- Update slug constraint
ALTER TABLE blogvi_posts
    DROP CONSTRAINT IF EXISTS blogvi_posts_slug_key;
ALTER TABLE blogvi_posts
    ADD CONSTRAINT blogvi_posts_slug_key UNIQUE (slug); 