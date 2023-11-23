# A python code to find the landmark name from given image,
# get latitude and longitude of the landmark
# and display it on the map using folium library and Google image vision

# Importing required libraries
import os
from google.cloud import vision
from google.cloud.vision import Image
import folium
from folium import plugins
import requests
import streamlit as st
import branca.colormap as cm
from branca.element import Template, MacroElement


WORKING_DIR = os.getcwd()
CREDS_FILE = os.path.join(WORKING_DIR, "gcp_credentials.json")
IMAGES_DIR = os.path.join(WORKING_DIR, "input_images")
MAPS_DIR = os.path.join(WORKING_DIR, "output_maps")


# Creating a client
class GoogleCloudVision:
    def __init__(self, credentials=CREDS_FILE):
        # Initialize a client and authenticate with credentials
        self.credentials = credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials
        self.client = vision.ImageAnnotatorClient()

    def find_landmark(self, image_data):
        # Initialize a client
        client = vision.ImageAnnotatorClient.from_service_account_json(self.credentials)
        # Load image into memory
        image = vision.Image(content=image_data.read())
        # Perform landmark detection
        response = client.landmark_detection(image=image)
        landmarks = response.landmark_annotations
        return landmarks


import branca.colormap as cm


class FoliumMap:
    def __init__(self):
        self.map = folium.Map(location=[0, 0], zoom_start=2)
        # Define a colormap
        self.colormap = cm.LinearColormap(
            colors=["red", "yellow", "green"], index=[0, 0.5, 1], caption="Confidence"
        )

    def add_marker(self, lat, lon, landmark_name, confidence):
        # Normalize the confidence score to [0, 1]
        confidence_score = float(confidence.split(": ")[1].strip("%")) / 100
        # Get the color from the colormap
        marker_color = self.colormap.rgb_hex_str(confidence_score)

        icon = folium.features.DivIcon(
            icon_size=(30, 30),
            icon_anchor=(15, 15),
            html=f'<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="{marker_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-map-pin">'
            f'<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>'
            f'<circle cx="12" cy="10" r="3" fill="{marker_color}"></circle>'
            "</svg>",
        )

        folium.Marker(
            [lat, lon],
            popup=landmark_name + " " + confidence,
            icon=icon,
        ).add_to(self.map)

    def add_heatmap(self, lat, lon):
        folium.plugins.HeatMap([[lat, lon]]).add_to(self.map)

    def save_map(self, map_name):
        # Add the colormap to the map
        self.map.add_child(self.colormap)

        # Add Font Awesome CSS
        template = """
        {% macro html(this, kwargs) %}
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css">
        {% endmacro %}
        """
        macro = MacroElement()
        macro._template = Template(template)
        self.map.get_root().add_child(macro)

        self.map.save(map_name)


# main function to find location of the landmark which name is given in IMAGE_NAME
# and highlight all possible locations on for given landmark
# write confidences of each location on map for each highlighted location


import streamlit.components.v1 as components


def main():
    # initialize GoogleCloudVision class
    gc = GoogleCloudVision()
    # initialize FoliumMap class
    fm = FoliumMap()

    # upload image
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")
    if uploaded_file is not None:
        # find landmark from image
        landmarks = gc.find_landmark(uploaded_file)
        # find all possible locations of the landmark
        for landmark in landmarks:
            # get landmark name
            landmark_name = landmark.description
            # get confidence of landmark
            confidence = "Confidence: " + str(round(landmark.score * 100, 2)) + "%"
            # get latitude and longitude of landmark
            lat = landmark.locations[0].lat_lng.latitude
            lon = landmark.locations[0].lat_lng.longitude
            # add marker on map for each location of landmark
            fm.add_marker(lat, lon, landmark_name, confidence)
            # add heatmap on map for each location of landmark
            fm.add_heatmap(lat, lon)
        # save map
        map_file = os.path.join(MAPS_DIR, "output.html")
        fm.save_map(map_file)
        # Display the map in the Streamlit app
        with open(map_file, "r") as f:
            map_html = f.read()
        components.html(map_html, height=600)
    else:
        st.write("Please upload an image.")


if __name__ == "__main__":
    main()
