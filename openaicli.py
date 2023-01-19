import os
import openai

class OpenAICli:
    def __init__(self, api_key):
        openai.api_key = api_key

    def classify(self, text, model):
        prompttext = "classify expected response from this text into Code,Text or Image \"" + text + "\"" 
        response = openai.Completion.create(model=model, prompt=prompttext, temperature=0, max_tokens=50)
        return response.choices[0].text

    def get_image_url(self, text):
        response = openai.Image.create(prompt=text, n=2, size="1024x1024")
        return response.data[0].url
            
    def get_text_response(self, text, model):
        response = openai.Completion.create(model=model, prompt=text, temperature=0, max_tokens=100)
        return response.choices[0].text
