# Import necessary libraries
from google.cloud import vision
import folium
from folium import plugins
import streamlit as st
import streamlit.components.v1 as components
import branca.colormap as cm
from branca.element import Template, MacroElement
from PIL import Image as Img
from google.oauth2 import service_account
import base64

# Define the supported image formats
SUPPORTED_FORMATS = ("png", "jpg", "jpeg", "webp")
# Define the accuracy using heatmap marker radius
ACCURACY_HEATMAP_RADIUS = 20
DEFAULT_ZOOM_START = (
    2  # Does noting since we are using fit_bounds to fit the map to the markers
)
IS_CAMERA_ACCESS_ASKED = False


# Define the main App class
class App:
    def __init__(self):
        """
        Initialize the App class.
        """

        # Create a credentials dictionary using Streamlit secrets
        # These secrets are used to authenticate with the Google Cloud Vision API
        credentials_dict = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"],
            "universe_domain": st.secrets["universe_domain"],
        }

        # Create a credentials object from the dictionary
        # This object will be used to authenticate with the Google Cloud Vision API
        self.credentials = service_account.Credentials.from_service_account_info(
            credentials_dict
        )


# Google Cloud Vision class for landmark detection
class GoogleCloudVision(App):
    def __init__(self):
        """
        Initialize the GoogleCloudVision class.
        This class is a child of the App class, so we call the constructor of the parent class.
        """

        super().__init__()

        # Initialize a client for the Google Cloud Vision API
        # We authenticate with the API using the credentials object created in the parent class
        self.client = vision.ImageAnnotatorClient(credentials=self.credentials)

    def find_landmark(self, image_data):
        """
        Detect landmarks in an image using the Google Cloud Vision API.

        Parameters:
        image_data (bytes): The image data to analyze.

        Returns:
        landmarks (list): A list of detected landmarks.
        """

        # Load the image data into memory
        image_data.seek(0)
        image = vision.Image(content=image_data.read())

        # Perform landmark detection on the image
        # The response is a list of detected landmarks
        response = self.client.landmark_detection(image=image)
        landmarks = response.landmark_annotations
        with open("response.txt", "w") as f:
            f.write(str(response))
        return landmarks


class FoliumMap:
    def __init__(self, zoom_start_=DEFAULT_ZOOM_START):
        """
        Initialize the FoliumMap class.

        Parameters:
        zoom_start (int): Initial zoom level for the map.
        """

        # Initialize the maximum score and its corresponding location
        self.max_score_location = [0, 0]
        self.max_score = 0
        self.zoom_start = zoom_start_

        # Create a Folium map centered at the maximum score location
        self.map = folium.Map(
            location=self.max_score_location, zoom_start=self.zoom_start
        )

        # Initialize a linear color map with white, yellow, and green colors
        # The color map is used to color markers based on their similarity score
        # Scores of 0 are colored white, scores of 50 are colored yellow, and scores of 100 are colored green
        self.colormap = cm.LinearColormap(
            colors=["white", "yellow", "green"],  # Colors for the color map
            index=[0, 50, 100],  # Scores corresponding to the colors
            vmin=0,  # Minimum score
            vmax=100,  # Maximum score
            caption="Similarity score",  # Caption for the color map
        )

    def add_marker(self, lat, lon, landmark_name, confidence):
        """
        Add a marker to the map.

        Parameters:
        lat (float): Latitude of the marker.
        lon (float): Longitude of the marker.
        landmark_name (str): Name of the landmark.
        confidence (str): Confidence score of the landmark detection.
        """

        # Convert the confidence score from a percentage to a decimal
        confidence_score = float(confidence.split(": ")[1].strip("%")) / 100

        # If this location's score is higher than the current max score, update the max score and location
        if confidence_score > self.max_score:
            self.max_score = confidence_score
            self.max_score_location = [lat, lon]

        # Update the map center and zoom level to the max score location
        self.map.location = self.max_score_location

        # Determine the marker color based on the confidence score
        # If the confidence score is less than 50%, the marker color is the first color in the colormap
        if confidence_score < 0.50:
            marker_color = self.colormap(0)
        # If the confidence score is less than 80%, the marker color is the second color in the colormap
        elif confidence_score < 0.80:
            marker_color = self.colormap(50)
        # If the confidence score is 80% or higher, the marker color is the third color in the colormap
        else:
            marker_color = self.colormap(100)

        # Define the marker icons
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

        # Add a marker to the map at the specified latitude and longitude
        # The marker icon and popup text depend on the confidence score
        if confidence_score > 0.80:
            # If the confidence score is greater than 80%, use the star icon
            folium.Marker(
                [lat, lon],  # Position of the marker
                popup=landmark_name + " " + confidence,  # Popup text
                icon=icon_star,  # Icon for the marker
            ).add_to(self.map)
        elif confidence_score > 0.50:
            # If the confidence score is greater than 50%, use the pin icon
            folium.Marker(
                [lat, lon],  # Position of the marker
                popup=landmark_name + " " + confidence,  # Popup text
                icon=icon_pin,  # Icon for the marker
            ).add_to(self.map)
        else:
            # If the confidence score is 50% or less, use the X icon
            folium.Marker(
                [lat, lon],  # Position of the marker
                popup=landmark_name + " " + confidence,  # Popup text
                icon=icon_x,  # Icon for the marker
            ).add_to(self.map)

    def add_heatmap(self, lat, lon):
        """
        Add a heatmap to the map at the specified latitude and longitude.

        Parameters:
        lat (float): Latitude of the heatmap.
        lon (float): Longitude of the heatmap.
        """

        # Add a heatmap to the map at the specified latitude and longitude
        folium.plugins.HeatMap(
            [[lat, lon]], radius=ACCURACY_HEATMAP_RADIUS, blur=12, min_opacity=0.5
        ).add_to(self.map)

    def display_map(self, max_content_width):
        """
        Display the map.

        Parameters:
        max_content_width (int): Maximum content width for the map.
        """

        # Add a link to the Font Awesome stylesheet for the marker icons
        template = """
        {% macro html(this, kwargs) %}
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css">
        {% endmacro %}
        """
        macro = MacroElement()
        macro._template = Template(template)
        self.map.get_root().add_child(macro)
        # Display the map
        components.html(self.map._repr_html_(), width=max_content_width, height=500)

    def satalite_map(self):
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Esri Satellite",
            overlay=False,
            control=True,
        ).add_to(self.map)

    def save(self, filename):
        """
        Save the map to a file.

        Parameters:
        filename (str): Name of the file to save the map to.
        """
        folium.TileLayer(tiles="Mapbox Control Room").add_to(self.map)
        self.map.save(filename)


st.set_page_config(
    page_title="Landmark Detection",
    page_icon="📷",
    layout="centered",
    initial_sidebar_state="expanded",
)


from streamlit_js_eval import streamlit_js_eval

screen_width = streamlit_js_eval(
    js_expression="window.screen.width", key="screen_width"
)


def main():
    """
    Main function of the app.
    """

    # Set the page title and favicon
    st.title("LANDMARK BOT 📌🗺️")
    st.markdown(
        """
        <link rel="shortcut icon" href="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/google/274/camera_1f4f7.png" type="image/png">
        """,
        unsafe_allow_html=True,
    )

    # Display the app sidebar
    st.sidebar.title("Upload an image of a landmark")
    st.sidebar.write(
        """Use the upload widget to upload an image of a landmark. 
        The app will display the landmarks detected by Google Cloud Vision."""
    )

    # Initialize Google Cloud Vision and Folium Map
    gc = GoogleCloudVision()
    fm = FoliumMap()

    # Create a switch to toggle between satellite and normal mode

    # Create a file uploader for the user to upload an image
    js_code_camera_access = """
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
  // Request access to the camera
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
      // User granted access to the camera, you can do something with the stream if needed
      console.log('Camera access granted');
      // You might want to close the stream if you're not using it
      // stream.getTracks().forEach(track => track.stop());
    })
    .catch(function(error) {
      // User denied access to the camera or there was an error
      console.error('Camera access denied:', error);
    });
} else {
  // If getUserMedia is not supported
  console.error('getUserMedia is not supported on this browser');
}
"""
    camera = st.sidebar.toggle("Camera", False, help="Switch on the camera.")
    if camera:
        st.write("Camera is on")
        uploaded_file = st.sidebar.camera_input(label="Point the camera at a landmark.")
    else:
        st.write("Camera is off")
        uploaded_file = st.sidebar.file_uploader(
            label="",
            type=SUPPORTED_FORMATS,
            accept_multiple_files=False,
            help="Upload an image of a landmark.",
        )

    # If image is uploaded, display the image on sidebar but limit the image height to 300 pixels
    if uploaded_file is not None:
        image = Img.open(uploaded_file)
        st.sidebar.image(image, caption="Uploaded Image", use_column_width=True)
    else:
        # Display the app description
        st.write(
            """
            This app uses Google Cloud Vision to detect landmarks in images. 
            """
        )

        # Display the app instructions
        st.markdown(
            """
            ### Instructions
            - _**Click** on the **>** icon on the **top left corner** of the app to expand the sidebar._
            - _**Upload** an image of a landmark using the upload **widget** on the sidebar._
            """,
            unsafe_allow_html=True,
        )

    # If an image is uploaded, perform landmark detection and add markers to the map
    if uploaded_file is not None:
        landmarks = gc.find_landmark(uploaded_file)
        for landmark in landmarks:
            landmark_name = landmark.description
            confidence = "Matched: " + str(round(landmark.score * 100, 2)) + "%"
            lat = landmark.locations[0].lat_lng.latitude
            lon = landmark.locations[0].lat_lng.longitude
            fm.add_marker(lat, lon, landmark_name, confidence)
            fm.add_heatmap(lat, lon)

        # Convert the map to HTML
        map_html = fm.map._repr_html_()
        # use js or css to make iframe smaller for map_html

        # Adjust the map to show all markers. You may want to zoom out a bit to see the whole map extend by 10%
        fm.map.fit_bounds(fm.map.get_bounds(), padding=[40, 40])
        # Display a note about zooming out to see the whole map
        if landmarks:
            a = """>Zoom out to see the whole map, or just download it."""

            b = """>Click on the markers to see the landmark name and similarity score."""
            st.write(a + "\n" + b)
            satellite_mode = st.toggle(
                "Satellite Mode", False, help="Switch on the satellite mode."
            )
            # Choose the tileset based on the switch
            apply_satellite = fm.satalite_map() if satellite_mode else None
            # Add a download button for the map. Upon clicking the button, open a new tab with the map in it
            try:
                st.download_button(
                    label="Download Map",
                    data=map_html,
                    file_name=f"{landmark_name}_full_screen_map.html",
                    mime="text/html",
                    on_click=st.write(
                        f'<a href="data:text/html;base64,{base64.b64encode(map_html.encode()).decode()}" download="map.html" style="display: none;">Download Map</a>',
                        unsafe_allow_html=True,
                    ),
                )
            except UnboundLocalError:
                st.write(
                    """
                > boop-beep-boop...
                """
                )

        else:
            pass
        # Display the map if landmarks are detected, if not display a message
        if landmarks:
            fm.display_map(max_content_width=screen_width)

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

    # Display the app footer
    st.write(
        """
        ###
        ###
        ###
        ###
        ###
        ###
        ###
        #### About
        > This app was created by [Elshad Sabziyev](https://www.github.com/elshadsabziyev) using [Streamlit](https://www.streamlit.io/), [Google Cloud Vision](https://cloud.google.com/vision), and [Folium](https://python-visualization.github.io/folium/).
        """
    )


# Check if the script is running directly (not being imported)
if __name__ == "__main__":
    # If so, run the main function
    main()
