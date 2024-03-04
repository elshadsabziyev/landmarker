# NOTE: This file is part of the Landmarker app.

# Import necessary libraries
import streamlit as st
from PIL import Image as Img
from streamlit_js_eval import streamlit_js_eval
import base64
import time
from mapping import FoliumMap
from landmark_detection import GoogleCloudVision, MockGoogleCloudVision
from openai_summary import OpenAI_LLM, MockOpenAI_LLM
from firestore import Firestore

# Constants
SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "webp"]
DEBUG_MODE_WARNING_ENABLED = True


# TODO: Refactor and add other parent classes
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
        self.summarizer = self.init_OpenAI_LLM()
        self.firestore_connection = self.init_firestore()
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

    def init_OpenAI_LLM(self):
        if self.debug:
            return MockOpenAI_LLM()
        else:
            return OpenAI_LLM()

    def init_folium_map(self):
        return FoliumMap()

    def init_firestore(self):
        return Firestore()

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
                        PIN COLOR GUIDE:
                        - **Red Pin**: Low confidence
                        - **Yellow Pin**: Medium confidence
                        - **Green Pin**: High confidence
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
                    prompt = f"Craft a professional and concise 80-word summary about {landmark_most_matched} in {city}, {country}. Include the origin of its name, historical significance, and cultural impact. Share fascinating facts that make it a must-visit for tourists."
                    # TODO: refactor this part and move it to a separate method
                    if st.session_state.get("summary_stream") is not None:
                        st.write_stream(self.summarizer.stream_summary(prompt))
                        time.sleep(0.10)
                    else:
                        with st.spinner("Generating LLM Based Summary..."):
                            summary = self.summarizer.generate_summary(prompt)
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
                with st.spinner("Loading the map..."):
                    fm.display_map(self.screen_width, self.screen_height)
                st.write(
                    """
                    ---
                    """
                )
                st.write(
                    """
                    ## Reviews:
                    """
                )
                with st.spinner("Loading reviews..."):
                    reviews = self.firestore_connection.get_review_for_landmark(
                        lon, lat, 0.1, landmark_most_matched
                    )
                    # Button to add a review
                    with st.expander("**Click here to write a review.**"):
                        with st.form(key="add_review_form"):
                            username = st.text_input(
                                label="Username", help="Enter your username."
                            )
                            review = st.text_area(label="Review", help="Enter your review.")
                            score = st.slider(
                                label="Score",
                                min_value=1,
                                max_value=10,
                                value=5,
                                help="Choose a score.",
                                step=1,
                            )
                            submit_button = st.form_submit_button(label="Submit")

                        if submit_button:
                            if username and review and score:
                                self.firestore_connection.create_new_review(
                                    review,
                                    landmark_most_matched,
                                    f"{lon}/{lat}",
                                    score,
                                    username,
                                )
                                st.success("- Review added successfully.")
                                st.rerun()
                            else:
                                st.warning("- Please fill in all the fields.")
                    with st.expander(
                        "**Click here to see the reviews for this landmark.**"
                    ):
                        if reviews:
                            for review in reviews:
                                def mask_username(username):
                                    words = username.split()
                                    masked_words = []
                                    for word in words:
                                        if len(word) > 3:
                                            masked_word = word[:2] + "\\*" * (len(word) - 3) + word[-1]
                                        else:
                                            masked_word = word
                                        masked_words.append(masked_word)
                                    return ' '.join(masked_words)

                                st.markdown(f"##### {mask_username(review['Username'])}")
                                st.markdown(
                                    f""" {"**Excellent**" if review['Score10'] >= 9 else "**Good**" if review['Score10'] >= 7 else "**Average**" if review['Score10'] >= 5 else "**Poor**" if review['Score10'] >= 3 else "**Terrible**"} ({"⭐" * 1 if review['Score10'] <= 2 else "⭐" * 2 if review['Score10'] <= 4 else "⭐" * 3 if review['Score10'] <= 6 else "⭐" * 4 if review['Score10'] <= 8 else "⭐" * 5})"""
                                )
                                st.markdown(f"> {review['Review']}")
                                st.markdown("---")
                        else:
                            st.write(
                                """
                                - No reviews yet. Be the first one to review this landmark!
                                """
                            )
                    with st.expander("**Click here to see AI generated review summary.**"):
                        if reviews:
                            prompt = f"Craft a professional and concise 2-3 sentence review summary about {landmark_most_matched} in {city}, {country} considering the reviews: {', '.join([r['Review'] for r in reviews])}."
                            summary = self.summarizer.summarize_review(prompt)
                            st.write(
                                f"Overall Score: {round(sum([r['Score10'] for r in reviews])/len(reviews), 2)}"
                            )
                            st.write(
                                f"""
                                > **{summary}**
                                """
                            )
                        else:
                            st.write(
                                """
                                - No reviews yet. Be the first one to review this landmark!
                                """
                            )
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
        ###### This app was created by _[Elshad Sabziyev](https://www.github.com/elshadsabziyev)_ using _[Streamlit](https://www.streamlit.io/), [Google Cloud Vision](https://cloud.google.com/vision)_, _[Folium](https://python-visualization.github.io/folium/)_ and _[OpenAI API](https://openai.com)_.
        """
        st.markdown(footer, unsafe_allow_html=True)
