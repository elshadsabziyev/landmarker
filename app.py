# NOTE: This file is the main file of the Streamlit app.

# Import necessary libraries
import streamlit as st
from gui import Landmarker

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
