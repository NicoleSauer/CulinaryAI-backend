import random
import streamlit as st
import base64
import time
from run import generate_recipe, initialize_model


# Load and initialize model
model, tokenizer = initialize_model(
    model_name='models/gpt2-large_2_epochs',
    tokenizer_model='openai-community/gpt2-large',
)

# 👨‍🍳
st.title("CulinaryAI")

st.session_state.user_input = st.chat_input("Nudeln, Tomaten, Zwiebeln...")

if "messages" not in st.session_state:
    # Initialize chat history
    st.session_state.messages = []

    greeting_message = 'Willkommen bei CulinaryAI! Ich bin hier, um dir bei der Suche nach kreativen neuen Rezepten zu helfen. Die Betonung liegt auf kreativ, nicht auf schmackhaft.'

    # Display greeting message with fake typing effect
    with st.chat_message(name="ai", avatar='images/icons/ai_chef4.png'):
        message_placeholder = st.empty()
        full_response = ""

        for char in greeting_message:
            full_response += char
            message_placeholder.markdown(full_response)
            time.sleep(0.01)

    # Add greeting message to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": greeting_message})

    # Choose random welcome message
    welcome_message = random.choice([
        "Welche Zutaten hast du im Sinn?",
        "Welche Zutaten schweben dir vor?",
        "Welche Zutaten möchtest du aufbrauchen?",
        "Bereit für die Planung deiner nächsten Mahlzeit? Teile die Zutaten, die du hast.",
        "Wie kann ich dir bei deiner kulinarischen Reise helfen? Gib unten die Zutaten ein, die du verwenden möchtest.",
        "Nenne mir die wichtigsten Zutaten und lass uns anfangen!",
        "Planst du ein Gericht? Teile deine Zutaten, und ich kreiere ein Rezept!"
    ])

    time.sleep(0.3)

    # Display welcome message with fake typing effect
    with st.chat_message(name="ai", avatar='images/icons/ai_chef4.png'):
        message_placeholder = st.empty()
        full_response = ""

        for char in welcome_message:
            full_response += char
            message_placeholder.markdown(full_response)
            time.sleep(0.01)

    # Add welcome message to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": welcome_message})

else:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(name=message["role"], avatar='images/icons/ai_chef4.png' if message["role"] == "assistant" else 'images/icons/user.png'):
            st.markdown(message["content"])

    if st.session_state.user_input:
        # Get user input from state
        user_input = st.session_state.user_input

        # Clear user input in state
        st.session_state.user_input = ""

        # Add user message to chat history
        st.session_state.messages.append(
            {"role": "user", "content": user_input})

        # Display user message in chat message container
        with st.chat_message(name="user"):
            st.markdown(user_input)

        # Add delay
        time.sleep(0.5)

        model_response = ""

        # Display assistant response in chat message container
        with st.chat_message(name="ai", avatar='images/icons/ai_chef4.png'):
            message_placeholder = st.empty()
            chat_response = ""
            assistant_response = random.choice(
                [
                    "Gute Wahl! Lass mich ein leckeres Rezept für dich zaubern...",
                    "Ausgezeichnete Auswahl! Ich werde ein leckeres Rezept auf Basis deiner Zutaten erstellen...",
                    "Fantastisch! Deine ausgewählten Zutaten könnten ein köstliches Gericht ergeben. Das könnte etwas dauern...",
                    "Schöne Auswahl! Ich freue mich darauf, ein Rezept mit den von dir angegebenen Zutaten zu generieren...",
                    "Perfekt! Lass mich meine Magie wirken und dir ein fantastisches Rezept für deine ausgewählten Zutaten vorschlagen...",
                    "Ich bin dabei! Lass mich ein Rezept für dich generieren...",
                    "Alles klar, das könnte spannend werden! Ich werde ein Rezept für dich generieren...",
                ]
            )

            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.split():
                chat_response += chunk + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(chat_response + "▌")
            message_placeholder.markdown(chat_response)

        user_input_list = user_input.split(',')

        # Remove whitespaces
        user_input_list = [elem.strip() for elem in user_input_list]

        with st.chat_message(name="ai", avatar='images/icons/ai_chef4.png'):
            # Add gif to chat
            st.image('images/homer.gif')

        # Query language model
        model_response = generate_recipe(
            model,
            tokenizer,
            user_input_list,
        )

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": chat_response})
        st.session_state.messages.append(
            {"role": "assistant", "content": model_response})

        st.rerun()

    # Choose random welcome back message
    welcome_back_message = random.choice([
        "Ich hoffe, das war lecker! Was möchtest du als nächstes kochen?",
        "Ich hoffe, das hat geschmeckt! Was möchtest du als nächstes kochen?",
        "Ich hoffe, das war gut! Was möchtest du als nächstes kochen?",
        "Ich hoffe, das hat dir geschmeckt! Was möchtest du als nächstes kochen?",
    ])

    time.sleep(0.3)

    # Display welcome back message with fake typing effect
    with st.chat_message(name="ai", avatar='images/icons/ai_chef4.png'):
        message_placeholder = st.empty()
        full_response = ""

        for char in welcome_back_message:
            full_response += char
            message_placeholder.markdown(full_response)
            time.sleep(0.01)

    # Add welcome back message to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": welcome_back_message})
