import pandas as pd
import numpy as np
import openai
import os
from dotenv import load_dotenv
from ast import literal_eval
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

df = pd.read_csv("processed/embeddings.csv", index_col=0)
df["embeddings"] = df["embeddings"].apply(literal_eval).apply(np.array)

df.head()

################################################################################
### Step 12
################################################################################


def create_context(question, df, max_len=1800, size="ada"):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(
        input=question, engine="text-embedding-ada-002"
    )["data"][0]["embedding"]

    # Get the distances from the embeddings
    df["distances"] = distances_from_embeddings(
        q_embeddings, df["embeddings"].values, distance_metric="cosine"
    )

    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values("distances", ascending=True).iterrows():

        # Add the length of the text to the current length
        cur_len += row["n_tokens"] + 4

        # If the context is too long, break
        if cur_len > max_len:
            break

        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
    df,
    # model="text-davinci-003",
    model="gpt-3.5-turbo-instruct",
    question="Am I allowed to publish model outputs to Twitter, without a human review?",
    max_len=1800,
    size="ada",
    debug=False,
    max_tokens=250,
    stop_sequence=None,
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        # Create a completions using the questin and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return ""


################################################################################
### Step 13
################################################################################

# print(answer_question(df, question="What day is it?", debug=False))

# print(answer_question(df, question="What is our newest embeddings model?"))


# print(answer_question(df, question="What is 'abscess' in Perio?", debug=False))
# question="What is Database Utility in MacPractice?"
# question="List a few Database Utilities in MacPractice?"
# question="How to move a patient to another account in MacPractice?"
# question="How to move a patient to another account in MacPractice? Show me step by step."
# question="How to become a volunteer for DTSD, show me step by step.",
print(
    answer_question(
        df,
        question="How to obtain background clearances for the district? Show me step by step.",
        debug=False,
    )
)
