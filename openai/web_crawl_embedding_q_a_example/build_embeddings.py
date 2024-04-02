import openai
import pandas as pd
import os
from dotenv import load_dotenv
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# Assuming the CSV file is named "output.csv" and is located in the current directory
df = pd.read_csv("processed/chunked.csv")


# Note that you may run into rate limit issues depending on how many files you try to embed
# Please check out our rate limit guide to learn more on how to handle this: https://platform.openai.com/docs/guides/rate-limits

df["embeddings"] = df.text.apply(
    lambda x: openai.Embedding.create(input=x, engine="text-embedding-ada-002")["data"][
        0
    ]["embedding"]
)
df.to_csv("processed/embeddings.csv")
df.head()
