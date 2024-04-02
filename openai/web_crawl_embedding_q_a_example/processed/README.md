# Web Q&A with Embeddings

Learn how to crawl your website and build a Q/A bot with the OpenAI API. You can find the full tutorial in the [OpenAI documentation](https://platform.openai.com/docs/tutorials/web-qa-embeddings).

This project split the sample code into mutliple scripts for flexibility.

### Folder Structure

```
    ├── README.md
    ├── build_embeddings.py
    ├── crawl.py
    ├── make_csv.py
    ├── post_crawl.py
    ├── processed
    │   ├── chunked.csv
    │   ├── embeddings.csv
    │   └── scraped.csv
    ├── q_a.py
    ├── requirements.txt
    ├── text
    │   └── macpractice.atlassian.net
    │       ├── macpractice.atlassian.net_wiki_spac ...
    │       └── macpractice.atlassian.net_wiki_space ...
    └── tokenization.py
```

- crawl.py: crawls the website, each page is stored as a text file under `text/{domain}/`
- post_crawl.py: removes unwanted files crawled
- make_csv.py: combine all crawed files and put it into `scraped.csv` under `processed`
- tokenization.py:
  - tokenize the text in each csv row
  - set a max token-count, and break it down if necessary
  - output to `processed/chunked.csv`
- embeddings.csv: create an embedding, output to `processed/embeddings.csv`
- q_a.py: use the embedding to answer a question
