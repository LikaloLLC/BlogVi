from dependency_injector import containers, providers
from supabase import create_client

from infrastructure.service.iam import LogtoAPIClient, LogtoOrganizationService, LogtoUserService, TokenService
from infrastructure.service.oauth import LogtoOauth2ComponentAdapter
from infrastructure.service.user import UserService
from infrastructure.service.blog import BlogService
from infrastructure.service.chargebee import ChargebeeService
from infrastructure.service.credits import CreditsService
from repositories.blog import BlogSupabaseRepository
from repositories.user import UserSupabaseRepository
from repositories.credits import CreditsSupabaseRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Auth configuration
    config.auth.base_url.from_env("AUTH_BASE_URL", as_=str, required=False)
    config.auth.client_id.from_env("AUTH_CLIENT_ID", as_=str, required=False)
    config.auth.client_secret.from_env("AUTH_CLIENT_SECRET", as_=str, required=False)
    config.auth.management_client_id.from_env("AUTH_MANAGEMENT_CLIENT_ID", as_=str, required=False)
    config.auth.management_client_secret.from_env("AUTH_MANAGEMENT_CLIENT_SECRET", as_=str, required=False)
    config.auth.redirect_uri.from_env("AUTH_REDIRECT_URI", as_=str, required=False)
    config.auth.openid_conf_endpoint.from_env("AUTH_OPENID_CONF_ENDPOINT", as_=str, required=False)

    # Supabase configuration
    config.supabase.url.from_env("SUPABASE_URL", as_=str, required=True)
    config.supabase.key.from_env("SUPABASE_KEY", as_=str, required=True)

    # Chargebee configuration
    config.chargebee.api_key.from_env("CHARGEBEE_API_KEY", as_=str, required=False)
    config.chargebee.site.from_env("CHARGEBEE_SITE", as_=str, required=False)

    # Supabase client
    supabase_client = providers.Factory(
        create_client,
        supabase_url=config.supabase.url,
        supabase_key=config.supabase.key,
    )

    # Repositories
    user_repository = providers.Singleton(UserSupabaseRepository, supabase_client=supabase_client)
    blog_repository = providers.Singleton(BlogSupabaseRepository, supabase_client=supabase_client)
    credits_repository = providers.Singleton(CreditsSupabaseRepository, supabase_client=supabase_client)

    # Logto services
    logto_api_client = providers.Singleton(
        LogtoAPIClient,
        base_url=config.auth.base_url,
        client_id=config.auth.management_client_id,
        client_secret=config.auth.management_client_secret,
    )

    idp_user_service = providers.Factory(LogtoUserService, client=logto_api_client)
    idp_organization_service = providers.Factory(LogtoOrganizationService, client=logto_api_client)
    token_service = providers.Factory(TokenService, openid_conf_endpoint=config.auth.openid_conf_endpoint)

    oauth2_component_adapter = providers.Factory(
        LogtoOauth2ComponentAdapter,
        client_id=config.auth.client_id,
        client_secret=config.auth.client_secret,
        redirect_uri=config.auth.redirect_uri,
        base_url=config.auth.base_url,
    )

    # Chargebee service
    chargebee_service = providers.Factory(
        ChargebeeService,
        api_key=config.chargebee.api_key,
        site=config.chargebee.site,
    )

    # Application services
    user_service = providers.Factory(UserService, user_repo=user_repository)
    blog_service = providers.Factory(BlogService, blog_repo=blog_repository)
    credits_service = providers.Factory(CreditsService, credits_repo=credits_repository) 