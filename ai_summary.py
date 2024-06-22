# # NOTE: This file contains the AI_LLM class which is used to generate a summary about the landmark detected using the OpenAI API.
import pickle
import streamlit as st
from together import Together
import time
from credentials import Credentials


class MockOpenAI_LLM:
    def __init__(self):
        pass

    def generate_summary(self, prompt):
        summary = """
        The Maiden Tower is a 12th-century monument in the Old City, Baku, Azerbaijan. Along with the Shirvanshahs' Palace, dated to the 15th century, it forms a group of historic monuments listed in 2001 under the UNESCO World Heritage List of historical monuments as cultural property, Category III. It is one of the most prominent national and cultural symbols of Azerbaijan.
        """
        return summary

    def stream_summary(self, prompt):
        summary = """
        The Maiden Tower is a 12th-century monument in the Old City, Baku, Azerbaijan. Along with the Shirvanshahs' Palace, dated to the 15th century, it forms a group of historic monuments listed in 2001 under the UNESCO World Heritage List of historical monuments as cultural property, Category III. It is one of the most prominent national and cultural symbols of Azerbaijan.
        """
        for s in summary:
            yield s
            time.sleep(0.06)

    def summarize_review(self, review):
        summary = """
        The food was delicious and the service was excellent. I would definitely recommend this restaurant to my friends and family.
        """
        return summary


class AI_Summary(Credentials):
    def __init__(self):
        super().__init__()

    @st.cache_data(show_spinner=False)
    def generate_summary(_self, prompt):
        try:
            client = Together(api_key=_self.TogetherAI_credentials)
            summary = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=[{"role": "user", "content": prompt}],
            )
            response = summary.choices[0].message.content
            print("Cache miss: generate_summary")
            return response
        except Exception as e:
            st.error(
                f"""
                ### Error: LLM Based Summary could not be generated.
                - Error Code: 5x000
                - There may be issues with OpenAI API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def stream_summary(_self, prompt):
        try:
            client = Together(api_key=_self.TogetherAI_credentials)
            messages = [
                {
                    "role": "system",
                    "content": "Your job is provide, short, concise, and informative summary about the landmark.",
                },
                {"role": "user", "content": prompt},
            ]
            summary = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=messages,
                stream=True,
            )
            for s in summary:
                yield s.choices[0].text
                time.sleep(0.07)
        except Exception as e:
            st.error(
                f"""
                ### Error: LLM Based Summary could not be generated.
                - Error Code: 5x001
                - There may be issues with OpenAI API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    @st.cache_data(show_spinner=False)
    def summarize_review(_self, review):
        try:
            client = Together(api_key=_self.TogetherAI_credentials)
            summary = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=[
                    {
                        "role": "system",
                        "content": """Your job is to summarize the reviews for a given landmark.
                        You must focus on the reviews and extract as much info as possible and analyze the reviews
                        to write a conclusion with upsides and downsides of the landmark with some key points.""",
                    },
                    {"role": "user", "content": review},
                ],
            )
            response = summary.choices[0].message.content
            return response
        except Exception as e:
            st.error(
                f"""
                ### Error: LLM Based Summary could not be generated.
                - Error Code: 5x002
                - There may be issues with OpenAI API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()
