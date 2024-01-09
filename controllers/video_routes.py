# Standard library imports
import json
import logging
import datetime

# Third-party imports
from flask import request, jsonify, send_file, session

# Local imports
from utils.html_parser import parse_html  # Assuming parse_html is in utils
from services.data_processing import process_videos, get_all_videos
from controllers.subprocess_controller import extract_youtube_ids
from models.firestore_encoder import FirestoreEncoder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def upload_file():
    """
    Handles the file upload request, processes the content, and returns the results.
    """
    logging.info("Received a request to upload a file")

    if request.method != 'POST':
        logging.warning("Invalid method for file upload")
        return jsonify({'error': 'Invalid method'}), 405

    file_part = request.files.get('file')
    if not file_part or file_part.filename == '':
        logging.warning("No file part or selected file in the request")
        return jsonify({'error': 'No file part or selected file in the request'}), 400

    filename = file_part.filename
    file_extension = filename.rsplit('.', 1)[1].lower()

    try:
        file_content = file_part.read().decode('utf-8')
    except UnicodeDecodeError as e:
        logging.error(f"Unable to decode the file: {e}", exc_info=True)
        return jsonify({'error': 'Unable to decode the file. Ensure it is UTF-8 encoded.'}), 400

    video_data_list = []
    if file_extension == 'html':
        video_data_list = parse_html(file_content)
    elif file_extension == 'txt':
      video_id_list = extract_youtube_ids(file_content)
      # Temporary fix: Assigning the current timestamp to each video ID.
      # This should be replaced with the appropriate timestamp logic as per the application's requirement.
      current_timestamp = datetime.datetime.now(datetime.timezone.utc)
      video_data_list = [{'video_id': video_id, 'timestamp': current_timestamp} for video_id in video_id_list]

    if not video_data_list:
        logging.info("No video IDs found in the file")
        return jsonify({'message': 'No video IDs found in the file'}), 200

    processed_data, progress = process_videos(video_data_list)
    logging.info(f"File {filename} processed successfully with {len(processed_data)} videos")

    return jsonify({
        'message': 'File uploaded and processed successfully',
        'total_videos': len(processed_data),
        'progress': progress
    }), 200

def download_videos():
    """
    Downloads video data as a JSON file.
    """
    try:
        video_data = get_all_videos()
        filename = 'video_data.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, cls=FirestoreEncoder, ensure_ascii=False, indent=4)
        return send_file(filename, as_attachment=True)
    except FileNotFoundError as e:
        logging.error(f"File not found error: {e}", exc_info=True)
        return jsonify({'error': 'File not found error'}), 500
    except json.JSONEncodeError as e:
        logging.error(f"JSON encoding error: {e}", exc_info=True)
        return jsonify({'error': 'JSON encoding error'}), 500

def process_extracted_videos():
    """
    Processes extracted videos and returns the results.
    """
    video_data_list = extract_youtube_ids()  # Assumes this function returns a list of IDs

    if not video_data_list:
        return jsonify({'error': 'No video IDs extracted'}), 400

    processed_data, progress = process_videos(video_data_list)
    session['processed_data'] = processed_data  # Store in session for future use

    return jsonify({
        'message': 'Videos processed',
        'total_videos': len(video_data_list),
        'progress': progress
    }), 200
