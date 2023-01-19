# openaichatbot
Simple chatbot client-server implementation. The server talks to OpenAI and Azure. The bot can use a public model or use a fine tuned model  that is trained using a fact database stored in Azure. The included python client allows you to (1) enable a text based interactive chat interface using public or private data (2) Store facts in Azure that can be used to train the finetune model.
I have also included a react client that talked to the server. In order to use it do the following: (a) Create a clean react client. (b) Replace App.js with the included App.js and copy jux.css into the same director. 
Using the jsh.py client or the react client requires you to first run the server. You also need to properly set up the environment variables in order to run the jsvr.py. 
