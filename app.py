import streamlit as st
from gui import Landmarker

if __name__ == "__main__":
    try:
        debug_mode = True if st.secrets["Config"]["debug_mode"] == "True" else False
    except Exception as e:
        debug_mode = False
    landmarker = Landmarker(debug=debug_mode)
    try:
        landmarker.main()
    except Exception as e:
        st.error(
            f"""
            ### Error: App could not be loaded.
            - Error Code: 0x000
            - Most likely, it's not your fault.
            - Please try again. If the problem persists, please contact the developer.
            """
        )
        st.stop()
