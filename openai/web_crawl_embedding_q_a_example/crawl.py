################################################################################
### Step 1
################################################################################

import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
full_url = os.getenv("WEBSITE_URL")


# website specific exclusions
def custom_exclude():
    return ["resource-manager/view", "fs/pages"]
    # return []


# Regex pattern to match a URL
HTTP_URL_PATTERN = r"^http[s]{0,1}://.+$"
VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "wmv", "flv", "mkv"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "svg"}
PDF_EXTENSION = "pdf"
VIDEO_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-ms-wmv",
    "video/x-flv",
}


# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])


def should_skip(url):
    for exclude in custom_exclude():
        if exclude in url:
            return True
    return False


def get_content_type(url):
    try:
        print(f"Checking URL {url}")
        # Start with a HEAD request
        head_response = requests.head(url, allow_redirects=True, timeout=5)
        if "Content-Type" in head_response.headers:
            return head_response.headers["Content-Type"].split(";")[0]

        # If HEAD fails, fallback to a GET request for the first few bytes
        get_response = requests.get(
            url, headers={"Range": "bytes=0-256"}, stream=True, timeout=5
        )
        content_type = get_response.headers.get("Content-Type", "").split(";")[0]
        get_response.close()  # Ensure to close the connection
        return content_type

    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return None


def is_video_url(base_url, url):
    # Ensure the URL is absolute by joining the base URL with the relative URL
    absolute_url = urljoin(base_url, url)

    try:
        content_type = get_content_type(absolute_url)

        # Check if the Content-Type is one of the known video types
        if content_type in VIDEO_CONTENT_TYPES:
            print("is video url", absolute_url)
            return True
    except requests.RequestException as e:
        print(f"Error checking URL {absolute_url}: {e}")

    return False


# Function to get the hyperlinks from a URL
def get_hyperlinks(url):

    # Try to open the URL and read the HTML
    # might need to set User-agent to get around the bot detection
    # try:
    #     # Open the URL and read the HTML
    #     with urllib.request.urlopen(url) as response:

    #         # If the response is not HTML, return an empty list
    #         if not response.info().get("Content-Type").startswith("text/html"):
    #             return []

    #         # Decode the HTML
    #         html = response.read().decode("utf-8")
    # except Exception as e:
    #     print(f"Error get hyperlink {url}: {e}")
    #     return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(url, headers=headers)
        # Check if the response is HTML, else return an empty list
        if "text/html" not in response.headers["Content-Type"]:
            return []

        html = response.text
    except Exception as e:
        print(f"Error get hyperlink {url}: {e}")
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks


# Function to get the hyperlinks from a URL that are within the same domain
def get_domain_hyperlinks(base_url, local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        # Skip video links
        if any(link.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
            continue  # Skip adding this link if it's a video
        # FIXME: the following lead to infinite loop somehow
        # elif is_video_url(base_url, link):
        #     continue

        # website specific exclusions
        if should_skip(link):
            continue

        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif (
                link.startswith("#")
                or link.startswith("mailto:")
                or link.startswith("tel:")
            ):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


def download_file(url, directory, domain):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes

        # Create a file path with the URL path component
        path = urlparse(url).path
        filename = os.path.basename(path)

        # Ensure the filename does not contain URL parameters or fragments
        filename = filename.split("?")[0].split("#")[0]

        # Prevent directory traversal attacks
        filename = filename.replace("..", "")

        # Join the directory with the sanitized filename
        full_path = os.path.join(directory, domain, filename)

        # Ensure subdirectories exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
    except Exception as e:
        print(f"Error saving {url} to {full_path}: {e}")


def write_seen_to_file(seen, file_path):
    with open(file_path, "w") as file:
        for url in seen:
            file.write(url + "\n")


def crawl(url):
    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # Create a directory to store the text files
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("img/"):
        os.mkdir("img/")

    if not os.path.exists("pdf/"):
        os.mkdir("pdf/")

    if not os.path.exists("text/" + local_domain + "/"):
        os.mkdir("text/" + local_domain + "/")

    if not os.path.exists("img/" + local_domain + "/"):
        os.mkdir("img/" + local_domain + "/")

    if not os.path.exists("pdf/" + local_domain + "/"):
        os.mkdir("pdf/" + local_domain + "/")

    # Create a directory to store the csv files
    if not os.path.exists("processed"):
        os.mkdir("processed")

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url)  # for debugging and to see the progress

        # Try extracting the text from the link, if failed proceed with the next item in the queue
        # Get the text from the URL using BeautifulSoup
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
        # Get the text but remove the tags
        text = soup.get_text()
        if "404 - Page Not Found" in text:
            print(f"404 - Page Not Found: {url}")
            continue

        try:
            # Save text from the url to a <url>.txt file
            with open(
                "text/" + local_domain + "/" + url[8:].replace("/", "_") + ".txt",
                "w",
                encoding="UTF-8",
            ) as f:
                # If the crawler gets to a page that requires JavaScript, it will stop the crawl
                if "You need to enable JavaScript to run this app." in text:
                    print(
                        "Unable to parse page "
                        + url
                        + " due to JavaScript being required"
                    )

                # Otherwise, write the text to the file in the text directory
                f.write(text)
        except Exception as e:
            print("Unable to parse page " + url)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(base_url, local_domain, url):
            if link not in seen:
                if link.split(".")[-1].lower() in IMAGE_EXTENSIONS:
                    download_file(link, "img/", local_domain)
                elif link.split(".")[-1].lower() == PDF_EXTENSION:
                    download_file(link, "pdf/", local_domain)
                else:
                    queue.append(link)

                seen.add(link)

    output_file_path = "seen_urls.txt"
    write_seen_to_file(seen, output_file_path)
    print(f"Seen URLs saved to {output_file_path}")

    # Create a DataFrame to store the URLs and save it to a CSV file
    df = pd.DataFrame(list(seen), columns=["URL"])
    df.to_csv("processed/seen_urls.csv", index=False)
    print("Seen URLs saved to processed/seen_urls.csv")


crawl(full_url)
