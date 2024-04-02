import tiktoken
import pandas as pd
import matplotlib.pyplot as plt


# Load the cl100k_base tokenizer which is designed to work with the ada-002 model
tokenizer = tiktoken.get_encoding("cl100k_base")


# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens=500):

    # Split the text into sentences
    sentences = text.split(". ")

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    return chunks


def show_plot():
    plt.title("Distribution of Number of Tokens")
    plt.xlabel("Number of Tokens")
    plt.ylabel("Frequency")
    plt.show()


df = pd.read_csv("processed/scraped.csv", index_col=0)
df.columns = ["title", "text"]

# Tokenize the text and save the number of tokens to a new column
df["n_tokens"] = df.text.apply(lambda x: len(tokenizer.encode(x)))

# Visualize the distribution of the number of tokens per row using a histogram
# df.n_tokens.hist()
# show_plot()

# The newest embeddings model can handle inputs with up to 8191
# if your the text exceeds this limit, you can split it into smaller chunks
# and process each chunk separately
# for now set the max_tokens to 500

shortened = []
max_tokens = 500
# Loop through the dataframe
for row in df.iterrows():

    # If the text is None, go to the next row
    if row[1]["text"] is None:
        continue

    # If the number of tokens is greater than the max number of tokens, split the text into chunks
    if row[1]["n_tokens"] > max_tokens:
        shortened += split_into_many(row[1]["text"], max_tokens)

    # Otherwise, add the text to the list of shortened texts
    else:
        shortened.append(row[1]["text"])


df2 = pd.DataFrame(shortened, columns=["text"])
df2["n_tokens"] = df2.text.apply(lambda x: len(tokenizer.encode(x)))

# uncomment the following line to visualize the distribution of the number of tokens per row using a histogram
# df2.n_tokens.hist()
# show_plot()

print(df2.size)
df2.to_csv("processed/chunked.csv")
df2.head()  # this somehow make to_csv() to function
