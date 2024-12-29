# Authentication and Organization Design

## Overview

This document outlines the authentication and organization management design using Logto as the identity provider. The system supports multi-tenancy through Logto's organization features while maintaining a clean separation between authentication and application data.

## Authentication Flow

1. **Initial Login**
   - User clicks "Authorize" button
   - Redirected to Logto login page
   - Upon successful authentication:
     - Receive ID token and access token
     - Decode ID token to get user information
     - Fetch user's organizations from Logto
     - Create default organization if none exists

2. **Session Management**
   ```python
   st.session_state.user_info        # Stores current user information
   st.session_state.organizations    # List of user's organizations
   st.session_state.active_organization  # Currently selected organization
   ```

## Organization Management

### Logto Integration

1. **Organization Creation**
   ```python
   # Automatic organization creation for new users
   if not user_organizations:
       tenant_id = str(uuid.uuid4())
       organization_name = f'{user_in_idp.name}\'s organization'
       organization_in_idp = idp_organization_service.create(tenant_id, organization_name)
       idp_organization_service.add_members(organization_in_idp.id, [user_in_idp.id])
   ```

2. **Organization Access**
   ```python
   # Fetch user's organizations
   user_organizations = idp_organization_service.organizations_of_user(user_in_idp.id)
   ```

### Database Schema

1. **User Table**
   ```sql
   create table if not exists users (
       id uuid primary key default uuid_generate_v4(),
       logto_id text not null unique,
       email text not null,
       name text not null,
       created_at timestamptz not null default now(),
       updated_at timestamptz not null default now()
   );
   ```

2. **Organization-Scoped Tables**
   ```sql
   -- Example of organization-scoped table
   create table if not exists posts (
       id uuid primary key default uuid_generate_v4(),
       logto_organization_id text not null,
       -- other fields...
   );
   ```

### Multi-tenancy Implementation

1. **Organization Selection**
   ```python
   # Sidebar organization selector
   if len(st.session_state.organizations) > 1:
       org_names = [org.name for org in st.session_state.organizations]
       selected_org_idx = st.sidebar.selectbox(
           "Organization",
           range(len(org_names)),
           format_func=lambda x: org_names[x]
       )
       st.session_state.active_organization = st.session_state.organizations[selected_org_idx]
   ```

2. **Data Scoping**
   ```python
   # Repository pattern for organization scoping
   def list_items(self, filters: Optional[dict] = None) -> List[dict]:
       query = self._supabase.table(TABLE_NAME).select("*")
       
       # Always filter by current organization
       org_id = st.session_state.active_organization.id
       query = query.eq('logto_organization_id', org_id)
       
       # Apply additional filters
       if filters:
           # ... apply other filters ...
       
       return query.execute().data
   ```

## Security Considerations

1. **Organization Access**
   - All database queries must include organization_id filter
   - Organization ID comes from Logto token/session
   - Never accept organization ID from client input

2. **User Sessions**
   - Token refresh handled automatically
   - Session state includes current organization
   - Organization switch requires re-fetching data

3. **Data Isolation**
   - Each table includes logto_organization_id
   - Queries always scoped to current organization
   - Foreign key constraints within organization scope

## Best Practices

1. **Organization Setup**
   - Create default organization for new users
   - Allow organization switching in UI
   - Store minimal organization data locally

2. **Data Access**
   - Use repository pattern for data access
   - Always include organization scope in queries
   - Validate organization access in services

3. **UI/UX**
   - Show current organization in UI
   - Provide clear organization switching
   - Indicate organization-specific content

## Implementation Example

```python
# Service layer
class BaseService:
    def get_current_organization_id(self) -> str:
        return st.session_state.active_organization.id

    def validate_organization_access(self, org_id: str) -> bool:
        return org_id in [org.id for org in st.session_state.organizations]

# Repository layer
class BaseRepository:
    def apply_organization_filter(self, query: Any) -> Any:
        org_id = st.session_state.active_organization.id
        return query.eq('logto_organization_id', org_id)

# Usage in specific repository
class PostRepository(BaseRepository):
    def list_posts(self, filters: Optional[dict] = None) -> List[dict]:
        query = self._supabase.table('posts').select("*")
        query = self.apply_organization_filter(query)
        
        if filters:
            # Apply additional filters
            pass
            
        return query.execute().data
```

## Migration Considerations

When implementing this design in existing projects:

1. Add `logto_organization_id` to existing tables
2. Migrate existing data to default organizations
3. Update repositories to include organization filtering
4. Add organization selection to UI
5. Test data isolation between organizations
