"""
This module is used to format the prompt for the GPT model
"""
CHAT_INTRO = [
    {"role": "system", "content": "You are a helpful assistant. Your job is to answer questions \
     based on knowledge provided in the context or conversation history"},
    {"role": "system", "content": "Use a conversational tone. Avoid being tentative and reminding \
     the user that you are an AI model"},
]

CHAT_SUMMARY = [
    {"role": "system", "content": "This is a summary of older conversations organized by \
     topic:{conversation_summary}. Use it to answer the question below"},
]

CHAT_CONTEXT = [
    {"role": "system", "content": "this is some background information that might be \
     helpful to answer the questions: {context}"},
]

CHAT_QA_HISTORY = [
    {"role": "user", "content": "{question}"},
    {"role": "assistant", "content": "{answer}"},
]

CHAT_Q = [
    {"role": "system", "content": "this is some context for the conversation: {standard_context}"},
    {"role": "system", "content": "Ask me any question you have. If I am unable to answer \
     your question, I will prompt you to perform a search by including the $search() \
     function in your response. I will place the search term inside the parentheses, \
     like this: $search(search term). This will ensure that I can reliably prompt you \
     to search for information. Thank you! I will not give up without at least \
     attempting a search."},
    {"role": "user", "content": "Question: {question}"},
]

# CHAT_QA_HISTORY is appended to this prompt to get the chat summary
CHAT_SUMMARIZE_CONVERSATION = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "system", "content": "Summarize the conversation below. \
     When the conversation involves multiple people or topics, summarize \
     each topic separately. Response should be plain text"},
]


class Prompt:
    """
    This class is used to format the prompt based on the provided arguments
    The format of the prompt is as follows:

    Instructions: in CHAT_INTRO -- this is a set of instructions to the model

    Chat summary: in CHAT_SUMMARY -- a summary of the conversation history used
    for capturing the context of older conversations

    QA history including tool invocations: in CHAT_QA_HISTORY + CHAT_TOOL_INVOCATION
    these are intermingled based on when the tool was needed

    Chat Q: in CHAT_Q -- this is the question that the user is asking
    """

    def __init__(self):
        self.standard_context = CHAT_INTRO

    def get_intro_prompt(self):
        """
        This function returns the intro prompt
        """
        return self.standard_context

    def get_summary_prompt(self, conversation_summary):
        """
        This function returns the summary prompt
        """
        formatted_chat_summary = [
            {"role": blob["role"], "content": blob["content"].
             format(conversation_summary=conversation_summary)} for blob in CHAT_SUMMARY]
        return formatted_chat_summary

    def get_qa_history_prompt(self, question, answer):
        """
        This function returns the QA history prompt
        """
        formatted_qa_history = [
            {"role": blob["role"], "content": blob["content"]
             .format(question=question, answer=answer)} for blob in CHAT_QA_HISTORY]
        return formatted_qa_history

    def get_context_prompt(self, context):
        """
        This function returns the context prompt
        """
        formatted_chat_context = [
            {"role": blob["role"], "content": blob["content"]
             .format(context=context)} for blob in CHAT_CONTEXT]
        return formatted_chat_context

    def get_q_prompt(self, question, standard_context):
        """
        This function returns the Q prompt
        """
        formatted_chat_q = [
            {"role": blob["role"], "content": blob["content"]
             .format(question=question, standard_context=standard_context)} for blob in CHAT_Q]
        return formatted_chat_q

    def get_summarize_conversation_prompt(self):
        """
        This function returns the summarize conversation prompt
        """
        return CHAT_SUMMARIZE_CONVERSATION
