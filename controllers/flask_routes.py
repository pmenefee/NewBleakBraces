# Flask and JSON imports
from flask import jsonify, request

# Utility, services, and controllers imports
from services.data_processing import embed_summaries_from_firestore, download_csv
from controllers.subprocess_controller import extract_youtube_ids
from controllers.video_routes import upload_file, download_videos, process_extracted_videos
from controllers.user_interaction_routes import index, query, upload_screen
from utils.agents import agent_expander
from services.pinecone import query_pinecone
from utils.youtube_api import youtube_search
from config.api_keys import yt_api_key

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_progress():
    """
    Endpoint to track and return the progress of processing.
    """
    # Implement appropriate progress tracking here
    return jsonify({'progress': 0})

def handle_agent_expander():
    """
    Endpoint to handle expanding a user's topic into subtopics using an agent.
    """
    data = request.json
    user_topic = data.get('topic')

    if not user_topic:
        logging.warning("No topic provided in handle_agent_expander")
        return jsonify({'error': 'No topic provided'}), 400

    subtopics = agent_expander(user_topic)
    return jsonify({'subTopics': subtopics})

def handle_query_pinecone():
    """
    Endpoint to query Pinecone for videos related to a given subtopic.
    """
    data = request.json
    subtopic = data.get('subTopic')

    if not subtopic:
        logging.warning("No subtopic provided in handle_query_pinecone")
        return jsonify({'error': 'No subtopic provided'}), 400

    video_titles = query_pinecone(subtopic)
    return jsonify({'results': video_titles})

def search_youtube():
  content = request.json
  subtopic = content.get('subTopic')
  if not subtopic:
      logging.warning("No subtopic provided in search_youtube")
      return jsonify({'error': 'No subtopic provided'}), 400

  # Replace 'yt_api_key' with the actual variable that holds your YouTube API key.
  videos = youtube_search(yt_api_key, subtopic, 3)
  return jsonify({'videos': videos})


def initialize_routes(app):
  app.add_url_rule('/', 'index', view_func=index, methods=['GET'])
  app.add_url_rule('/query', 'query', view_func=query, methods=['GET'])
  app.add_url_rule('/upload_screen', 'upload_screen', view_func=upload_screen, methods=['GET'])
  app.add_url_rule('/upload', 'upload_file', view_func=upload_file, methods=['POST'])
  app.add_url_rule('/download', 'download_videos', view_func=download_videos)
  app.add_url_rule('/progress', 'get_progress', view_func=get_progress)
  app.add_url_rule('/extract_youtube_ids', 'extract_youtube_ids', view_func=extract_youtube_ids, methods=['POST'])
  app.add_url_rule('/process_videos', 'process_extracted_videos', view_func=process_extracted_videos, methods=['POST'])
  app.add_url_rule('/embed_summaries_from_firestore', 'embed_summaries_from_firestore', view_func=embed_summaries_from_firestore, methods=['POST'])
  app.add_url_rule('/generate-sub-topics', 'handle_agent_expander', view_func=handle_agent_expander, methods=['POST'])
  app.add_url_rule('/query-subtopic', 'handle_query_pinecone', view_func=handle_query_pinecone, methods=['POST'])
  app.add_url_rule('/search_youtube', 'search_youtube', view_func=search_youtube, methods=['POST'])
  app.add_url_rule('/download_csv', 'download_csv', view_func=download_csv, methods=['GET'])



