# Standard library imports
import datetime
import logging

# Third-party imports
import dateutil.parser
import isodate
import openai
from flask import jsonify, Response

# Local imports
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from utils.agents import agent_summarizer
from utils.youtube_api import get_category_name, get_youtube_video_details
from config.api_keys import yt_api_key
from controllers.firestore_controller import get_all_videos_from_firestore, db, create_csv_from_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def download_csv():
  try:
      data = get_all_videos_from_firestore()
      csv_file = create_csv_from_data(data)
      return Response(
          csv_file.getvalue(),
          mimetype='text/csv',
          headers={"Content-disposition": "attachment; filename=firestore_data.csv"})
  except Exception as e:
      return {"error": str(e)}, 500


def process_video_data(video_id, video_details, timestamp):
  """
  Extracts video data and stores it in Firebase Firestore.

  :param video_id: The YouTube video ID.
  :param video_details: Dictionary containing details of the video.
  :param timestamp: The timestamp when the video data was processed.
  """
  try:
      # Parsing and formatting snippet data
      snippet = video_details.get('snippet', {})
      published_at = dateutil.parser.parse(snippet.get('publishedAt', '')) if snippet.get('publishedAt') else None
      duration = isodate.parse_duration(video_details.get('contentDetails', {}).get('duration', '')) if video_details.get('contentDetails', {}).get('duration') else None
      duration_in_seconds = duration.total_seconds() if duration else None

      # Formatting video data for Firestore
      video_data = {
          'video_id': video_id,
          'kind': video_details.get('kind', ''),
          'etag': video_details.get('etag', ''),
          'snippet': {
              'publishedAt': published_at,
              'channelId': snippet.get('channelId', ''),
              'title': snippet.get('title', ''),
              'description': snippet.get('description', ''),
              'thumbnails': snippet.get('thumbnails', {}),
              'channelTitle': snippet.get('channelTitle', ''),
              'tags': snippet.get('tags', []),
              'categoryId': snippet.get('categoryId', ''),
              'liveBroadcastContent': snippet.get('liveBroadcastContent', ''),
              'defaultLanguage': snippet.get('defaultLanguage', ''),
              'localized': snippet.get('localized', {}),
              'defaultAudioLanguage': snippet.get('defaultAudioLanguage', '')
          },
          'contentDetails': video_details.get('contentDetails', {}),
          'statistics': video_details.get('statistics', {}),
          'duration_in_seconds': duration_in_seconds,
          'timestamp': timestamp,
          'last_updated': datetime.datetime.now(datetime.timezone.utc),
          'generated': {
              'summary': agent_summarizer(snippet.get('description', '')),
          }
      }

      # Store video data in Firestore
      db.collection('youtube_videos').document(video_id).set(video_data)
      logging.info(f"Data processed and inserted successfully for video ID {video_id} into Firestore.")
  except Exception as e:
      logging.error(f"Failed to insert data into Firestore for video ID {video_id}: {e}", exc_info=True)


def process_videos(video_data_list):
  """
  Processes a list of video data and embeds summaries into Pinecone.
  
  :param video_data_list: A list of video data.
  :return: Tuple containing the processed data and progress percentage.
  """
  processed_data = []
  progress = 0
  embedding = OpenAIEmbeddings(openai_api_key=openai.api_key)
  index_name = "learning-objectives"
  pinecone_index = Pinecone.get_pinecone_index(index_name=index_name, pool_threads=4)
  
  for idx, video_data in enumerate(video_data_list):
      video_id = video_data['video_id']
      video_details = get_youtube_video_details(yt_api_key, video_id)
      if video_details:
          process_video_data(video_id, video_details, video_data['timestamp'])
          summary = agent_summarizer(video_details.get('description', ''))
          processed_data.append({'video_id': video_id, 'summary': summary})
  
          # Embed summary into Pinecone
          try:
              embedded_summary = embedding.embed_query(summary)
              if isinstance(embedded_summary, list) and all(isinstance(item, float) for item in embedded_summary):
                  vector_to_upsert = {
                      "id": video_id,
                      "values": embedded_summary,
                      "metadata": {
                          "title": video_details.get('snippet', {}).get('title', ''),
                          "video_id": video_id
                      }
                  }
                  pinecone_index.upsert(vectors=[vector_to_upsert])
                  logging.info(f"Upserted vector for video ID {video_id}")
              else:
                  logging.warning(f"Skipping upsert for video ID {video_id} due to invalid embedding format.")
          except Exception as e:
              logging.error(f"Error embedding summary for video ID {video_id}: {e}")
  
          progress = (idx + 1) / len(video_data_list) * 100
  
  return processed_data, progress


def get_all_videos():
  """
  Retrieves all videos from Firestore.

  :return: A list of video data.
  """
  videos = db.collection('youtube_videos').stream()
  video_list = [{doc.id: doc.to_dict()} for doc in videos]
  return video_list


def embed_summaries_from_firestore(video_data):
  """
  Process summaries of videos and insert embeddings into Pinecone.

  :param video_data: List of dictionaries containing video_id, title, and summary.
  """
  embedding = OpenAIEmbeddings(openai_api_key=openai.api_key)
  pool_threads = 4
  index_name = "learning-objectives"
  pinecone_index = Pinecone.get_pinecone_index(index_name=index_name, pool_threads=pool_threads)

  for video in video_data:
      if 'video_id' not in video or 'title' not in video or 'summary' not in video:
          logging.warning(f"Required data not found in video data: {video}")
          continue

      video_id = video['video_id']
      video_title = video['title']
      summary = video['summary']

      try:
          embedded_summary = embedding.embed_query(summary)
          if isinstance(embedded_summary, list) and all(isinstance(item, float) for item in embedded_summary):
              vector_to_upsert = {
                  "id": video_id,
                  "values": embedded_summary,
                  "metadata": {
                      "title": video_title,
                      "video_id": video_id
                  }
              }
              pinecone_index.upsert(vectors=[vector_to_upsert])
              logging.info(f"Upserted vector for video ID {video_id}")
          else:
              logging.warning(f"Skipping upsert for video ID {video_id} due to invalid embedding format.")
      except Exception as e:
          logging.error(f"Error inserting embedding for video ID {video_id}: {e}")
