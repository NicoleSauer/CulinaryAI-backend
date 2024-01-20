import random
import streamlit as st
import time
from run import generate_recipe
st.title("culinaryAI")

assistant_message = (
    f"Welcome to culinaryAI! I'm here to help you with finding creative new recipes. Creative, not tasteful!"
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

with st.chat_message(name="assistant", ):
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
        assistant_response = random.choice(
            [
                "Great choices! Let me whip up a delicious recipe for you...\n",
                "Excellent selection! I'll create a tasty recipe based on your ingredients...\n",
                "Fantastic! Your chosen ingredients will make a mouthwatering dish. Let me suggest a recipe...\n",
                "Nice picks! I'm excited to generate a recipe using the ingredients you provided...\n",
                "Perfect! Now, let me work my magic and suggest a fantastic recipe for your selected ingredients...\n"
            ]
        )

        response_1 = ""
        for chunk in assistant_response.split(' '):
            response_1 += chunk + " "
            time.sleep(0.05)
            # Cursor added
            message_placeholder.markdown(response_1 + "▌")

        message_placeholder.markdown(response_1)

        # Add response to chat history
        st.session_state.message.append(
            {"role": "assistant", "content": response_1})

        model_response = generate_recipe(
            'openai-community/gpt2-large', 'openai-community/gpt2-large', prompt.split(', '), 'Please give me a recipe wit the following ingredients:')

        response_2 = ""
        for chunk in model_response.split(' '):
            response_2 += chunk + " "
            time.sleep(0.05)
            # Cursor added
            message_placeholder.markdown(response_2 + "▌")

        message_placeholder.markdown(response_2)

        # Add response to chat history
        st.session_state.message.append(
            {"role": "assistant", "content": response_2})
