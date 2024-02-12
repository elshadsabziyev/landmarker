# Note: This file contains the FoliumMap class which is used to create a Folium map and geolocate the landmarks detected.

# Import necessary libraries
import streamlit as st
import folium
import requests
import branca.colormap as cm
from geopy.geocoders import Nominatim
import streamlit.components.v1 as components

# Constants
DEFAULT_ZOOM_START = 2
ACCURACY_HEATMAP_RADIUS = 100

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
