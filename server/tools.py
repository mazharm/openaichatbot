"""
This module containts tools that assist the chatbot
"""
import os
import getpass
from datetime import datetime
from serpapi import GoogleSearch

class Tools:
    """
    This class contains tools that assist the chatbot
    """

    def __init__(self):
        self.username = getpass.getuser()

        self.serpapi_params = {
            "engine": "google",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": 2,
            "api_key": os.getenv("SERPAPI_API_KEY")
        }

        self.tools = {
            "search": {"description": "Search the web for information needed \
                       to answer the question.", "parameter": "search term"},
        }

        self.tool_apis = {
            "search": self.query_serpapi,
        }

    def call_tool(self, tool, parameter):
        """
        This function calls the tool with the given parameter
        """
        return self.tool_apis[tool](parameter)

    def get_tools(self):
        """
        This function returns the tools dictionary
        """
        return self.tools

    def get_username(self, parameter=None): # pylint: disable=unused-argument
        """
        This function returns the username
        """
        return self.username, "Local host"

    def __process_response(self, res: dict):
        """
        Process response from SerpAPI.
        """
        if "error" in res.keys():
            raise ValueError(f"Got error from SerpAPI: {res['error']}")
        if "answer_box" in res.keys() and "answer" in res["answer_box"].keys():
            toret = res["answer_box"]["answer"]
        elif "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret = res["answer_box"]["snippet"]
        elif (
            "answer_box" in res.keys()
            and "snippet_highlighted_words" in res["answer_box"].keys()
        ):
            toret = res["answer_box"]["snippet_highlighted_words"][0]
        elif (
            "sports_results" in res.keys()
            and "game_spotlight" in res["sports_results"].keys()
        ):
            toret = res["sports_results"]["game_spotlight"]
        elif (
            "knowledge_graph" in res.keys()
            and "description" in res["knowledge_graph"].keys()
        ):
            toret = res["knowledge_graph"]["description"]
        elif "snippet" in res["organic_results"][0].keys():
            toret = res["organic_results"][0]["snippet"]

        else:
            toret = "No good search result found"
        return toret

    def query_serpapi(self, question):
        """
        Query SerpAPI for the given question.
        """
        self.serpapi_params["q"] = question

        serpapi_client = GoogleSearch(self.serpapi_params)
        results = serpapi_client.get_dict()
        sources = [result["link"] for result in results["organic_results"]]

        response = self.__process_response(results)
        return response, sources

    def __get_time(self):
        """
        This function returns the current time
        """
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        return time_string

    def __get_date(self):
        """
        This function returns the current date
        """
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        return date_string

    def get_default_context(self):
        """
        This function returns the default context
        """
        date_time_string = self.__get_date()+" "+self.__get_time()
        default_context = "\nToday's date: "+date_time_string + \
            "\n Current User: "+self.username+"\n"

        return default_context
