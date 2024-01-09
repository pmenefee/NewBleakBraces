# Standard library imports
import re
import logging

# Third-party imports
from bs4 import BeautifulSoup
import dateutil.parser

# Initialize logging with structured formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Timezone information for date parsing
tzinfos = {
    "CST": -21600  # Central Standard Time (USA) UTC-6:00
    # Add other timezones if necessary
}

def parse_html(html_content):
    """
    Parses HTML content to extract video IDs and timestamps.

    :param html_content: HTML content as a string.
    :return: A list of dictionaries containing video IDs and their timestamps.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    video_data_list = []
    timestamp_regex = re.compile(
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2}\u202F[APM]{2}\s\w+'
    )

    for div in soup.find_all("div", class_="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1"):
        link_tag = div.find('a', href=True)
        if link_tag and 'youtube.com/watch?v=' in link_tag['href']:
            video_id = link_tag['href'].split('watch?v=')[-1].split('&')[0]
            timestamp_match = timestamp_regex.search(div.get_text())
            timestamp = None
            if timestamp_match:
                try:
                    timestamp = dateutil.parser.parse(timestamp_match.group(), tzinfos=tzinfos)
                except ValueError as e:
                    logging.error(f"Error parsing timestamp for video ID {video_id}: {e}")
            video_data_list.append({'video_id': video_id, 'timestamp': timestamp})

    return video_data_list
