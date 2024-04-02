import pandas as pd
import os


def remove_newlines(serie):
    if not serie.dtype == object:
        raise TypeError("Series must contain string values.")

    serie = serie.astype(str)  # Ensure all values are treated as strings
    serie = serie.str.replace("\n", " ")
    serie = serie.str.replace("\\n", " ")
    serie = serie.str.replace("  ", " ")
    serie = serie.str.replace("  ", " ")
    return serie


domain = "macpractice.atlassian.net"

# Create a list to store the text files
texts = []

# Get all the text files in the text directory
for file in os.listdir("text/" + domain + "/"):

    # Open the file and read the text
    with open("text/" + domain + "/" + file, "r", encoding="UTF-8") as f:
        text = f.readlines()

        # Filter out lines shorter than 50 characters
        filtered_text = [line.strip() for line in text if len(line.strip()) > 50]

        # Join filtered lines back into a single string
        filtered_text = "\n".join(filtered_text)

        # Omit the last 4 cnars, then replace -, _, and 'macpractice.atlassian.net_wiki_spaces_MPHelpDesk_page' with spaces.
        texts.append(
            (
                file[:-4]
                .replace("macpractice.atlassian.net_wiki_spaces_MPHelpDesk_pages", "")
                .replace("-", " ")
                .replace("_", " "),
                filtered_text,
            )
        )

# Create a dataframe from the list of texts
df = pd.DataFrame(texts, columns=["fname", "text"])

# Set the text column to be the raw text with the newlines removed
df["text"] = df.fname + ". " + remove_newlines(df.text)
df.to_csv("processed/scraped.csv")
df.head()
