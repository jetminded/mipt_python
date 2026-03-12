import streamlit as st
import cowsay
import io
import sys

def render_cowsay_page():
    """Render the cowsay page with animal selection and text input"""
    st.title("🐄 Cowsay Generator")
    
    # Animal selection radio buttons
    animal_options = ["cow", "dragon", "tux"]
    
    selected_animal = st.radio(
        "Choose an animal:",
        options=animal_options,
        index=0
    )
    
    # Text input field
    user_text = st.text_input(
        "Enter your text:",
        value="Hello, World!"
    )
    
    # Generate cowsay output when text is provided
    if user_text.strip():
        # Capture stdout to get the cowsay output as string
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        # Generate cowsay output using the selected animal
        if selected_animal == "cow":
            cowsay.cow(user_text)
        elif selected_animal == "dragon":
            cowsay.dragon(user_text)
        elif selected_animal == "tux":
            cowsay.tux(user_text)
        
        # Restore stdout and get the captured output
        sys.stdout = old_stdout
        output = captured_output.getvalue()
        
        # Display the result in a code block
        st.code(output, language="text")
    else:
        st.info("Please enter some text to generate cowsay output.")
