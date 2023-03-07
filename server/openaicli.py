"""
This module is used to interact with the OpenAI API
"""
from openai import Embedding, Image, ChatCompletion

class OpenAICli:
    """
    This class is used to interact with the OpenAI API
    """
    temperature=0.3
    top_p=1
    frequency_penalty=0.0 
    presence_penalty=0.0 
    model="gpt-3.5-turbo-0301"
    impage_size="1024x1024"
    
    def __init__(self):
        return

    def get_image(self, text):
        """
        This function is used to generate an image from a piece of text
        """
        response = Image.create(prompt=text, n=2, size=self.impage_size)
        return response.data[0].url

    def get_response(self, messages):
        """
        This the main function to send the chat context to the GPT model and get a response.
        """
        response = ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty)

        return response.choices[0].message.content.strip()

    def get_response_from_text(self, text):
        """
        This function is used when you need a response for a single piece of text
        """

        response = ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{text}"},
            ])

        return response.choices[0].message.content.strip()

    def get_embedding(self, text, model="text-similarity-davinci-001"):
        """
        This function is used to generate an embedding vector for a piece of text
        """
        text = text.replace("\n", " ")
        return Embedding.create(input=[text], model=model)['data'][0]['embedding']
