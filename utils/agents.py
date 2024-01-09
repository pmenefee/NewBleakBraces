# Standard library imports
import logging

# Third-party imports
import openai

# Local imports
from config.api_keys import oai_api_key

# Configure logging with structured formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize the OpenAI client with API key
openai.api_key = oai_api_key

def openai_chat_completions(model, messages):
    """
    Utility function to interact with OpenAI's chat API.

    :param model: The model to be used for the OpenAI completion.
    :param messages: The messages to be sent for the completion.
    :return: The content of the response or None if an error occurs.
    """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content if response.choices else None
    except Exception as e:
        logging.error("Error in OpenAI interaction", exc_info=True)
        return None

def agent_summarizer(description):
    """
    Generate a summary for a given video description using OpenAI's GPT-3.5 Turbo model.

    :param description: A string representing the YouTube video description.
    :return: A string summary of the description.
    """
    try:
        model = "gpt-3.5-turbo"
        prompt = "Provide a short summary of the following YouTube video description. The summary should be concise.\nDescription:"
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": description}]

        result = openai_chat_completions(model, messages)

        if result:
            logging.info(f"Summary generated successfully for description: {description[:50]}...")
            return result
        else:
            logging.warning("OpenAI response was empty while generating summary.")
            return "Failed to generate summary. Response is empty."
    except Exception as e:
        logging.error("Error in agent_summarizer", exc_info=True)
        return "An error occurred during summary generation."

def agent_expander(user_topic):
    """
    Generate subtopics from the user's input using OpenAI's GPT-3.5 Turbo model.

    :param user_topic: A string representing the user's topic of interest.
    :return: A string of subtopics generated based on the user's topic.
    """
    try:
        model = "gpt-3.5-turbo"
        prompt = "Produce sub-topics for the following user's topic of interest. The sub-topics should be precise.\nDescription:"
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": user_topic}]

        result = openai_chat_completions(model, messages)

        if result:
            logging.info(f"Generated subtopics for topic: {user_topic[:50]}...")
            return result
        else:
            logging.warning("Failed to generate subtopics. Response is empty.")
            return "Failed to generate subtopics. Response is empty."
    except Exception as e:
        logging.error("Error in agent_expander", exc_info=True)
        return "An error occurred during subtopic generation."
