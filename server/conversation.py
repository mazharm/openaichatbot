"""
This module contains the class that encapsulates the conversation history and context
"""
import traceback
import re
from .openaicli import OpenAICli
from .prompt import Prompt
from .pineconecli import PineconeCli
from .tools import Tools


class Conversation:
    """
    This class is used to encapsulate the conversation history and context
    """
    conversation_summary = []
    unsummarized_conversations = 0
    # Initialize conversation history with an empty list
    conversation_history = []
    oai = OpenAICli()
    pc = PineconeCli()
    tls = Tools()
    default_context = tls.get_default_context()
    prompt = Prompt()
    intro_prompt = prompt.get_intro_prompt()

    def __init__(self):
        return

    def reset(self):
        """
        This function resets the conversation history
        """
        self.conversation_summary = []
        self.unsummarized_conversations = 0
        self.conversation_history = []

    # Define function to summarize conversation history using GPT model
    def summarize_conversations(self):
        """
        This function summarizes the conversation history using GPT model
        """
        summarizeprompt = self.prompt.get_summarize_conversation_prompt() + \
            self.conversation_history
        new_summarized_conversation = self.oai.get_response(summarizeprompt)

        formatted_chat_summary = self.prompt.get_summary_prompt(
            new_summarized_conversation)

        return formatted_chat_summary

    def get_conversation_history(self):
        """
        This function returns the conversation history
        """
        return self.conversation_summary+self.conversation_history

    def _add_conversation(self, question, answer):
        """
        This function adds the question and answer to the conversation history
        """
        if answer is not None and answer != "":
            # conversation contains the question and answer
            self.conversation_history += self.prompt.get_qa_history_prompt(
                question=question, answer=answer)
            self.unsummarized_conversations += 1

            if self.unsummarized_conversations > 10:
                # Summarize older conversations using GPT model
                self.conversation_summary = self.summarize_conversations()

                # Keep only the last 5 (*2) conversations in the history
                self.conversation_history = self.conversation_history[-10:]

                self.unsummarized_conversations = 0

    def parse_tool(self, text):
        """
        This function parses the text to see if it contains a tool invocation
        """
        match = re.search(r"\$search\(\s*(['\"])?([^'\"]+)\1?\s*\)", text)
        if match is not None:
            tool_name = "search"
            tool_param = match.group(2)

            if tool_name is not None and tool_param is not None:
                return True, tool_name, tool_param

        return False, None, None

    def _process_response(self, response):
        """
        This function processes the response to see if it contains a tool invocation
        """
        is_tool, tool_name, tool_param = self.parse_tool(response)

        if is_tool:
            # Call the tool with the given parameter
            tool_output, source = self.tls.call_tool(tool_name, tool_param)

            if tool_output is not None:
                # Add the question and answer to the conversation history
                self._add_conversation(tool_param, tool_output)
                print("Source:", source)
                return False

        return True

    def _get_prompt(self, question, context):
        """
        This used is used to format the prompt based on the provided arguments
        The format of the prompt is as follows:
        
        Instructions: in CHAT_INTRO -- this is a set of instructions to the model
        
        Chat summary: in CHAT_SUMMARY -- a summary of the conversation history used 
        for capturing the context of older conversations
        
        QA history including tool invocations: in CHAT_QA_HISTORY + CHAT_TOOL_INVOCATION 
        these are intermingled based on when the tool was needed
        
        Chat Q: in CHAT_Q -- this is the question that the user is asking
        """
        self.default_context = self.tls.get_default_context()
        full_prompt = self.intro_prompt + self.prompt.get_context_prompt(context) +\
            self.conversation_summary+self.conversation_history +\
            self.prompt.get_q_prompt(question, self.default_context)

        return full_prompt

    def get_response(self, text, verbose=False):
        """
        Get the response from the OpenAI API
        """
        try:
            response = ""

            # Get user input
            context = self.pc.find_match(text)

            for _ in range(2):
                my_prompt = self._get_prompt(text, context)

                if verbose:
                    print("Prompt=", my_prompt)
                response = self.oai.get_response(my_prompt)
                if self._process_response(response):
                    break

            if response is not None and response != "":
                # Add the question and answer to the conversation history
                self._add_conversation(text, response)
        except Exception as err: # pylint: disable=broad-except
            print("Error:", err)
            traceback.print_exc()
            response = "Sorry, I hit an internal error. Please try again."

        return response
