-- Modify post_collaborators table to include author fields
ALTER TABLE blogvi_post_collaborators
    ADD COLUMN IF NOT EXISTS name text,
    ADD COLUMN IF NOT EXISTS email text,
    ADD COLUMN IF NOT EXISTS avatar_url text,
    ADD COLUMN IF NOT EXISTS bio text,
    ADD COLUMN IF NOT EXISTS social_urls text[] DEFAULT array[]::text[];

-- Make name and email required
ALTER TABLE blogvi_post_collaborators
    ALTER COLUMN name SET NOT NULL,
    ALTER COLUMN email SET NOT NULL;

-- Add indexes
CREATE INDEX IF NOT EXISTS blogvi_post_collaborators_email_idx ON blogvi_post_collaborators(email);
CREATE INDEX IF NOT EXISTS blogvi_post_collaborators_role_idx ON blogvi_post_collaborators(role);

-- Update role check constraint to include author role
ALTER TABLE blogvi_post_collaborators
    DROP CONSTRAINT IF EXISTS blogvi_post_collaborators_role_check,
    ADD CONSTRAINT blogvi_post_collaborators_role_check 
    CHECK (role IN ('author', 'editor', 'reviewer', 'viewer')); 