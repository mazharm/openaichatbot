""" jsh.py is a command line client to jsvr.py. It can be used to:
1. Upload facts to the cloud (Azure blob storage)
2. Create a training file from the cloud (from Azure blob storage)
3. Start an interactive chat session using the Open AI public or fine tuned model

The interactions with the Azure and Open AI APIs are handled by jsvr.py. This logic is
encapsulated in the server to allow it to be callable by jsh and by a react front end.
"""
import io
import argparse
import json
import requests

JSVR_URL = 'http://localhost:5000'

def call_server(input_text, mode, command):
    """This is a command line client to jsvr.py
    It can be used to create a training file from the cloud and upload facts to the cloud
    It can also be used to start an interactive chat session with the cloud

    This function calls jsvr. Possible commands are:
    get-response: get a response from the cloud
    clear-history: clear the chat history
    write-fact: write a fact to the cloud
    """
    headers = {'Content-Type': 'application/json'}
    data = {'text': input_text, 'type': mode, 'command': command}

    response = requests.post(JSVR_URL, headers=headers, json=data, timeout=10)

    if response.status_code == 200:
        result = json.loads(response.text)
    else:
        print(f'Error: {response.text}')
        result = ""

    return result

def upload_facts(filename):
    """
    Upload facts from the given filename to the cloud (Azure blob storage)
    The facts file should be a jsonl file with one fact per line
    """
    print(f'Uploading facts from file {filename} to cloud...')
    with io.open(filename, encoding='utf8') as f_lines:
        for line in f_lines:
            fact = json.loads(line)
            call_server(fact, 'private', 'write-fact')

def interactive_fact_upload():
    """
    Upload facts to the cloud (Azure blob storage) interactively
    fact delimiters are use to separate facts in the training file
    they are inserted by jsvr.py when creating the training file
    """
    while True:
        question = input("Question> ")
        answer = input("Answer> ")
        text = {'prompt': question, 'completion': answer}
        call_server(text, 'private', 'write-fact')

def create_training_file(newer_than):
    """
    Create an Open AI training file from the facts stored in the cloud (Azure blob storage)
    """
    print(f'Creating training file with data newer than {args.newer_than}...')
    call_server(newer_than, '', 'create-training-file')

def interactive_chat(model):
    """
    Start an interactive chat session with the Open AI cloud
    """
    while True:
        text = input("JSh> ")
        output = call_server(text, model, 'get-response')
        print(output['text'])

def clear_history():
    """
    Clear the interactive chat history in jsvr.py
    this is different from the kill-all-facts command which deletes all facts in the cloud
    The chat history is transient and is not stored in the cloud. It is best to clear this history
    when starting a conversation about a new topic
    """
    print('Clearing chat history')
    output = call_server('', '', 'clear-history')
    print(output['text'])

def kill_all_facts():
    """
    kill all facts -- dangerous function -- use with care!
    disabled by default in jsvr.py to prevent accidental deletion of cloud data
    """
    print('Killing all facts in the cloud')
    output = call_server('', '', 'kill-all-facts')
    print(output['text'])

if __name__ == "__main__":
    CUSTOM_MODEL = 'public'

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--create-training-file', action='store_true', \
                  help='Create a training file from cloud (default all data)')
    parser.add_argument('-n', '--newer-than', type=str, nargs='?', default='1900-01-01')
    parser.add_argument('-u', '--upload-facts', action='store_true', \
                  help='Upload facts to cloud default: interactive, use -f to specify file')
    parser.add_argument('-i', '--interactive', action='store_true', \
                  help='Start interactive mode')
    parser.add_argument('-ch', '--clear-history', action='store_true', \
                  help='Clear the chat history')
    parser.add_argument('-f', '--facts-file', type=str, default='facts.json', \
                  help='Specify the facts file to use (remove custom delimiters)')
    parser.add_argument('-m', '--model', type=str, default='public', \
                  help='Specify the model to use (public, private or custom model name))')
    parser.add_argument('-k', '--kill-all-facts', action='store_true', \
                  help='Kill all facts in the cloud (use with care!)')

    args = parser.parse_args()
    if args.model:
        CUSTOM_MODEL = args.model
        print(f'Using custom model {CUSTOM_MODEL}')

    if args.create_training_file:
        create_training_file(args.newer_than)
    elif args.clear_history:
        clear_history()
    elif args.interactive:
        if args.upload_facts:
            print('starting interactive fact upload')
            interactive_fact_upload()
        else :
            print('starting interactive chat')
            interactive_chat(CUSTOM_MODEL)
    elif args.upload_facts:
        upload_facts(args.facts_file)
    elif args.kill_all_facts:
        kill_all_facts()
    else:
        print('No command specified')
  # End of file
