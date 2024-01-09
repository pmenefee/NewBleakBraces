import subprocess
import logging
import time

def extract_youtube_ids(cookies_content, debug=False):
    """
    Extracts YouTube video IDs from the user's watch history using yt-dlp.
    :param cookies_content: The content of the cookies file.
    :param debug: Enable detailed logging for debugging.
    :return: A list of extracted YouTube video IDs.
    """
    cookies_file_path = './www.youtube.com_cookies.txt'
    logging.info("Starting extraction of YouTube IDs")

    with open(cookies_file_path, 'w') as cookies_file:
        cookies_file.write(cookies_content)

    command = f"yt-dlp --cookies {cookies_file_path} --skip-download --playlist-start 1 --playlist-end 10 --get-id 'https://www.youtube.com/feed/history'"
    if debug:
        command += " --verbose"
    logging.info(f"Running command: {command}")

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        start_time = time.time()

        while process.poll() is None:
            if time.time() - start_time > 120:  # 120 seconds timeout
                process.kill()
                logging.error("yt-dlp command timed out")
                return []
            time.sleep(10)  # Sleep for 10 seconds before checking again

        output, error = process.communicate()

        if error:
            logging.error(f"Error during extraction: {error}")
            return []

        video_ids = [line.strip() for line in output.split('\n') if line.strip()]
        if debug:
            logging.info(f"Raw output: {output}")

        logging.info(f"Extraction complete. Extracted {len(video_ids)} IDs.")
        return video_ids

    except Exception as e:
        logging.error(f"Exception occurred during YouTube ID extraction: {str(e)}", exc_info=True)
        return []
