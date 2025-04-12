import google.generativeai as genai
import os

def configure_api():
    api_key = "AIzaSyDbSOCsLjSVrHwoULWqv_1STArQU9ZGvMI"
    genai.configure(api_key=api_key)

def setup_model():
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.5,
        "top_k": 1,
        "max_output_tokens": 2000
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    return model

def summarize_text(model, input_text):
    convo = model.start_chat(history=[])
    convo.send_message(input_text)
    return convo.last.text
