import os
import time
import webbrowser
import random
import io
from enum import Enum
from flask import Flask, request, jsonify
from flask_cors import CORS
import azurecli
import openaicli
import random
import datetime
import json

# Set these values to your storage account and container
account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
container_name = os.environ.get("AZURE_STORAGE_CONTAINER_NAME")
account_url = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
client_id=os.environ.get("AZURE_CLIENT_ID")
client_secret=os.environ.get("AZURE_CLIENT_SECRET")
tenant_id=os.environ.get("AZURE_TENANT_ID")
prompt_delimiter = "###!###"
response_delimiter = "###????###"

# Set these values to your OpenAI API key and model
oac = openaicli.OpenAICli(os.getenv("OPENAI_API_KEY"))
azc = azurecli.AzureCli(account_name, container_name, account_url, client_id, client_secret, tenant_id)
private_model = os.environ.get("OPENAI_PRIVATE_MODEL")
public_model = "text-davinci-003"

class ResponseType(Enum):
    Text = 1
    Image = 2
    Code = 3

public_conversation_history=""
private_conversation_history=""

def default_filename():
  now = datetime.datetime.now()
  return f'training.{now.strftime("%Y%m%d%H%M%S")}.jsonl'

def default_blob_name():
  now = datetime.datetime.now()
  return f'blob.{now.strftime("%Y%m%d%H%M%S")}.json'

# Create a function to retrieve all JSON objects from all blobs
def create_training_file():
    # Iterate through the blobs and print their contents to a file
    filename = default_filename()

    with open(filename, "w") as output_file:
        blobs = azc.get_blob_list()
        
        # Iterate through the blobs
        for blob in blobs:

            # Retrieve the JSON object from the blob
            fact = azc.get_json_from_blob(blob.name)
            
            facttext = {'prompt': fact['prompt']+prompt_delimiter, 'completion': ' '+fact['completion']+response_delimiter}

            # Print the JSON object to the file
            output_file.write(json.dumps(facttext))
            output_file.write("\n")

    # The output file should now contain the contents of all blobs, one per line

def delete_all_blobs():
    blobs = azc.get_blob_list()
    for blob in blobs:
        azc.delete_blob(blob.name)

def get_text_response(text, type, model):
  global public_conversation_history
  global private_conversation_history
    
  if type == "private":
      conversation_history = private_conversation_history
  else:
      conversation_history = public_conversation_history

  # Add the text to the conversation history -- do this only for text and code
  conversation_history = conversation_history[-2000:] + "\nQuestion: "+ text 
  print("Conversation:"+conversation_history)

  responsetext = oac.get_text_response(conversation_history+prompt_delimiter, model)
  responsetext = responsetext.replace("Answer:", "", 1).lstrip()
  responsetext = responsetext.replace(response_delimiter, "").lstrip()
  responsetext = responsetext.replace("?", "").lstrip()
    
  # Add the response to the conversation history
  conversation_history = conversation_history + "\nAnswer: "+ responsetext
  if type == "private":
    private_conversation_history = conversation_history 
  else:
    public_conversation_history = conversation_history

  return (responsetext)

def get_response(text, type, model):         
    # get the response type in the form of text, image or code
    responsetype = oac.classify(text, model)

    if responsetype.__contains__("Code"):
      # generate code format it properly
      response=get_text_response(text, type, model).strip()
      rtype = ResponseType.Code
    elif responsetype.__contains__("Image"):
      # generate an image and format it properly
      response = oac.get_image_url(text)
      rtype = ResponseType.Image
    else: #assume text for everything else
      response=get_text_response(text, type, model).strip()
      rtype = ResponseType.Text

    return rtype,response

def write_fact(jsonfact):
    azc.store_json_in_blob(jsonfact, default_blob_name())

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

CORS(app)

@app.route('/', methods=['POST'])
def handle_data():
    print("Processing JSON data...")

    data = request.get_json()
    #data = json.loads(request.json)

    text = data['text']
    type = data['type']
    command = data['command']

    output = {}
    if command == "get-response":
        # Return the text as-is
        if (type == 'public'):
            model = public_model
        elif (type == 'private'):
            model = private_model
        else :
            model = type

        print("Model: " + model)
        rtype, response = get_response(text, type, model)
        output = {'type': rtype.name, 'text': response}

    elif command == "clear-history":
        global public_conversation_history
        global private_conversation_history

        # clear public and private conversation history
        public_conversation_history = ""
        private_conversation_history = ""

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
    app.run()
