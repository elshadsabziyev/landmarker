# NOTE: This file contains the OpenAI_LLM class which is used to generate a summary about the landmark detected using the OpenAI API.

# Import necessary libraries
import pickle
import streamlit as st
import openai
import time
from credentials import Credentials

class OpenAI_LLM(Credentials):
    # Class definitions
    """
    The LLM_Summary class is a child class of the Credentials class.
    It uses the credentials object to authenticate with the OpenAI API.
    It uses the OpenAI API to generate a summary about the landmark detected.
    """

    def __init__(self):
        """
        Initialize the LLM_Summary class.
        This class is a child of the Credentials class, so we call the constructor of the parent class.
        """
        super().__init__()

    def generate_summary(self, prompt):
        """
        Generate a summary about the landmark detected using the OpenAI API.

        Parameters:
        prompt (str): The prompt to generate the summary.

        Returns:
        summary (str): The generated summary.
        """
        try:
            openai.api_key = self.OpenAI_credentials
            summary = openai.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=150,
            )
            response = summary.choices[0].message.content
            return response
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: LLM Based Summary could not be generated.
                - Error Code: 0x018
                - There may be issues with OpenAI API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def stream_summary(self, prompt):
        """
        Generate a summary about the landmark detected using the OpenAI API.
        Unlike the generate_summary method, this method is used to stream the summary to the app.

        Parameters:
        prompt (str): The prompt to generate the summary.

        Returns:
        summary (OpenAI Stream): The generated summary.
        """
        try:
            openai.api_key = self.OpenAI_credentials
            summary = openai.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=150,
                stream=True,
            )
            for s in summary:
                yield s
                time.sleep(0.06)
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: LLM Based Summary could not be generated.
                - Error Code: 0x018
                - There may be issues with OpenAI API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()


class MockOpenAI_LLM:
    # Class definitions
    """
    The MockOpenAI_LLM class is a child class of the Credentials class.
    Unlike the OpenAI_LLM class, it does not use the credentials object to authenticate with the OpenAI API.
    So, it can be used to test the app without having to authenticate with the API.
    It uses a mock response to simulate the generation of a summary about the landmark detected.
    """

    def __init__(self):
        """
        Initialize the MockOpenAI_LLM class.
        This class is a child of the Credentials class, so we call the constructor of the parent class.
        """
        pass

    def generate_summary(self, prompt):
        """
        Mock method to simulate the generation of a summary about the landmark detected.

        Parameters:
        prompt (str): The prompt to generate the summary.

        Returns:
        summary (str): The generated summary.
        """
        # Load the mock response from a pickle file
        response = self._load_mock_response()

        # Extract the summary from the mock response
        summary = response
        return summary

    def _load_mock_response(self):
        """
        Load the mock response from a pickle file.

        Returns:
        response (object): The loaded mock response.
        """
        with open("summary.pkl", "rb") as f:
            response = pickle.load(f)
        return response

