from google.cloud import firestore
from credentials import Credentials
import streamlit as st
from fuzzywuzzy import fuzz


class Firestore(Credentials):
    def __init__(self):
        super().__init__()
        try:
            self.client = firestore.Client(
                credentials=self.Firestore_credentials)
        except Exception as e:
            st.error(
                f"""
                ### Error: Invalid credentials.
                - Error Code: 4x000
                - There may be issues with Firestore API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def get_all_reviews(self):
        try:
            reviews_ref = self.client.collection("user_reviews")
            reviews = self._get_reviews(reviews_ref)
            return reviews
        except Exception as e:
            st.error(
                f"""
                ### Error: Failed to retrieve reviews.
                - Error Code: 4x001
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None

    def _get_reviews(self, reviews_ref):
        try:
            reviews = []
            for review in reviews_ref.stream():
                reviews.append(review.to_dict())
            return reviews
        except Exception as e:
            st.error(
                f"""
                ### Error: Failed to retrieve reviews.
                - Error Code: 4x002
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None

    def create_new_review(self, review, landmark, coordinates, score, username):
        try:
            reviews_ref = self.client.collection("user_reviews")
            self._create_review(
                reviews_ref, review, landmark, coordinates, score, username
            )
        except Exception as e:
            st.error(
                f"""
                ### Error: Failed to save new review.
                - Error Code: 4x003
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )

    def _create_review(
        self, reviews_ref, review, landmark, coordinates, score, username
    ):
        try:
            review_data = {
                "Username": username,
                "Landmark": landmark,
                "Coordinates": coordinates,
                "Score10": score,
                "Review": review,
            }
            reviews_ref.document().set(review_data)
        except Exception as e:
            st.error(
                f"""
                ### Error: Failed to save new review.
                - Error Code: 4x004
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )

    def get_review_for_landmark(self, long, lat, accuracy_range, landmark_name):
        try:
            reviews_ref = self.client.collection("user_reviews")
            reviews = self._get_reviews_for_landmark(
                reviews_ref, long, lat, accuracy_range, landmark_name
            )
            return reviews
        except Exception as e:
            st.error(
                f"""
                ### Error: Failed to retrieve reviews for landmark.
                - Error Code: 4x005
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None

    def _get_reviews_for_landmark(
        self, reviews_ref, long, lat, accuracy_range, landmark_name
    ):
        try:
            reviews = []
            for review in reviews_ref.stream():
                review_data = review.to_dict()
                if (
                    float(review_data["Coordinates"].split("/")[0])
                    <= long + accuracy_range
                    and float(review_data["Coordinates"].split("/")[0])
                    >= long - accuracy_range
                    and float(review_data["Coordinates"].split("/")[1])
                    <= lat + accuracy_range
                    and float(review_data["Coordinates"].split("/")[1])
                    >= lat - accuracy_range
                    or fuzz.ratio(review_data["Landmark"], landmark_name) >= 80
                ):
                    reviews.append(review_data)
            if reviews:
                return reviews
            return None
        except Exception as e:
            st.error(
                f"""
                ### Error: Failed to retrieve reviews for landmark.
                - Error Code: 4x006
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None
