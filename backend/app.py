from dotenv import load_dotenv
import os
import google.generativeai as genai
from flask import Flask, request, jsonify,session,send_file
from rag import *
from flask_cors import CORS
load_dotenv()


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction="You are a website builder you return html,css,js code for a website prompt.Don't give any explanation of the code.Return code as the response.",
)
history = []
app = Flask(__name__)

CORS(app)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data['prompt']
    rag = search(prompt)
    chat = model.start_chat(history=history)
    
    response = chat.send_message(f"""if this prompt #{prompt}# by the user is requesting for a website Return this *exact* code  #{rag}#  as your response.  Else if the prompt  requesting for the  changing the component of the  website (that you provided in previous response)then only modify the code and return the modified code.Else converse with the user and tell them that you are a website builder and you return html,css,js code for a website prompt.
    Note***                             
    Don't give any explanation of the code.Return code as the response for user to copy easily .***""")
    
    code = response.text
    
    # Clean up the markdown
    if "```html" in code:
        code = code.replace("```html\n", "").replace("\n```", "").replace("\\n", "\n").replace("```html", "")
       
        
    history.append({
        "role": "model",
        "parts": [
            code,
        ],
        })
    f = open("output.html", "w")
    f.write(code)
    f.close()
    return jsonify({"response": code})

@app.route('/reset', methods=['POST'])
def reset():
    history.clear()
    return jsonify({"response": "History cleared"})



if __name__ == '__main__':
    app.run(debug=True)