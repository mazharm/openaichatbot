import os
import io
import argparse
import json
import requests

## This is a command line client to jsvr.py
## It can be used to create a training file from the cloud and upload facts to the cloud
## It can also be used to start an interactive chat session with the cloud

# this function calls jsvr. Possible commands are:
# get-response: get a response from the cloud
# clear-history: clear the chat history
# write-fact: write a fact to the cloud
def call_server(input, mode, command):
    url = 'http://localhost:5000'
    headers = {'Content-Type': 'application/json'}
    data = {'text': input, 'type': mode, 'command': command}
    
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = json.loads(response.text)
    else:
        print(f'Error: {response.text}')
        result = ""

    return result

def upload_facts(filename):
  with io.open(filename) as f:
    for line in f:
      fact = json.loads(line)
      call_server(fact, 'public', 'write-fact')

# fact delimiters get added during training file generation
def interactive_fact_upload():
  while True:
    question = input("Question> ")
    answer = input("Answer> ")
    text = {'prompt': question, 'completion': answer}
    call_server(text, 'private', 'write-fact')

def create_training_file(newer_than):
  output = call_server(newer_than, '', 'create-training-file')
  # url = output['text'] -- need to implement this in the future
  # return url

def interactive_chat(model):
  while True:
    text = input("JSh> ")
    output = call_server(text, model, 'get-response')
    print(output['text'])

def clear_history():
  output = call_server('', '', 'clear-history')
  print(output['text'])

if __name__ == "__main__":
  custom_model = 'public'

  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--create-training-file', action='store_true', help='Create a training file from cloud (default all data)')
  parser.add_argument('-n', '--newer-than', type=str, nargs='?', default='1900-01-01')
  parser.add_argument('-u', '--upload-facts', action='store_true', help='Upload facts to cloud default: interactive, use -f to specify file')
  parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive mode')
  parser.add_argument('-ch', '--clear-history', action='store_true', help='Clear the chat history')
  parser.add_argument('-f', '--facts-file', type=str, default='facts.json', help='Specify the facts file to use (remove custom delimiters)')
  parser.add_argument('-m', '--model', type=str, default='public', help='Specify the model to use (public, private or custom model name))')
  parser.add_argument('-k', '--kill-all-facts', action='store_true', help='Kill all facts in the cloud (use with care!)')

  args = parser.parse_args()
  if args.model:
    custom_model = args.model
    print(f'Using custom model {custom_model}')

  if args.create_training_file:
    # create the training file
    print(f'Creating training file with data newer than {args.newer_than}...')
    training_file = create_training_file(args.newer_than)
    print('Training file url:', training_file)
  elif args.clear_history:
    # clear the chat history
    print('Clearing chat history')
    clear_history()
  elif args.interactive:
    if args.upload_facts:
      print('starting interactive fact upload')
      interactive_fact_upload()
    else :
      print('starting interactive chat')
      interactive_chat(custom_model)
  elif args.upload_facts:
    # upload the facts
    print(f'Uploading facts from file {args.facts_file} to cloud...')
    upload_facts(args.facts_file) 
  elif args.kill_all_facts:
    # kill all facts
    print('Killing all facts in the cloud')
    call_server('', '', 'kill-all-facts')
  else:
    print('No command specified')
 

