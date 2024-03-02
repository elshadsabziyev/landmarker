from google.cloud import firestore
from credentials import Credentials
import streamlit as st
from fuzzywuzzy import fuzz


class Firestore(Credentials):
    """
    The Firestore class is the child class of the Credentials class.
    It uses the credentials object to authenticate with the Firestore API.
    It also uses the client object to perform operations on the Firestore database.
    """

    def __init__(self):
        """
        Initialize the Firestore class.
        This class is a child of the Credentials class, so we call the constructor of the parent class.
        """
        super().__init__()
        try:
            self.client = firestore.Client(credentials=self.Firestore_credentials)
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Invalid credentials.
                - Error Code: 100
                - There may be issues with Firestore API.
                - Another possible reason is that credentials you provided are invalid or expired.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def get_all_reviews(self):
        """
        Get all reviews from the Firestore database.

        Returns:
        reviews (list): A list of reviews.
        """
        try:
            reviews_ref = self.client.collection("user_reviews")
            reviews = self._get_reviews(reviews_ref)
            return reviews
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Failed to retrieve reviews.
                - Error Code: 101
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None

    def _get_reviews(self, reviews_ref):
        """
        Get all reviews from the Firestore database.

        Args:
        reviews_ref (firestore.CollectionReference): A reference to the reviews collection.

        Returns:
        reviews (list): A list of reviews.
        """
        try:
            reviews = []
            for review in reviews_ref.stream():
                reviews.append(review.to_dict())
            return reviews
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Failed to retrieve reviews.
                - Error Code: 102
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None

    def create_new_review(self, review, landmark, coordinates, score, username):
        """
        Create a new review in the Firestore database.

        Args:
        review (str): The review text.
        landmark (str): The landmark name.
        coordinates (dict): The coordinates of the landmark.
        score (int): The score of the review.
        username (str): The username of the reviewer. Also used as the document ID.

        Returns:
        None
        """
        try:
            reviews_ref = self.client.collection("user_reviews")
            self._create_review(
                reviews_ref, review, landmark, coordinates, score, username
            )
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Failed to save new review.
                - Error Code: 103
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )

    def _create_review(
        self, reviews_ref, review, landmark, coordinates, score, username
    ):
        """
        Create a new review in the Firestore database.

        Args:
        reviews_ref (firestore.CollectionReference): A reference to the reviews collection.
        review (str): The review text.
        landmark (str): The landmark name.
        coordinates (dict): The coordinates of the landmark.
        score (int): The score of the review.
        username (str): The username of the reviewer. Also used as the document ID.

        Returns:
        None
        """
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
                Error: {e}
                ### Error: Failed to save new review.
                - Error Code: 104
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )

    def get_review_for_landmark(self, long, lat, accuracy_range, landmark_name):
        """
        Get all reviews for a landmark from the Firestore database.

        Args:
        long (float): The longitude of the landmark.
        lat (float): The latitude of the landmark.
        accuracy_range (float): The accuracy range of the landmark.
        landmark_name (str): The name of the landmark.

        Returns:
        reviews (list): A list of reviews.
        """
        try:
            reviews_ref = self.client.collection("user_reviews")
            reviews = self._get_reviews_for_landmark(
                reviews_ref, long, lat, accuracy_range, landmark_name
            )
            return reviews
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Failed to retrieve reviews for landmark.
                - Error Code: 105
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None

    def _get_reviews_for_landmark(
        self, reviews_ref, long, lat, accuracy_range, landmark_name
    ):
        """
        Get all reviews for a landmark from the Firestore database.

        Args:
        reviews_ref (firestore.CollectionReference): A reference to the reviews collection.
        long (float): The longitude of the landmark.
        lat (float): The latitude of the landmark.
        accuracy_range (float): The accuracy range of the landmark.
        landmark_name (str): The name of the landmark.

        Returns:
        reviews (list): A list of reviews.
        """
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
                Error: {e}
                ### Error: Failed to retrieve reviews for landmark.
                - Error Code: 106
                - There may be issues with Firestore API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            return None


def test_firestore():
    """
    Test the Firestore class.
    """
    firestore = Firestore()
    print(firestore.get_all_reviews())
    print(
        firestore.create_new_review(
            "This is a test review",
            "Test Landmark",
            "0.1/0.1",
            5,
            "Test User",
        )
    )
    print(firestore.get_review_for_landmark(0, 0, 0.1, "Test Landmark"))


if __name__ == "__main__":
    test_firestore()
