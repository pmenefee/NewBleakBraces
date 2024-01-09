# Standard library imports
import logging
import csv
import io
import json

# Third-party imports
import firebase_admin
from firebase_admin import credentials, firestore


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize Firebase Admin
try:
    cred = credentials.Certificate('config/rabbit-408205-firebase-adminsdk-opkxt-77124475b9.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logging.info("Firebase Admin initialized successfully.")
except Exception as e:
    logging.error("Failed to initialize Firebase Admin", exc_info=True)

def store_in_firestore(data):
    """
    Stores the provided data in Firestore.

    :param data: The data to be stored.
    """
    # Firestore storing logic
    # Implement the logic to store data in Firestore
    pass

def get_all_videos_from_firestore():
    """
    Retrieves all videos from Firestore.

    :return: A list of video data.
    """
    try:
        videos = db.collection('youtube_videos').stream()
        video_list = []
        for doc in videos:
            video_data = doc.to_dict()
            video_data['video_id'] = doc.id  # Ensure video_id is added to each video dictionary
            video_list.append(video_data)
        return video_list
    except Exception as e:
        logging.error("Failed to retrieve videos from Firestore", exc_info=True)
        return []

def flatten_dict(d, parent_key='', sep='_'):
  """
  Flattens a nested dictionary.
  
  :param d: The dictionary to flatten
  :param parent_key: The base key to use for the flattened keys
  :param sep: Separator to use between keys
  :return: A flattened dictionary
  """
  items = []
  for k, v in d.items():
      new_key = f"{parent_key}{sep}{k}" if parent_key else k
      if isinstance(v, dict):
          items.extend(flatten_dict(v, new_key, sep=sep).items())
      elif isinstance(v, list):
          # Convert list to a string to ensure it can be written to CSV
          items.append((new_key, json.dumps(v)))
      else:
          items.append((new_key, v))
  return dict(items)

def create_csv_from_data(data):
  """
  Converts a list of dictionaries into a CSV file, handling nested dictionaries.

  :param data: List of dictionaries
  :return: CSV file object
  """
  # Flatten each video's data and collect all unique fieldnames
  flattened_data = [flatten_dict(video) for video in data]
  fieldnames = set()
  for entry in flattened_data:
      fieldnames.update(entry.keys())

  output = io.StringIO()
  # Use the unique fieldnames for all videos as the CSV headers
  writer = csv.DictWriter(output, fieldnames=sorted(fieldnames))
  writer.writeheader()
  writer.writerows(flattened_data)
  output.seek(0)
  return output

