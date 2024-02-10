# Import necessary libraries
import base64
import pickle
import time
from PIL import Image as Img
from google.cloud import vision
from google.oauth2 import service_account
from geopy.geocoders import Nominatim
import folium
from folium import plugins
import branca.colormap as cm
import requests
import streamlit as st
import streamlit.components.v1 as components
import openai
from streamlit_js_eval import streamlit_js_eval

# Constants
SUPPORTED_FORMATS = ("png", "jpg", "jpeg", "webp")
ACCURACY_HEATMAP_RADIUS = 10
DEFAULT_ZOOM_START = 2
DEFAULT_MOBILE_MAX_WIDTH = 500
DEBUG_MODE_WARNING_ENABLED = False


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
                max_tokens=110,
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
                max_tokens=110,
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


class FoliumMap:
    # Class definitions
    """
    The FoliumMap class is used to create a Folium map.
    It uses the Folium library to create the map.
    It also uses the Nominatim library to get the city and country of a location using its latitude and longitude.
    """

    def __init__(self, zoom_start_=DEFAULT_ZOOM_START):
        """
        Initialize the FoliumMap class.

        Parameters:
        zoom_start (int): Initial zoom level for the map.
        """
        self.max_score_location = [0, 0]
        self.max_score = 0
        self.zoom_start = zoom_start_

        self.map = self._create_initial_map()
        try:
            self.geo_locator = Nominatim(user_agent="landmarker")
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Map could not be created.
                - Error Code: 0x005
                - There may be issues with Geolocataion Provider.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()
        self.colormap = self._create_colormap()

    def _create_initial_map(self):
        """
        Create an initial Folium map centered at the maximum score location.

        Returns:
        map (folium.Map): The created map.
        """
        try:
            return folium.Map(
                location=self.max_score_location, zoom_start=self.zoom_start
            )
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Map could not be created.
                - Error Code: 0x006
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    @staticmethod
    def get_wikipedia_page(landmark):
        """
        Get the correct Wikipedia page for a given landmark.

        Parameters:
        landmark (str): The name of the landmark.

        Returns:
        page_url (str): The URL of the Wikipedia page for the landmark.
        """
        try:
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": landmark,
                },
            ).json()
            if response["query"]["search"]:
                page_title = response["query"]["search"][0]["title"]
                page_url = (
                    f"https://www.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                )
                return page_url
            else:
                return None
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Wikipedia page could not be retrieved.
                - Error Code: 0x021
                - There may be issues with Wikipedia API.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def _create_colormap(self):
        """
        Create a linear color map with white, yellow, and green colors.

        Returns:
        colormap (cm.LinearColormap): The created color map.
        """
        return cm.LinearColormap(
            colors=["white", "yellow", "green"],
            index=[0, 50, 100],
            vmin=0,
            vmax=100,
            caption="Similarity score",
        )

    def get_location_details(self, lat, lon):
        """
        Get the city and country of a location using its latitude and longitude.

        Parameters:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.

        Returns:
        city (str): The city of the location.
        country (str): The country of the location.
        """
        try_count = 0
        try:
            location = self.geo_locator.reverse(f"{lat}, {lon}")
            try_count = 0
        except Exception as e:
            try_count += 1
            if try_count > 2:
                st.error(
                    f"""
                    Error: {e}
                    ### Error: Location details could not be retrieved.
                    - Error Code: 0x007
                    - There may be issues with Geolocataion Provider.
                    - Also if you switching between satellite and normal mode too fast, this error may occur.
                    - Most likely, it's not your fault.
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )
                st.stop()
            else:
                st.rerun()
        address = location.raw["address"]

        city_keys = ["city", "town", "village", "suburb"]
        country_keys = ["country", "state", "county"]

        city = self._get_detail_from_address(address, city_keys)
        country = self._get_detail_from_address(address, country_keys)

        return city, country

    def _get_detail_from_address(self, address, keys):
        """
        Get a detail from an address using a list of possible keys.

        Parameters:
        address (dict): The address to get the detail from.
        keys (list): The possible keys for the detail.

        Returns:
        detail (str): The detail from the address.
        """
        try:
            for key in keys:
                if key in address:
                    return address[key]
            return ""
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Location details could not be retrieved.
                - Error Code: 0x008
                - There may be issues with Geolocataion Provider.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def add_marker(self, lat, lon, landmark_name, confidence):
        """
        Add a marker to the map.

        Parameters:
        lat (float): Latitude of the marker.
        lon (float): Longitude of the marker.
        landmark_name (str): Name of the landmark.
        confidence (str): Confidence score of the landmark detection.
        """
        try:
            confidence_score = float(confidence.split(": ")[1].strip("%")) / 100
        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Invalid confidence score.
                - Error Code: 0x009
                - It's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

        if confidence_score > self.max_score:
            self.max_score = confidence_score
            self.max_score_location = [lat, lon]

        self.map.location = self.max_score_location

        marker_color = self._get_marker_color(confidence_score)
        icon_pin = folium.features.DivIcon(
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            html=f'<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{marker_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-map-pin">'
            f'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>'
            f'<circle cx="12" cy="10" r="3" fill="{marker_color}"></circle>'
            "</svg>",
        )
        icon_star = folium.features.DivIcon(
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            html=f'<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="{marker_color}" stroke="{marker_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-star">'
            f'<polygon points="12 2 15.09 8.5 22 9.27 17 14 18.18 21 12 17.77 5.82 21 7 14 2 9.27 8.91 8.5 12 2"></polygon>'
            "</svg>",
        )
        icon_x = folium.features.DivIcon(
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            html=f'<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="{marker_color}" stroke="{marker_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x">'
            f'<line x1="18" y1="6" x2="6" y2="18"></line>'
            f'<line x1="6" y1="6" x2="18" y2="18"></line>'
            "</svg>",
        )

        icon = self._get_marker_icon(confidence_score, icon_pin, icon_star, icon_x)

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<strong>{landmark_name}</strong><br><em>{confidence}</em>",
                show=True,
                max_width=100,
            ),
            icon=icon,
        ).add_to(self.map)

    def _get_marker_icon(self, confidence_score, icon_pin, icon_star, icon_x):
        """
        Get the marker icon based on the confidence score.

        Parameters:
        confidence_score (float): The confidence score of the landmark detection.
        icon_pin (folium.features.DivIcon): The pin icon.
        icon_star (folium.features.DivIcon): The star icon.
        icon_x (folium.features.DivIcon): The x icon.

        Returns:
        icon (folium.features.DivIcon): The marker icon.
        """
        if confidence_score < 0.35:
            icon = icon_x
        elif confidence_score < 0.65:
            icon = icon_pin
        else:
            icon = icon_star
        return icon

    def _get_marker_color(self, confidence_score):
        """
        Get the marker color based on the confidence score.

        Parameters:
        confidence_score (float): The confidence score of the landmark detection.

        Returns:
        color (str): The marker color.
        """
        if confidence_score < 0.35:
            color = "red"
        elif confidence_score < 0.65:
            color = "yellow"
        else:
            color = "green"
        return color

    def add_markers(self, landmarks):
        """
        Add markers to the map for a list of landmarks.

        Parameters:
        landmarks (list): The landmarks to add markers for.
        """
        for landmark in landmarks:
            lat, lon = landmark.location.lat_lng
            landmark_name = landmark.description
            confidence = f"Confidence: {landmark.score * 100:.2f}%"

            self.add_marker(lat, lon, landmark_name, confidence)

    def add_heatmap(self, lat, lon, score):
        """
        Instead of adding a heatmap, this method adds a circle to the map.
        It acts as background for the markers.
        """
        folium.Circle(
            location=[lat, lon],
            radius=ACCURACY_HEATMAP_RADIUS * 1.8,
            color=f"{'red' if score < 0.35 else 'yellow' if score < 0.65 else 'green'}",
            fill=True,
            fill_color=f"{'red' if score < 0.35 else 'yellow' if score < 0.65 else 'green'}",
            popup="Accuracy",
            opacity=0.5,
        ).add_to(self.map)

    def satalite_map(self):
        """
        Create a satalite map layer.

        Returns:
        satalite_map (folium.TileLayer): The satalite map layer.
        """
        try_count_2 = 0
        try:
            satalite_map = folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Esri Satellite",
                overlay=False,
                control=True,
            )
            satalite_map.add_to(self.map)
            try_count_2 = 0
            return satalite_map
        except Exception as e:
            try_count_2 += 1
            if try_count_2 > 2:
                st.error(
                    f"""
                    Error: {e}
                    ### Error: Satalite map could not be created.
                    - Error Code: 0x010
                    - There may be issues with Map Tile Provider.
                    - Most likely, it's not your fault.
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )
                st.stop()
            else:
                st.rerun()

    def get_city_country(self, lat, lon):
        """
        Get the city and country of a location using its latitude and longitude.

        Parameters:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.

        Returns:
        city (str): The city of the location.
        country (str): The country of the location.
        """
        city, country = self.get_location_details(lat, lon)
        return city, country

    def display_map(self, max_content_width, max_content_height):
        """
        Display the map on Streamlit.

        Parameters:
        max_content_width (int): The maximum width of the map.
        """

        try:
            components.html(
                self.map._repr_html_(),
                width=max_content_width,
                height=max_content_width * 0.6,
            )

        except Exception as e:
            st.error(
                f"""
                Error: {e}
                ### Error: Map could not be displayed.
                - Error Code: 0x011
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()


class Landmarker(FoliumMap):
    # Class definitions
    """
    The Landmarker class is a child class of the GoogleCloudVision and FoliumMap classes.
    It is the main class of the Credentials.
    It uses the GoogleCloudVision class to perform landmark detection on an image.
    It uses the FoliumMap class to create a Folium map and add markers to the map.
    """

    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        self.gc = self.init_google_cloud_vision()
        self.fm = self.init_folium_map()
        self.set_page_config()
        self.screen_width = 0
        self.screen_height = 0
        try:
            with st.empty():
                _screen_res = streamlit_js_eval(
                    js_expressions="""
            function getScreenResolution() {
                return  window.innerWidth + "x" + window.screen.height;
            }
            getScreenResolution();
            """,
                    want_output=True,
                    key="SCR_W",
                )

                if _screen_res.split("x")[0] and _screen_res.split("x")[1]:
                    self.screen_width = int(_screen_res.split("x")[0])
                    self.screen_height = int(_screen_res.split("x")[1])
                st.empty()
        except Exception as e:
            pass

    def init_google_cloud_vision(self):
        if self.debug:
            return MockGoogleCloudVision()
        else:
            return GoogleCloudVision()

    def init_folium_map(self):
        return FoliumMap()

    def set_page_config(self):
        st.set_page_config(
            page_title="Landmark Detection",
            page_icon="🗿",
            layout="centered",
            initial_sidebar_state="auto",
        )

    def main(self):
        """
        Main function of the app.
        """

        # Set the page title and favicon
        if self.debug and DEBUG_MODE_WARNING_ENABLED:
            st.warning(
                """
                ## Warning: Debug mode is on.
                - Debug mode is on. (See the sidebar)
                """
            )
            st.sidebar.warning(
                """
                ### Warning: Debug mode is on.
                - Debug mode is on.
                - This mode is only for testing the app.
                - Please do not use this mode unless you are testing the app.
                """
            )
        title = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Major+Mono+Display&display=swap');
        .title {
            font-family: 'Major Mono Display', monospace;
            color: #1c6f11;
            top: 0px;
            font-size: 3.1em;
        }
        </style>

        <div class="title">
        LAND-MARKER
        </div>
        """
        st.markdown(title, unsafe_allow_html=True)

        st.markdown(
            """
            <link rel="shortcut icon" href="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/274/camera_1f4f7.png" type="image/png">
            """,
            unsafe_allow_html=True,
        )

        # Display the app sidebar
        sidebar_title = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=monospace&display=swap');
        .sidebar-title {
            font-family: 'monospace', monospace;
            font-weight: 1000;
            color: #1c6f11;
            top: 0px;
            font-size: 1.5em;
        }
        </style>

        <div class="sidebar-title">
        INSTRUCTIONS
        </div>
        """

        st.sidebar.markdown(sidebar_title, unsafe_allow_html=True)
        st.sidebar.write(
            """Use the upload widget to upload an image of a landmark. 
            The app will display the landmarks detected by Google Cloud Vision."""
        )

        # Initialize Google Cloud Vision and Folium Map
        gc = self.gc
        fm = self.fm
        # Create a switch to toggle between satellite and normal mode
        camera = st.sidebar.toggle(
            label="Camera", value=False, help="Switch on the camera."
        )
        if camera:
            st.write(" - Privacy Notice: Camera is on")
            try:
                uploaded_file = st.sidebar.camera_input(
                    label="Point the camera at a landmark",
                )
            except Exception as e:
                st.warning(
                    f"""
                    Error: {e}
                    ### Error: Camera could not be turned on.
                    - Error Code: 0x012
                    - There may be issues with your camera.
                    - Try enabling the camera in your browser/OS settings.
                    - You can manually upload an image of a landmark.
                    - If the problem persists, it's not your fault, probably.
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )
        else:
            try:
                uploaded_file = st.sidebar.file_uploader(
                    label="Upload an image",
                    type=SUPPORTED_FORMATS,
                    accept_multiple_files=False,
                    help="Upload an image of a landmark.",
                )
            except Exception as e:
                st.warning(
                    f"""
                    Error: {e}
                    ### Error: Image could not be uploaded.
                    - Error Code: 0x013
                    - There may be issues with your image.
                    - Please make sure you have uploaded a valid image.
                    - Please make sure the image is in one of the supported formats (png, jpg, jpeg, webp).
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )

        # If image is uploaded, display the image on sidebar but limit the image height to 300 pixels
        if uploaded_file is not None:
            image = Img.open(uploaded_file)
            st.sidebar.image(
                image,
                caption="Uploaded Image",
                use_column_width=True,
            )
        else:
            # Display the app description
            st.write(
                """
                Detect **landmarks** in an image and **mark** them on a map.
                """
            )

            # Display the app instructions
            st.markdown(
                """
                ---
                ### _Instructions_
                - _**Click** on the **>** icon on the **top left corner** of the app to expand the sidebar._
                - _**Upload** an image of a landmark using the upload **widget** on the sidebar._
                """,
                unsafe_allow_html=True,
            )
        landmark_most_matched = ""
        landmark_most_matched_score = 0
        lat_most_matched = 0
        lon_most_matched = 0
        # If an image is uploaded, perform landmark detection and add markers to the map
        if uploaded_file is not None:
            landmarks = gc.find_landmark(uploaded_file)
            for landmark in landmarks:
                landmark_name = landmark.description
                confidence = "Matched: " + str(round(landmark.score * 100, 2)) + "%"
                lat = landmark.locations[0].lat_lng.latitude
                lon = landmark.locations[0].lat_lng.longitude
                fm.add_marker(lat, lon, landmark_name, confidence)
                fm.add_heatmap(lat, lon, landmark.score)
                if landmark.score > landmark_most_matched_score:
                    landmark_most_matched_score = landmark.score
                    landmark_most_matched = landmark_name
                    lat_most_matched = lat
                    lon_most_matched = lon

            # Convert the map to HTML
            try:
                map_html = fm.map._repr_html_()
            except Exception as e:
                st.error(
                    f"""
                    Error: {e}
                    ### Error: Map could not loaded.
                    - Error Code: 0x014
                    - Most likely, it's not your fault.
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )
                st.stop()
            # use js or css to make iframe smaller for map_html

            # Adjust the map to show all markers. You may want to zoom out a bit to see the whole map extend by 10%
            try:
                fm.map.fit_bounds(fm.map.get_bounds(), padding=[40, 40], max_zoom=17)
            except Exception as e:
                st.warning(
                    f"""
                    Error: {e}
                    ### Error: Map could not be adjusted.
                    - Error Code: 0x015
                    - Most likely, it's not your fault.
                    - Please try again, or zoom out a bit to see the whole map.
                    - You can also rerun the app to see if the problem persists.
                    - If the problem persists, please contact the developer.
                    """
                )
            # Display a note about zooming out to see the whole map
            if landmarks:
                a = """ - **Zoom out to see the whole map, or just download it.**"""

                b = """ - **Click on the markers to see the landmark name and similarity score.**"""

                c = """ - **Click on the download button to download the map.**"""

                d = """ - **Toggle the satellite map switch to see the map in satellite mode.**"""

                e = """ - **Toggle the stream summary switch to see the summary stream.**"""
                with st.expander("**Click here to see the instructions.**"):
                    st.write(a + "\n" + b + "\n" + c + "\n" + d + "\n" + e)
                    st.write(
                        """
                        ---
                        ICON GUIDE:
                        - **Red X**: Low confidence
                        - **Yellow Pin**: Medium confidence
                        - **Green Star**: High confidence
                        """
                    )
                with st.expander("**Click here to change the app settings.**"):
                    col1, col2 = st.columns(2)
                    with col1:
                        satellite_mode = st.toggle(
                            "Satellite Map",
                            False,
                            help="Switch on the satellite mode.",
                        )
                    with col2:
                        stream_mode = st.toggle(
                            "Stream Summary",
                            False,
                            help="Switch on for streaming the summary as it's being generated.",
                        )
                    if stream_mode:
                        st.session_state["summary_stream"] = True
                    else:
                        st.session_state["summary_stream"] = None
                # Choose the tileset based on the switch
                _ = fm.satalite_map() if satellite_mode else None
                # open google maps in a new tab and map should be in satellite mode
            else:
                pass
            # Display the map if landmarks are detected, if not display a message
            PREVIOUS_CITY_COUNTRY = ("Kövsər Dönər", "28 May")
            if landmarks:
                city, country = fm.get_city_country(lat, lon)
                if city and country:
                    if (city, country) != PREVIOUS_CITY_COUNTRY:
                        st.write(
                            f"""
                            ## {landmark_most_matched}
                            ### {city}, {country}
                            """
                        )
                        PREVIOUS_CITY_COUNTRY = (city, country)
                else:
                    st.write(
                        """
                        # Unknown Location
                        """
                    )
                try:
                    st.write(
                        """
                        ##### LLM Based Summary:
                        """
                    )
                    summarizer = OpenAI_LLM()
                    prompt = f"Craft a professional and concise 80-word summary about {landmark_most_matched} in {city}, {country}. Include the origin of its name, historical significance, and cultural impact. Share fascinating facts that make it a must-visit for tourists."
                    # TODO: refactor this part and move it to a separate method
                    if st.session_state.get("summary_stream") is not None:
                        st.write_stream(summarizer.stream_summary(prompt))
                        time.sleep(0.10)
                    else:
                        with st.spinner("Generating LLM Based Summary..."):
                            summary = summarizer.generate_summary(prompt)
                            st.write(
                                f"""
                                > **{summary}**
                                """
                            )
                except Exception as e:
                    st.error(
                        f"""
                        Error: {e}
                        ### Error: LLM Based Summary could not be generated.
                        - Error Code: 0x017
                        - Most likely, it's not your fault.
                        - Please try again. If the problem persists, please contact the developer.
                        """
                    )
                    st.stop()
                help_text = (
                    """Satalite map is not available for download. What you are going to download is the normal map."""
                    if satellite_mode
                    else """Download the map to see the whole map."""
                )
                lat = lat_most_matched
                lon = lon_most_matched
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.link_button(
                        label="Show in Google Maps",
                        url=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                    )
                wiki_url = (
                    fm.get_wikipedia_page(landmark_most_matched)
                    or f"https://www.google.com/search?q={landmark_most_matched} wikipedia&btnI"
                )
                with col2:
                    st.link_button(
                        label="Open Wikipedia Page",
                        url=wiki_url,
                    )
                    try:
                        col3.download_button(
                            label="Download Map",
                            data=map_html,
                            file_name=f"{landmark_most_matched}_full_screen_map.html",
                            mime="text/html",
                            on_click=st.write(
                                f'<a href="data:text/html;base64,{base64.b64encode(map_html.encode()).decode()}" download="map.html" style="display: none;">Download Map</a>',
                                unsafe_allow_html=True,
                            ),
                            key="normal_map",
                            help=help_text,
                        )
                    except UnboundLocalError:
                        st.write(
                            """
                        > boop-beep-boop...
                        """
                        )
                fm.display_map(self.screen_width, self.screen_height)

            else:
                st.write(
                    """
                    # Oops! No landmarks detected.
                    ## Possible reasons:
                    - The image is not of a landmark.
                    - The landmark is not famous enough.
                    - The image is not clear enough.
                    """
                )
        for i in range(4):
            st.write("")
        footer = """
        ---
        ###### This app was created by _[Elshad Sabziyev](https://www.github.com/elshadsabziyev)_ using _[Streamlit](https://www.streamlit.io/), [Google Cloud Vision](https://cloud.google.com/vision)_,_[Folium](https://python-visualization.github.io/folium/)_ and _[OpenAI API](https://openai.com)_.
        """
        st.markdown(footer, unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        debug_mode = True if st.secrets["debug_mode"] == "True" else False
    except Exception as e:
        debug_mode = False
    landmarker = Landmarker(debug=debug_mode)
    try:
        landmarker.main()
    except Exception as e:
        st.error(
            f"""
            Error: {e}
            ### Error: App could not be loaded.
            - Error Code: 0x016
            - Most likely, it's not your fault.
            - Please try again. If the problem persists, please contact the developer.
            """
        )
        st.stop()
