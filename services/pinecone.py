# Standard library imports
import logging

# Third-party imports
import pinecone
import openai
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings

# Local imports
from config.api_keys import pinecone_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize Pinecone
logging.info("Initializing Pinecone")
pinecone.init(api_key=pinecone_api_key, environment='gcp-starter')
existing_indexes = pinecone.list_indexes()
index_name = 'learning-objectives'

# Create Pinecone index if it doesn't exist
if index_name not in existing_indexes:
    logging.info(f"Creating new index: {index_name}")
    pinecone.create_index(index_name, dimension=768, metric='cosine')
else:
    logging.info(f"Index '{index_name}' already exists.")

def insert_embedding_into_pinecone(video_id, embedding):
    """
    Insert an embedding into Pinecone.

    :param video_id: Identifier for the video.
    :param embedding: The embedding vector to be inserted.
    """
    pinecone_index = pinecone.Index(index_name)

    # Validate embedding type
    if not isinstance(embedding, list) or not all(isinstance(e, float) for e in embedding):
        logging.error(f"Invalid embedding type for video ID {video_id}: {type(embedding)}")
        return

    try:
        pinecone_index.upsert(vectors={video_id: embedding})
        logging.info(f"Embedding successfully inserted for video ID {video_id}")
    except Exception as e:
        logging.error(f"Error inserting embedding into Pinecone for video ID {video_id}: {e}", exc_info=True)

def query_pinecone(subtopic):
    """
    Embed a subtopic and query Pinecone for the most relevant vectors.

    :param subtopic: The subtopic to query.
    :return: A list of results including titles and scores.
    """
    embedding = OpenAIEmbeddings(openai_api_key=openai.api_key)
    pinecone_index = Pinecone.get_pinecone_index(index_name=index_name, pool_threads=4)

    try:
        # Embed the subtopic
        embedded_subtopic = embedding.embed_query(subtopic)

        # Query Pinecone
        query_result = pinecone_index.query(
            vector=embedded_subtopic, 
            top_k=3, 
            include_metadata=True
        )

        # Extract video titles and their scores
        results = [{
            'title': result['metadata']['title'],
            'score': result['score']
        } for result in query_result['matches'] if 'metadata' in result and 'title' in result['metadata']]

        return results
    except Exception as e:
        logging.error(f"Error querying Pinecone for subtopic: {e}", exc_info=True)
        return []
