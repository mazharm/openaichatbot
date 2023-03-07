""" jsvr.py handles the interactions with the Azure and Open AI APIs
This server is called by jsh and by a react front end.
It can be used to:
1. Store facts in the Azure blob storage
2. Create an OpenAI training file from the facts in the Azure blob storage
3. Enable an interactive chat session with the Open AI public or fine tuned model
"""
import datetime
import json
import argparse
import ast
from flask import Flask, request, jsonify
from flask_cors import CORS
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from .azurecli import AzureCli
from .openaicli import OpenAICli
from .conversation import Conversation
from .pineconecli import PineconeCli

oai = OpenAICli()
con = Conversation()
azc = AzureCli()
pc = PineconeCli()
VERBOSE = False


def is_python_code(text):
    """
    Check if the text is valid Python code
    """
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def format_code(code):
    """
    Format the code using Pygments
    """
    lexer = get_lexer_by_name("python")
    highlighted_code = highlight(code, lexer, HtmlFormatter())

    # Get the CSS rules for the highlighted code
    css = HtmlFormatter().get_style_defs(".highlight")

    # Generate the HTML document
    html = f"<html><head><style>\n{css}\n</style></head>\n<body>\n\
            {highlighted_code}\n</body></html>"

    return html


def loadfacts():
    """
    Load the facts from the JSONL file
    """
    # Open the JSONL file in read mode
    with open("output.jsonl", 'r', encoding='utf8') as f:
        # Initialize an empty list to store the parsed JSON objects
        json_list = []

        # Iterate through each line in the file
        for line in f:
            # Parse the JSON object from the line
            json_obj = json.loads(line)
            # Add the parsed JSON object to the list
            json_list.append(json_obj)

        return json_list


# Define a function to generate embeddings for a list of texts using OpenAI's GPT-3 model
def generate_embedding_vectors(facts):
    """
    Generate embedding vectors for a list of facts
    """
    vectors = []
    for index, fact in enumerate(facts):
        fact_text = fact['fact']
        embedding = oai.get_embedding(fact_text)
        vector = (f"{index}", embedding, fact)
        vectors.append(vector)
    return vectors


def facts_to_embeddings():
    """
    Generate embedding vectors for the facts in the JSONL file
    """
    facts = loadfacts()
    embedding_vectors = generate_embedding_vectors(facts)
    pc.upsert_vectors(embedding_vectors)


def default_filename():
    """
    Create a default filename for the training file
    """
    now = datetime.datetime.now()
    return f'training.{now.strftime("%Y%m%d%H%M%S")}.jsonl'


def default_blob_name():
    """
    Create a default filename for the blob
    """
    now = datetime.datetime.now()
    return f'blob.{now.strftime("%Y%m%d%H%M%S")}.json'


def create_training_file():
    """
    Create a training file from the JSON objects in the Azure blob storage
    """
    # Iterate through the blobs and print their contents to a file
    filename = default_filename()

    with open(filename, "w", encoding='utf8') as output_file:
        blobs = azc.get_blob_list()

        # Iterate through the blobs
        for blob in blobs:

            # Retrieve the JSON object from the blob
            fact = azc.get_json_from_blob(blob.name)

            facttext = {'prompt': fact['prompt'],
                        'completion': ' '+fact['completion']}

            # Print the JSON object to the file
            output_file.write(json.dumps(facttext))
            output_file.write("\n")

    # The output file should now contain the contents of all blobs, one per line


def delete_all_blobs():
    """
    Delete all blobs from the Azure blob storage
    """
    blobs = azc.get_blob_list()
    for blob in blobs:
        azc.delete_blob(blob.name)


def get_image(text):
    """
    Get an image from the Open AI API
    """
    # generate an image and format it properly
    response = oai.get_image(text)
    return response


def get_response(text):
    """
    Get a response from the Open AI API
    """
    response = con.get_response(text, VERBOSE).strip()

    if is_python_code(response):
        response = format_code(response)

    return response


def write_fact(jsonfact):
    """
    Write the fact to the Azure blob storage
    """
    azc.store_json_in_blob(jsonfact, default_blob_name())


app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

CORS(app)


@app.route('/', methods=['POST'])
def handle_data():
    """
    Handle the data from the client
    """
    print("Processing JSON data...")

    data = request.get_json()
    # data = json.loads(request.json)

    text = data['text']
    command = data['command']

    output = {}
    if command == "get-response":
        # Return the text as-is
        rtype, response = get_response(text)
        output = {'type': rtype.name, 'text': response}
    elif command == "clear-history":
        # clear public and private conversation history
        con.reset()
        output = {'type': 'Text', 'text': "History cleared."}
    elif command == "write-fact":
        # write the fact to the fact file
        write_fact(text)
    elif command == "kill-all-facts":
        # delete all the facts
        # delete_all_blobs()
        print("Functionality is disabled to prevent accidental deletion of all facts.")
    else:
        print("Unknown command:" + command)

    returnoutput = jsonify(output)
    print("Returning: " + returnoutput.get_data(as_text=True))

    # Return the output as a JSON response
    return returnoutput


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True
        print("Verbose logging enabled.")

    app.run()
