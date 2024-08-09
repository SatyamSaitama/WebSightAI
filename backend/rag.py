import pandas as pd
import os
import chromadb
from dotenv import load_dotenv
import chromadb.utils.embedding_functions as embedding_functions
load_dotenv()
load_dotenv('.env.local')

storage_path = os.getenv('STORAGE_PATH')
if storage_path is None:
    raise ValueError('STORAGE_PATH environment variable is not set')

client = chromadb.PersistentClient(path=storage_path)

# use directly
google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv("GEMINI_API_KEY"))


df = pd.read_csv('data.csv')
inputs = df.input.tolist()


def search(query):
    search = client.get_collection(name="embeds", embedding_function=google_ef).query(
        query_texts=[query],
        n_results=1,
        )
    
    output = df[df.input == search['documents'][0][0]]['output'].values[0]
    return output
