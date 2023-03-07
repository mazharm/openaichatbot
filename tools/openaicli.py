from openai import Embedding, ChatCompletion

class OpenAICli:
    def __init__(self):
        return
            
    def get_response(self, messages, hyperparameters, model="gpt-3.5-turbo-0301"):
        """
        This the main function to send the chat context to the GPT model and get a response.
        returns the response and the perplexity of the response
        """

        response = ChatCompletion.create(
            model=model,
            messages=messages, 
            temperature=hyperparameters['temperature'],
            top_p=hyperparameters['top_p'], 
            frequency_penalty=hyperparameters['frequency_penalty'],
            presence_penalty=hyperparameters['presence_penalty'], 
            n=1,
            best_of=1)

        return response.choices[0].message.content.strip(), response.choices[0].attributes['perplexity']
    
    def get_embedding(self, text, model="text-similarity-davinci-001"):
        """
        This function returns the embedding of the text
        """
        text = text.replace("\n", " ")
        return Embedding.create(input = [text], model=model)['data'][0]['embedding']
    