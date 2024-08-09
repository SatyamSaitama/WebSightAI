import streamlit as st

def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit app
st.title("LLM Chatbot")

# Initialize the session state if not already initialized
if "history" not in st.session_state:
    st.session_state.history = []

# User input
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        # Generate response
        response = generate_response(user_input)
        # Update history
        st.session_state.history.append(f"You: {user_input}")
        st.session_state.history.append(f"Bot: {response}")
        # Clear input
        user_input = ""

# Display the chat history
for message in st.session_state.history:
    st.write(message)
