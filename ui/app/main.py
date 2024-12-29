import uuid
import streamlit as st
from dependency_injector.wiring import Provide, inject
from extra_streamlit_components import CookieManager
from httpx_oauth.oauth2 import RefreshTokenError

from di_container import Container
from domain.model.iam import IIdpOrganizationService, IIdpUserService, ITokenService, UserId
from infrastructure.service.oauth import OAuth2ComponentAdapter
from infrastructure.service.user import UserService

st.set_page_config(
    page_title="BlogVi Manager",
    page_icon="🚀",
    layout="wide"
)

cookie = CookieManager(key='cookies')
LOGTO_TOKEN_COOKIE = 'logto_token'

@inject
def check_token_on_user_interaction(
    oauth2_component_adapter: OAuth2ComponentAdapter = Provide['oauth2_component_adapter'],
):
    if cookie.get_all():
        try:
            token = cookie.get(LOGTO_TOKEN_COOKIE)
            if token:
                new_token = oauth2_component_adapter.refresh_token(token)
                if token != new_token:
                    cookie.set(LOGTO_TOKEN_COOKIE, new_token)
        except RefreshTokenError:
            cookie.delete(LOGTO_TOKEN_COOKIE)
            st.session_state.user_info = {}

@inject
def set_user_if_token_exists(
    token_service: ITokenService = Provide['token_service'],
    idp_user_service: IIdpUserService = Provide['idp_user_service'],
    idp_organization_service: IIdpOrganizationService = Provide['idp_organization_service'],
):
    if cookie.get_all():
        try:
            token = cookie.get(LOGTO_TOKEN_COOKIE)
            if token:
                id_token = token_service.decode_id_token(token['id_token'])
                user_in_idp = idp_user_service.get_by_id(UserId(id_token.sub))
                st.session_state.user_info = user_in_idp
                
                # Load user organizations
                user_organizations = idp_organization_service.organizations_of_user(user_in_idp.id)
                st.session_state.user_organizations = user_organizations
                
                st.rerun()
        except Exception:
            st.session_state.user_info = {}
            st.session_state.user_organizations = []
            cookie.delete(LOGTO_TOKEN_COOKIE)

@inject
def login_oauth(
    oauth2_component_adapter: OAuth2ComponentAdapter = Provide['oauth2_component_adapter'],
    idp_user_service: IIdpUserService = Provide['idp_user_service'],
    idp_organization_service: IIdpOrganizationService = Provide['idp_organization_service'],
    token_service: ITokenService = Provide['token_service'],
    user_service: UserService = Provide['user_service'],
):
    st.markdown('# Sign in to BlogVi Manager\nWelcome! Please authorize to continue\n\n')

    oauth_info = oauth2_component_adapter.authorize_button(
        'Authorize',
        scope=('profile offline_access openid email roles '
               'urn:logto:scope:organizations urn:logto:scope:organization_roles')
    )

    if oauth_info:
        id_token = token_service.decode_id_token(oauth_info['token']['id_token'])
        user_in_idp = idp_user_service.get_by_id(UserId(id_token.sub))
        st.session_state.user_info = user_in_idp

        user_organizations = idp_organization_service.organizations_of_user(user_in_idp.id)
        if not user_organizations:
            tenant_id = str(uuid.uuid4())
            organization_name = f'{user_in_idp.name}\'s organization'

            organization_in_idp = idp_organization_service.create(tenant_id, organization_name)
            idp_organization_service.add_members(organization_in_idp.id, [user_in_idp.id])

        st.session_state.user = user_service.get_or_create(customer_id=user_in_idp.id)
        cookie.set(LOGTO_TOKEN_COOKIE, oauth_info['token'], key='set_access_token')

def main():
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}

    # with open('./media/base.css') as f:
    #     base_css = f.read()
    # st.markdown(f'<style>{base_css}</style>', unsafe_allow_html=True)

    if not st.session_state.user_info:
        login_oauth()
        return

    # with open('./media/page.css') as f:
    #     page_css = f.read()
    # st.markdown(f'<style>{page_css}</style>', unsafe_allow_html=True)

    st.sidebar.title("Blog Management")
    menu = ["Posts", "Categories", "Authors", "Settings"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Posts":
        from routes.posts import main as posts_main
        posts_main()
    elif choice == "Categories":
        from routes.categories import main as categories_main
        categories_main()
    elif choice == "Authors":
        from routes.authors import main as authors_main
        authors_main()
    elif choice == "Settings":
        from routes.settings import main as settings_main
        settings_main()

if __name__ == "__main__":
    container = Container()
    container.init_resources()
    container.wire(modules=[__name__, 'routes.posts', 'routes.categories', 'routes.authors', 'routes.settings'])
    main() 