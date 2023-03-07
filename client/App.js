import React, { useState, useEffect } from 'react';
import './App.css';
import Highlight from 'react-highlight';import SyntaxHighlighter from 'react-syntax-highlighter';
import { vs2015 } from 'react-syntax-highlighter/dist/cjs/styles/hljs';
import { CopyToClipboard } from 'react-copy-to-clipboard';

let recognition;

const ChatbotMessage = ({ message }) => {
  let returnval = ''
  const [copied, setCopied] = useState(false);
  const [highlight, setHighlight] = useState(false);

  if (message.type === 'Image') {
    returnval = <div className="chatbot-message">
                  <div className="chatbot-message-bubble">
                    <img src={message.text} alt="Image" />
                  </div>
                </div>
  }
  else if (message.type === 'Code') {
     returnval = <div className="chatbot-message">
                  <div>
                    <button onClick={() => setHighlight(!highlight)}>Highlight</button>
                    <div>
                    <CopyToClipboard text={message.text} onCopy={() => setCopied(true)}>
                      <button className="copy-button" disabled={copied}>
                      {copied ? 'Copied!' : 'Copy to Clipboard'}
                      </button>
                    </CopyToClipboard>
                    </div>
                  </div>
                  <div className="chatbot-message-bubble">
                    {highlight ? <SyntaxHighlighter style={vs2015}>{message.text}</SyntaxHighlighter> 
                      : <pre>{message.text}</pre>}
                  </div>
                </div>
  }
  else { // assume text
     returnval = <div className="chatbot-message">
                  <div className="chatbot-message-bubble">
                  {message.text}
                  </div>
                </div>
  }
  
  return (returnval);
}

const UserMessage = ({ message }) => {
  return (
    <div className="user-message">
      <div className="user-message-bubble">
        {message.text}
      </div>
    </div>
  );
}

const ChatbotConversation = ({ messages }) => {
  return (
    <div className="chatbot-conversation">
      {messages.map((message, index) => {
        if (message.sender === 'chatbot') {
          return <ChatbotMessage key={index} message={message} />
        } else {
          return <UserMessage key={index} message={message} />
        }
      })}
    </div>
  );
}

const ChatbotRequestReplyInterface = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'chatbot',
      type: 'text',
      text: 'Hello, how can I help you today?'
    }
  ]);

  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [isAudioEnabled, setAudioEnabled] = useState(false);
  const buttonRef = React.useRef(null);
  const synth = window.speechSynthesis; 

  function startRecognition() {
    if (!recognition) {
      // If recognition has not yet been initialized, create a new recognition object
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.maxAlternatives = 1;
      recognition.addEventListener('result', ({ results }) => {
        setInput(results[0][0].transcript);
        buttonRef.current.click();
      });
  
      console.log('starting recognition')
      recognition.start();
    } else if (!recognition.continuous) {
      // If recognition is not already running, start it
      console.log('starting recognition')
      recognition.start();
    }
  }

  function stopRecognition()
  {
    if (recognition.continuous) {
      recognition.stop();
      recognition.continuous = false;
      recognition.interimResults = false;
    }
  }

  function toggleAudioEnabled(event) {
    if (event.target.checked) {
      setAudioEnabled(true);
      startRecognition();
    }
    else {
      setAudioEnabled(false);
      stopRecognition();
    }
  }

  function speakOutput(type, text) {
    console.log('audio enabled' + isAudioEnabled)
    if (isAudioEnabled) {
      if (type === 'Text') {
      console.log('speaking text:'+text)
      const utterance = new SpeechSynthesisUtterance(text);
      synth.speak(utterance);
      }
    }
  }

  const call_server = (input, command) => {
    console.log('input= %s, command=%s', input, command)
    const data = {text: input, command: command};

    fetch('http://localhost:5000', {
      method: 'POST',
      headers: {'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    .then((response) => response.json())
    .then((result) => {
        const output = result;

        console.log('output:'+output)

        if (command === 'get-response') {  
        setMessages([...messages, { sender: 'user', text: input }, 
                                  {sender: 'chatbot', type: output.type, text: output.text}]);
   
        speakOutput(output.type, output.text, isAudioEnabled);
        setInput('');
        }
      })
      .catch((error) => {
        console.error(error);
      });
  }

  const handleSubmit = (event) => {
    console.log('audio enabled' + isAudioEnabled)
    console.log('submitting', input)

    event.preventDefault();
    const regex = /@fact @question: (.*?) @answer: (.*)/i;

    let result = regex.exec(input);
    if (result) {
      const [, question, answer] = result;

      if (question && answer) {
        console.log(question); 
        console.log(answer);
      } 
      setInput('');
    }
    else
      call_server(input, 'get-response');
  };


  const handleClearHistory = () => {
    setMessages([]);
    call_server('clear', 'clear-history');
  }

  return (
    <div className="chatbot-request-reply-interface">
      <div className="chatbot-header">
        <button
          className="clear-history-button"
          onClick={handleClearHistory}
        >
          Clear History
        </button>
        <label className="toggle-listening-button">
          <input
            id="mute-toggle"
            type="checkbox"
            checked={isAudioEnabled}
            onChange={toggleAudioEnabled}
          />
          <div className="toggle-listening-button-handle" />
        </label>
      </div>
      <div className='chatbot-messages'>
        <ChatbotConversation messages={messages} />
      </div>
      <div className="chatbot-footer">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={event => setInput(event.target.value)}
            placeholder="Enter your message..."
            ref={buttonRef}
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

export default ChatbotRequestReplyInterface;
