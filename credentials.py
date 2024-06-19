# NOTE: This file contains the Credentials class which is used to authenticate with the Google Cloud Vision API and TogetherAI API.

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
        self.GCP_credentials = self.get_VertexAI_credentials_from_secrets()
        self.Firestore_credentials = self.get_Firestore_credentials_from_secrets()
        self.TogetherAI_credentials = st.secrets["TogetherAI"]["api_key"]

    def get_Firestore_credentials_from_secrets(self):
        """
        Extracts the credentials from Streamlit secrets and creates a credentials object.
        This object will be used to authenticate with the Google Cloud Vision API.

        Returns:
        credentials (service_account.Credentials): The credentials object.
        """
        try:
            credentials_dict = {
                "type": st.secrets["Firestore"]["type"],
                "project_id": st.secrets["Firestore"]["project_id"],
                "private_key_id": st.secrets["Firestore"]["private_key_id"],
                "private_key": st.secrets["Firestore"]["private_key"],
                "client_email": st.secrets["Firestore"]["client_email"],
                "client_id": st.secrets["Firestore"]["client_id"],
                "auth_uri": st.secrets["Firestore"]["auth_uri"],
                "token_uri": st.secrets["Firestore"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["Firestore"][
                    "auth_provider_x509_cert_url"
                ],
                "client_x509_cert_url": st.secrets["Firestore"]["client_x509_cert_url"],
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
                - There may be issues with Google Cloud Vision API or TogetherAI API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def get_VertexAI_credentials_from_secrets(self):
        """
        Extracts the credentials from Streamlit secrets and creates a credentials object.
        This object will be used to authenticate with the Google Cloud Vision API.

        Returns:
        credentials (service_account.Credentials): The credentials object.
        """
        try:
            credentials_dict = {
                "type": st.secrets["VertexAI"]["type"],
                "project_id": st.secrets["VertexAI"]["project_id"],
                "private_key_id": st.secrets["VertexAI"]["private_key_id"],
                "private_key": st.secrets["VertexAI"]["private_key"],
                "client_email": st.secrets["VertexAI"]["client_email"],
                "client_id": st.secrets["VertexAI"]["client_id"],
                "auth_uri": st.secrets["VertexAI"]["auth_uri"],
                "token_uri": st.secrets["VertexAI"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["VertexAI"][
                    "auth_provider_x509_cert_url"
                ],
                "client_x509_cert_url": st.secrets["VertexAI"]["client_x509_cert_url"],
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
                - There may be issues with Google Cloud Vision API or TogetherAI API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()
