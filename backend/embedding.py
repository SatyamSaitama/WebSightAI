import pandas as pd
import os
import chromadb
import pickle
from dotenv import load_dotenv
import chromadb.utils.embedding_functions as embedding_functions
load_dotenv()
load_dotenv('.env.local')

# Set the path to the storage directory
storage_path = os.getenv('STORAGE_PATH')
if storage_path is None:
    raise ValueError('STORAGE_PATH environment variable is not set')

client = chromadb.PersistentClient(path=storage_path)

# Create a collection with the Google Generative AI embedding function
google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv("GEMINI_API_KEY"))

collection = client.create_collection(name="embeds", embedding_function=google_ef)
collection = client.get_collection(name="embeds", embedding_function=google_ef)

# Load the data
df = pd.read_csv('data.csv')
inputs = df.input.tolist()

# Add the inputs to the collection
collection.add(
    documents=inputs,
    ids=[f"{id}" for id in range(len(inputs))]
)

print("Embedding function created and data loaded into the collection.")
