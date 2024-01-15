import random
import streamlit as st
import time

st.title("culinaryAI")

assistant_message = (
    "Welcome to culinaryAI! I'm here to help you with finding creative new recipes. Creative, not tasteful!"
    + "\n"
    + random.choice(
        [
            "What ingredients do you have in mind? Enter them below.",
            "Ready to plan your next meal? Share the ingredients you have.",
            "How can I assist with your culinary journey? Input the ingredients you'd like to use below.",
            "Tell me the key ingredients, and let's get started! Type them in below.",
            "Planning a dish? Share your ingredients, and let's cook up a recipe! Enter them below."
        ]
    )
)

with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""

    for chunk in assistant_message.split("\n"):
        full_response += chunk + " "
        time.sleep(0.5)  # Ändere die Verzögerung nach Bedarf
        # Cursor hinzugefügt
        message_placeholder.markdown(full_response + "▌")

# Initialize chat history
if "message" not in st.session_state:
    st.session_state.message = []

# Display chat messages from history on app rerun
for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("pasta, tomatoes, onions..."):
    
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.message.append({"role": "user", "content": prompt})
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response =""
        assistant_response = random.choice(
            [
                "Great choices! Let me whip up a delicious recipe for you.",
                "Excellent selection! I'll create a tasty recipe based on your ingredients.",
                "Fantastic! Your chosen ingredients will make a mouthwatering dish. Let me suggest a recipe.",
                "Nice picks! I'm excited to generate a recipe using the ingredients you provided.",
                "Perfect! Now, let me work my magic and suggest a fantastic recipe for your selected ingredients."
            ]
        )
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            #Cursor added
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.message.append({"role": "assistant", "content": full_response})