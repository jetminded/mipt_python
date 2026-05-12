import streamlit as st
from pages.cowsay import render_cowsay_page
from pages.maps import render_maps_page

def main():
    """Main function to run the Streamlit application"""
    st.set_page_config(
        page_title="Demo Streamlit App",
        page_icon="🚀",
        layout="wide"
    )
    
    # Navigation using st.navigation
    pg = st.navigation([
        st.Page(render_cowsay_page, title="Cowsay", icon="🐄"),
        st.Page(render_maps_page, title="Maps", icon="🗺️"),
    ], position='top')
    pg.run()

if __name__ == "__main__":
    main()
