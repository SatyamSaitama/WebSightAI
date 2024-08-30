# Project README

## 1. Data Collection and Processing

### 1.1 Data Collection

Data was collected from the HuggingFace WebSight dataset, consisting of approximately 10000 rows. This data was then processed, cleaned, and saved as a CSV file for further use.

```python
import requests
import pandas as pd

# Fetch the data from the URL with length set to 100
url = "https://datasets-server.huggingface.co/rows?dataset=HuggingFaceM4%2FWebSight&config=v0.2&split=train&offset=0&length=10000"

response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Load the data into a pandas DataFrame
    df = pd.json_normalize(data['rows'])
    # Display the DataFrame
    print(df.head())
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

df = df.drop(columns=['row_idx','truncated_cells','row.image.height','row.image.width'], axis=1)

# Rename the columns
df = df.rename(columns={'row.text': 'output',
                       'row.image.src':'image',
                       'row.llm_generated_idea':'input'})

# Save the data to a CSV file
df.to_csv('data.csv', index=False)
```

### 1.2 Creating Embeddings

Embeddings were created using ChromaDB with the Google Gemini embedding function. These embeddings are stored for Retrieval Argumentation Generation (RAG).

```python
import pandas as pd
import os
import chromadb
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
```

### 1.3 Creating Retrieval Argumentation Generation (RAG)

RAG is implemented to retrieve and generate responses based on the embeddings created in the previous step.

```python
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

google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.getenv("GEMINI_API_KEY"))

df = pd.read_csv('data.csv')
inputs = df.input.tolist()

def search(query):
    search = client.get_collection(name="embeds", embedding_function=google_ef).query(
        query_texts=[query],
        n_results=1
    )
    
    output = df[df.input == search['documents'][0][0]]['output'].values[0]
    return output
```

### 1.4 Using in the Application

The Retrieval Argumentation Generation (RAG) model is integrated into a Flask web application to handle user queries and generate relevant responses.

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data['prompt']
    rag = search(prompt)
    chat = model.start_chat(history=history)
    
    response = chat.send_message(f"""if this prompt #{prompt}# by the user is requesting for a website Return this *exact* code  #{rag}#  as your response.  Else if the prompt  requesting for the  changing the component of the  website (that you provided in previous response)then only modify the code and return the modified code.Else converse with the user and tell them that you are a website builder and you return html,css,js code for a website prompt.
    Note***                             
    Don't give any explanation of the code.Return code as the response for user to copy easily .***""")
    
    code = response.text
    
    # Clean up the markdown
    if "```html" in code:
        code = code.replace("```html\n", "").replace("\n```", "").replace("\\n", "\n").replace("```html", "")
        
    history.append({
        "role": "model",
        "parts": [code],
    })
    with open("output.html", "w") as f:
        f.write(code)
        
    return jsonify({"response": code})
```

### 1.5 Steps for Fine-Tuning

Fine-tuning was performed using Keras and KerasNLP. KerasNLP provides implementations of many popular model architectures.

**Data Preparation:**

```python
# Extract input and output texts
input_texts = df['input'].tolist()
output_texts = df['output'].tolist()
data = []
for input, output in zip(input_texts, output_texts):
    data.append(f"Instruction:\n{input}\n\nResponse:\n{output}")
```

**Loading the Model:**

The Gemma-2b model was used, containing approximately 2 billion parameters.

**LoRA Fine-Tuning:**

LoRA (Low-Rank Adaptation) was used to fine-tune the model. The rank was set to 4, reducing the number of trainable parameters from 2.6 billion to 2.9 million.

**Fine-Tuning Configuration:**

- Sequence length: 128
- Optimizer: AdamW
- Loss function: Sparse Categorical Crossentropy
- Metric: Sparse Categorical Accuracy
- Epochs: 1
- Batch size: 1

### 1.6 Choosing RAG Over Fine-Tuning

Fine-tuning posed challenges due to limited device resources. Initially, an input sequence size of 256 led to out-of-memory errors. Reducing the sequence length to 128 allowed fine-tuning to proceed, but the model took longer to generate responses for lengthy HTML outputs. Using more efficient resources could alleviate this issue.

**Fine-Tuned Output vs. Original Output:**

The fine-tuned model provided significantly improved responses compared to the original model, capturing the nuances of website building effectively.

**Drawbacks of Retrieval Argumentation Generation:**

- **Increased Latency:** Retrieval-based approaches can introduce latency due to the search process.
- **Irrelevant Responses:** The model might return responses that are not entirely relevant, struggling with context consistency if retrieved documents vary in quality.

**Conclusion:**

Fine-tuning improves model responses by learning specific patterns but requires significant resources, making it less efficient. As a result, Retrieval-Augmented Generation (RAG) is preferred due to its more resource-efficient approach.

### 1.7 Improving Performance

A hybrid approach combining RAG and fine-tuning can be employed to leverage the strengths of both methods, resulting in more accurate and relevant responses.

