import streamlit as st
import folium
import requests
import branca.colormap as cm
from geopy.geocoders import Nominatim

DEFAULT_ZOOM_START = 2
ACCURACY_HEATMAP_RADIUS = 50


class FoliumMap:
    def __init__(self, zoom_start_=DEFAULT_ZOOM_START):
        self.max_score_location = [0, 0]
        self.max_score = 0
        self.zoom_start = zoom_start_
        self.map = self._create_initial_map()
        try:
            self.geo_locator = Nominatim(user_agent="LandMarker_App")
        except Exception as e:
            st.error(
                f"""
                ### Error: Map could not be created.
                - Error Code: 2x000
                - There may be issues with Geolocation Provider.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()
        self.colormap = self._create_colormap()

    def _create_initial_map(self):
        try:
            return folium.Map(
                location=self.max_score_location, zoom_start=self.zoom_start
            )
        except Exception as e:
            st.error(
                f"""
                ### Error: Map could not be created.
                - Error Code: 2x001
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    @staticmethod
    def get_wikipedia_page(landmark):
        tries = 0
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
                tries = 0
                return page_url
            else:
                tries = 0
                return None
        except Exception as e:
            tries += 1
            if tries > 2:
                st.error(
                    f"""
                    ### Error: Wikipedia page could not be retrieved.
                    - Error Code: 2x002
                    - There may be issues with Wikipedia API.
                    - Most likely, it's not your fault.
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )
                st.stop()
            else:
                st.rerun()

    def _create_colormap(self):
        return cm.LinearColormap(
            colors=["white", "yellow", "green"],
            index=[0, 50, 100],
            vmin=0,
            vmax=100,
            caption="Similarity score",
        )

    def get_location_details(self, lat, lon):
        try_count = 0
        try:
            location = self.geo_locator.reverse(f"{lat}, {lon}")
            try_count = 0
        except Exception as e:
            try_count += 1
            if try_count > 2:
                st.error(
                    f"""
                    ### Error: Location details could not be retrieved.
                    - Error Code: 2x003
                    - There may be issues with Geolocation Provider.
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
        try:
            for key in keys:
                if key in address:
                    return address[key]
            return ""
        except Exception as e:
            st.error(
                f"""
                ### Error: Location details could not be retrieved.
                - Error Code: 2x004
                - There may be issues with Geolocation Provider.
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()

    def add_marker(self, lat, lon, landmark_name, confidence):
        try:
            confidence_score = float(
                confidence.split(": ")[1].strip("%")) / 100
        except Exception as e:
            st.error(
                f"""
                ### Error: Invalid confidence score.
                - Error Code: 2x005
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
        icon = icon_pin
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                f"<strong>{landmark_name}</strong><br><em>{confidence}</em>",
                show=True,
                max_width=100,
            ),
            icon=icon,
        ).add_to(self.map)

    def _get_marker_color(self, confidence_score):
        if confidence_score < 0.35:
            color = "red"
        elif confidence_score < 0.65:
            color = "#ff7e37"
        else:
            color = "green"
        return color

    def add_markers(self, landmarks):
        for landmark in landmarks:
            lat, lon = landmark.location.lat_lng
            landmark_name = landmark.description
            confidence = f"Confidence: {landmark.score * 100:.2f}%"
            self.add_marker(lat, lon, landmark_name, confidence)

    def add_heatmap(self, lat, lon, score):
        folium.Circle(
            location=[lat, lon],
            radius=ACCURACY_HEATMAP_RADIUS * 1.8,
            color=f"{'red' if score < 0.35 else 'yellow' if score < 0.65 else 'green'}",
            fill=True,
            fill_color=f"{'red' if score < 0.35 else 'yellow' if score < 0.65 else 'green'}",
            popup="Accuracy",
            opacity=0.5,
        ).add_to(self.map)

    def satellite_map(self):
        try_count_2 = 0
        try:
            satellite_map = folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Esri",
                name="Esri Satellite",
                overlay=False,
                control=True,
            )
            satellite_map.add_to(self.map)
            try_count_2 = 0
            return satellite_map
        except Exception as e:
            try_count_2 += 1
            if try_count_2 > 2:
                st.error(
                    f"""
                    ### Error: Satellite map could not be created.
                    - Error Code: 2x006
                    - There may be issues with Map Tile Provider.
                    - Most likely, it's not your fault.
                    - Please try again. If the problem persists, please contact the developer.
                    """
                )
                st.stop()
            else:
                st.rerun()

    def get_city_country(self, lat, lon):
        city, country = self.get_location_details(lat, lon)
        return city, country

    def display_map(self):
        try:
            return self.map  # Return the map
        except Exception as e:
            st.error(
                f"""
                ### Error: Map could not be displayed.
                - Error Code: 2x007
                - Most likely, it's not your fault.
                - Please try again. If the problem persists, please contact the developer.
                """
            )
            st.stop()
