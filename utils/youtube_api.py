# Standard library imports
import logging
import os

# Third-party imports
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build

# Local imports
from config.api_keys import yt_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

youtube = build('youtube', 'v3', developerKey=yt_api_key)

def get_youtube_video_details(yt_api_key, video_id):
  """
  Makes an API call to YouTube to get details of a specific video.

  :param yt_api_key: YouTube API key.
  :param video_id: ID of the YouTube video.
  :return: Dictionary containing video details or empty dictionary on failure.
  """
  url = "https://www.googleapis.com/youtube/v3/videos"
  parts = "snippet,contentDetails,statistics"
  params = {"part": parts, "id": video_id, "key": yt_api_key}

  try:
      response = requests.get(url, params=params)
      if response.status_code == 200:
          items = response.json().get("items", [])
          if items:
              item = items[0]
              snippet = item.get("snippet", {})
              content_details = item.get("contentDetails", {})
              statistics = item.get("statistics", {})

              # Extract thumbnail information
              thumbnails = snippet.get("thumbnails", {})
              thumbnail_urls = {quality: thumb_info.get('url') for quality, thumb_info in thumbnails.items() if 'url' in thumb_info}

              # Extract additional fields
              video_details = {
                  "kind": item.get("kind", ""),
                  "etag": item.get("etag", ""),
                  "id": item.get("id", ""),
                  "snippet": {
                      "publishedAt": snippet.get("publishedAt", ""),
                      "channelId": snippet.get("channelId", ""),
                      "title": snippet.get("title", ""),
                      "description": snippet.get("description", ""),
                      "thumbnails": thumbnail_urls,
                      "channelTitle": snippet.get("channelTitle", ""),
                      "tags": snippet.get("tags", []),
                      "categoryId": snippet.get("categoryId", ""),
                      "liveBroadcastContent": snippet.get("liveBroadcastContent", ""),
                      "defaultLanguage": snippet.get("defaultLanguage", ""),
                      "localized": snippet.get("localized", {}),
                      "defaultAudioLanguage": snippet.get("defaultAudioLanguage", "")
                  },
                  "contentDetails": content_details,
                  "statistics": statistics
              }

              return video_details
          else:
              logging.warning(f"No items found for video ID {video_id}")
              return {}
      else:
          logging.error(f"Error fetching data for video ID {video_id}: {response.status_code}")
          logging.debug("Response Content:", response.content)
          return {}
  except requests.RequestException as e:
      logging.error(f"Request error for video ID {video_id}: {e}", exc_info=True)
      return {}

def get_category_name(yt_api_key, category_id):
    """
    Retrieves the category name for a given YouTube category ID.

    :param yt_api_key: YouTube API key.
    :param category_id: YouTube category ID.
    :return: Category name or 'Unknown' on failure.
    """
    url = "https://www.googleapis.com/youtube/v3/videoCategories"
    params = {"part": "snippet", "id": category_id, "key": yt_api_key}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                return items[0].get("snippet", {}).get("title", "Unknown")
            return "Unknown"
        else:
            logging.error(f"Error fetching category for ID {category_id}: {response.status_code}")
            return "Unknown"
    except requests.RequestException as e:
        logging.error(f"Request error for category ID {category_id}: {e}", exc_info=True)
        return "Unknown"

def get_channel_data(yt_api_key, channel_id):
  """
  Retrieves the channel data for a given YouTube category ID.

  :param yt_api_key: YouTube API key.
  :param category_id: YouTube category ID.
  :return: Category name or 'Unknown' on failure.
  """
  url = "https://www.googleapis.com/youtube/v3/channels"
  params = {"part": "snippet", "id": channel_id, "key": yt_api_key}

  try:
      response = requests.get(url, params=params)
      if response.status_code == 200:
          items = response.json().get("items", [])
          if items:
              return items[0].get("snippet", {}).get("title", "Unknown")
          return "Unknown"
      else:
          logging.error(f"Error fetching category for ID {channel_id}: {response.status_code}")
          return "Unknown"
  except requests.RequestException as e:
      logging.error(f"Request error for category ID {channel_id}: {e}", exc_info=True)
      return "Unknown"


# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def youtube_search(yt_api_key, query, max_results=3):
  try:
      # Log the YouTube API key and query for debugging
      logging.info(f"Using YouTube API key: {yt_api_key}")
      logging.info(f"Searching YouTube for query: '{query}' with max results: {max_results}")

      # Build the YouTube client
      youtube = build('youtube', 'v3', developerKey=yt_api_key)

      # Perform the search  
      search_response = youtube.search().list(
          q=query,
          part='snippet',
          maxResults=max_results,
          type='video'
      ).execute()

      # Extract video information
      videos = []
      for search_result in search_response.get('items', []):
          videos.append({
              'title': search_result['snippet']['title'],
              'videoId': search_result['id']['videoId'],
              'thumbnail': search_result['snippet']['thumbnails']['high']['url']
          })

      # Log the search results for debugging
      logging.info(f"Found {len(videos)} videos for query '{query}'")
      return videos

  except Exception as e:
      logging.error(f"Error in youtube_search: {str(e)}", exc_info=True)
      return []
