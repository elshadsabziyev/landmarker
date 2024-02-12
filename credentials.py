# NOTE: This file contains the Credentials class which is used to authenticate with the Google Cloud Vision API and OpenAI API.

# Import necessary libraries
import streamlit as st
from google.oauth2 import service_account


class Credentials:
    # Class definitions
    """
    The Credentials class is the parent class of the GoogleCloudVision and MockGoogleCloudVision classes.
    It gets the credentials from Streamlit secrets and creates a credentials object.
    """

    def __init__(self):
        """
        Initialize the Credentials class.
        """
        # Create a credentials dictionary using Streamlit secrets
        # These secrets are used to authenticate with the Google Cloud Vision API
        self.GCP_credentials = self.get_credentials_from_secrets()
        self.OpenAI_credentials = st.secrets["openai_api_key"]

    def get_credentials_from_secrets(self):
        """
        Extracts the credentials from Streamlit secrets and creates a credentials object.
        This object will be used to authenticate with the Google Cloud Vision API.

        Returns:
        credentials (service_account.Credentials): The credentials object.
        """
        try:
            credentials_dict = {
                "type": st.secrets["type"],
                "project_id": st.secrets["project_id"],
                "private_key_id": st.secrets["private_key_id"],
                "private_key": st.secrets["private_key"],
                "client_email": st.secrets["client_email"],
                "client_id": st.secrets["client_id"],
                "auth_uri": st.secrets["auth_uri"],
                "token_uri": st.secrets["token_uri"],
                "auth_provider_x509_cert_url": st.secrets[
                    "auth_provider_x509_cert_url"
                ],
                "client_x509_cert_url": st.secrets["client_x509_cert_url"],
            }
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict
            )
            return credentials
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Invalid credentials.
                - Error Code: 0x001
                - There may be issues with Google Cloud Vision API or OpenAI API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()
