import streamlit as st
from dependency_injector.wiring import inject, Provide

from infrastructure.service.user import UserService
from infrastructure.service.chargebee import ChargebeeService
from domain.service.credits import ICreditsService


@inject
def main(
    user_service: UserService = Provide['user_service'],
    chargebee_service: ChargebeeService = Provide['chargebee_service'],
    credits_service: ICreditsService = Provide['credits_service']
):
    st.markdown(f'''
        # Tool settings
        ''')
    
    # API Key Settings
    st.subheader("API Settings")
    with st.form(key='api_form'):
        text_input = st.text_input(label='Docsie API Key', value=st.session_state.user['docsie_api_key'])
        submit = st.form_submit_button(label='Save API Key')

        if submit:
            user = user_service.update(st.session_state.user['customer_id'], text_input)
            st.session_state.user = user.data[0]
            st.success("API Key updated successfully!")

    st.markdown("## Credits Management")
    customer_credits = credits_service.retrieve(st.session_state.chargebee_customer.id)
    if customer_credits.data:
        minutes = customer_credits.data[0]['minutes']
        st.write(f"Available Credits: {minutes} minutes")
    else:
        st.write("Available Credits: 0 minutes") 