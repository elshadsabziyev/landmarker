# NOTE: This file contains the GoogleCloudVision class which is used to perform landmark detection on an image using the Google Cloud Vision API.

# Import necessary libraries
import pickle
import streamlit as st
from google.cloud import vision
from credentials import Credentials

class GoogleCloudVision(Credentials):
    # Class definitions
    """
    The GoogleCloudVision class is a child class of the Credentials class.
    It uses the credentials object to authenticate with the Google Cloud Vision API.
    It also uses the client object to perform landmark detection on an image.
    """

    def __init__(self):
        """
        Initialize the GoogleCloudVision class.
        This class is a child of the Credentials class, so we call the constructor of the parent class.
        """
        super().__init__()

        # Initialize a client for the Google Cloud Vision API
        # We authenticate with the API using the credentials object created in the parent class
        try:
            self.client = vision.ImageAnnotatorClient(credentials=self.GCP_credentials)
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Invalid credentials.
                - Error Code: 0x002
                - There may be issues with Google Cloud Vision API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def find_landmark(self, image_data):
        """
        Detect landmarks in an image using the Google Cloud Vision API.

        Parameters:
        image_data (bytes): The image data to analyze.

        Returns:
        landmarks (list): A list of detected landmarks.
        """
        # Load the image data into memory
        image = self._load_image(image_data)

        # Perform landmark detection on the image
        # The response is a list of detected landmarks
        landmarks = self._detect_landmarks(image)
        return landmarks

    def _load_image(self, image_data):
        """
        Load the image data into memory.

        Parameters:
        image_data (bytes): The image data to load.

        Returns:
        image (vision.Image): The loaded image.
        """
        try:
            image_data.seek(0)
            image = vision.Image(content=image_data.read())
            return image
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Invalid image.
                - Error Code: 0x003
                - Please make sure you have uploaded a valid image.
                - Please make sure the image is in one of the supported formats (png, jpg, jpeg, webp).
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def _detect_landmarks(self, image):
        """
        Detect landmarks in an image using the Google Cloud Vision API.

        Parameters:
        image (vision.Image): The image to analyze.

        Returns:
        landmarks (list): A list of detected landmarks.
        """
        try:
            response = self.client.landmark_detection(image=image)
            landmarks = response.landmark_annotations
            return landmarks
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Landmark detection failed.
                - Error Code: 0x004
                - There may be issues with Google Cloud Vision API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()


class MockGoogleCloudVision:  # DO NOT USE THIS CLASS UNLESS YOU ARE TESTING THE APP
    # Class definitions
    """
    The MockGoogleCloudVision class is a child class of the Credentials class.
    Unlike the GoogleCloudVision class, it does not use the credentials object to authenticate with the Google Cloud Vision API.
    So, it can be used to test the app without having to authenticate with the API.
    Default response is loaded from a pickle file (response.pkl)
    This response is a mock response that is created using the Google Cloud Vision API.
    It contains the the response for an image of (Maiden Tower, Baku, Azerbaijan)
    It uses a mock response to simulate the detection of landmarks in an image.
    """

    def __init__(self):
        """
        Initialize the MockGoogleCloudVision class.
        This class is a child of the Credentials class, so we call the constructor of the parent class.
        """
        pass

    def find_landmark(self, image_data):
        """
        Mock method to simulate the detection of landmarks in an image.

        Parameters:
        image_data (bytes): The image data to analyze.

        Returns:
        landmarks (list): A list of detected landmarks.
        """
        # Load the mock response from a pickle file
        response = self._load_mock_response()

        # Extract the landmarks from the mock response
        landmarks = response.landmark_annotations
        return landmarks

    def _load_mock_response(self):
        """
        Load the mock response from a pickle file.

        Returns:
        response (object): The loaded mock response.
        """
        with open("response.pkl", "rb") as f:
            response = pickle.load(f)
        return response
