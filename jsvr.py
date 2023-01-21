""" jsvr.py handles the interactions with the Azure and Open AI APIs
This server is called by jsh and by a react front end.
It can be used to:
1. Store facts in the Azure blob storage
2. Create an OpenAI training file from the facts in the Azure blob storage
3. Enable an interactive chat session with the Open AI public or fine tuned model
"""
import os
from enum import Enum
import datetime
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import azurecli
import openaicli

# Set these values to your storage account and container
account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
client_id=os.environ.get("AZURE_CLIENT_ID")
client_secret=os.environ.get("AZURE_CLIENT_SECRET")
tenant_id=os.environ.get("AZURE_TENANT_ID")
PROMPT_DELIMITER = "###!###"
RESPONSE_DELIMITER = "###????###"

# Set these values to your OpenAI API key and model
oa_c = openaicli.OpenAICli(os.getenv("OPENAI_API_KEY"))
az_c = azurecli.AzureCli(account_name, container_name, account_url, \
        client_id, client_secret, tenant_id)
private_model = os.environ.get("OPENAI_PRIVATE_MODEL")
PUBLIC_MODEL = "text-davinci-003"

class ResponseType(Enum):
    """Enum for the type of response expected from the server"""
    TEXT = 1
    IMAGE = 2
    CODE = 3

class ConversationHistory():
    """Class to hold the conversation history for the public and private models"""
    def __init__(self):
        self.public_history = ""
        self.private_history = ""

    def reset_history(self):
        """Reset the conversation history for both models"""
        self.public_history = ""
        self.private_history = ""

    def get_conversation_history(self, history_type):
        """Get the conversation history for the specified model"""
        if history_type == "private":
            return self.private_history
        return self.public_history

    def set_conversation_history(self, history, history_type):
        """Set the conversation history for the specified model"""
        if history_type == "private":
            self.private_history = history
        else:
            self.public_history = history

def default_filename():
    """Create a default filename for the training file"""
    now = datetime.datetime.now()
    return f'training.{now.strftime("%Y%m%d%H%M%S")}.jsonl'

def default_blob_name():
    """Create a default filename for the blob"""
    now = datetime.datetime.now()
    return f'blob.{now.strftime("%Y%m%d%H%M%S")}.json'

def create_training_file():
    """Create a training file from the JSON objects in the Azure blob storage"""
    # Iterate through the blobs and print their contents to a file
    filename = default_filename()

    with open(filename, "w", encoding='utf8') as output_file:
        blobs = az_c.get_blob_list()

        # Iterate through the blobs
        for blob in blobs:

            # Retrieve the JSON object from the blob
            fact = az_c.get_json_from_blob(blob.name)

            facttext = {'prompt': fact['prompt']+PROMPT_DELIMITER, \
                 'completion': ' '+fact['completion']+RESPONSE_DELIMITER}

            # Print the JSON object to the file
            output_file.write(json.dumps(facttext))
            output_file.write("\n")

    # The output file should now contain the contents of all blobs, one per line

def delete_all_blobs():
    """Delete all blobs from the Azure blob storage"""
    blobs = az_c.get_blob_list()
    for blob in blobs:
        az_c.delete_blob(blob.name)

def get_text_response(text, conversation_type, model):
    """Get the text response from the OpenAI API"""

    c_h = conversation_history.get_conversation_history(conversation_type)

    # Add the text to the conversation history -- do this only for text and code
    c_h = c_h[-2000:] + "\nQuestion: "+ text
    print("Conversation:"+c_h)

    response_text = oa_c.get_text_response(c_h+PROMPT_DELIMITER, model)
    response_text = response_text.replace("Answer:", "", 1).lstrip()
    response_text = response_text.replace(RESPONSE_DELIMITER, "").lstrip()
    response_text = response_text.replace("?", "").lstrip()

    # Add the response to the conversation history
    c_h = c_h + "\nAnswer: "+ response_text
    conversation_history.set_conversation_history(c_h, conversation_type)

    return response_text

def get_response(text, conversation_type, model):
    """Get the response from the OpenAI API"""
    # get the response type in the form of text, image or code
    response_type = oa_c.classify(text, model)

    if "Code" in response_type:
        # generate code format it properly
        response=get_text_response(text, type, model).strip()
        rtype = ResponseType.CODE
    elif "Image" in response_type:
        # generate an image and format it properly
        response = oa_c.get_image_url(text)
        rtype = ResponseType.IMAGE
    else: #assume text for everything else
        response=get_text_response(text, conversation_type, model).strip()
        rtype = ResponseType.TEXT

    return rtype,response

def write_fact(jsonfact):
    """Write the fact to the Azure blob storage"""
    az_c.store_json_in_blob(jsonfact, default_blob_name())

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

CORS(app)

@app.route('/', methods=['POST'])
def handle_data():
    """Handle the data from the client"""
    print("Processing JSON data...")

    data = request.get_json()
    #data = json.loads(request.json)

    text = data['text']
    conversation_type = data['type']
    command = data['command']

    output = {}
    if command == "get-response":
        # Return the text as-is
        if conversation_type == 'public':
            model = PUBLIC_MODEL
        elif conversation_type == 'private':
            model = private_model
        else :
            model = conversation_type

        print("Model: " + model)
        rtype, response = get_response(text, type, model)
        output = {'type': rtype.name, 'text': response}

    elif command == "clear-history":
        # clear public and private conversation history
        conversation_history.reset_history()

        output = {'type': 'Text', 'text': "History cleared."}
    elif command == "write-fact":
        # write the fact to the fact file
        write_fact(text)
    elif command == "create-training-file":
        # create the training file
        create_training_file()
    elif command == "kill-all-facts":
        # delete all the facts
        # delete_all_blobs()
        print("Functionality is disabled to prevent accidental deletion of all facts.")
    else :
        print("Unknown command:" + command)

    returnoutput = jsonify(output)
    print("Returning: " + returnoutput.get_data(as_text=True))

    # Return the output as a JSON response
    return returnoutput

if __name__ == '__main__':
    conversation_history = ConversationHistory()
    app.run()
