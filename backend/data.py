import requests
import pandas as pd

# Fetch the data from the URL with length set to 100
url = "https://datasets-server.huggingface.co/rows?dataset=HuggingFaceM4%2FWebSight&config=v0.2&split=train&offset=0&length=100"

response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    # Load the data into a pandas DataFrame
    df = pd.json_normalize(data['rows'])  # Adjusted to access the 'rows' field in the JSON response
    # Display the DataFrame
    print(df.head())
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

df = df.drop(columns=['row_idx','truncated_cells','row.image.height','row.image.width'],axis=1)

# Rename the columns
df = df.rename(columns={'row.text': 'output',
                       'row.image.src':'image',
                        'row.llm_generated_idea':'input'
                        })

# Save the data to a CSV file
df.to_csv('data.csv', index=False)
