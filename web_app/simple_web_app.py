import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Simple Web App",
    page_icon="🎈",
    layout="centered"
)

# App title
st.title("🎈 Simple Web App")

# Create form for username input
with st.form("user_form"):
    st.subheader("Enter your name")
    
    # Username input field
    username = st.text_input(
        "Username:",
        placeholder="Enter your name here..."
    )
    
    # Submit button
    submitted = st.form_submit_button("Submit", type="primary")

# Handle form submission
if submitted:
    if username:
        # Create greeting banner
        st.success(f"🎉 Welcome, {username}!")
        
        # Launch balloons
        st.balloons()
        
        # Additional message
        st.write(f"Hello, **{username}**! We're glad to see you in our app! 🚀")
        
    else:
        # Warning if name is not entered
        st.warning("⚠️ Please enter your name before submitting!")
