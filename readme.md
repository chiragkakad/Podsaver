# Podsaver

Podsaver is a tool to download and archive podcasts.

## Features

- Downloads podcasts from RSS and ATOM feeds.
- Supports concurrent downloads.
- Supports updating the feeds.
- Supports downloading a single feed or multiple feeds through command line arguments or text file.
- Supports selecting different downloaders. Currently only supports Request.
- Offers a separate script to search the iTunes podcast directories for podcast feeds, and add those feeds to a text file.

## Installation

After cloning the repo on your local system, cd into the directory and install the dependencies by using pip.

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 podsaver.py -h
```

usage: podsaver.py [-h] [-f FILE] [-p PATH] [-u URL] [-d DOWNLOADER]
              [-c CONCURRENT]

Script to archive podcast.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  File containing RSS feeds for podcast
  -p PATH, --path PATH  Path to store podcast files
  -u URL, --url URL     RSS URL for podcast
  -d DOWNLOADER, --downloader DOWNLOADER
                        Downloader to use for downloading files
  -c CONCURRENT, --concurrent CONCURRENT
                        Number of concurrent downloads.

## Example

### Downloading Podcasts

#### Downloading a single feed

Downloads This Week in Tech Audio in the current working directory.

```bash
python3 podsaver.py -u "https://feeds.twit.tv/twit.xml"
```

#### Downloading feeds from file

Downloads feed from txt file in the current working directory.

```bash
python3 podsaver.py -f feed.txt
```

### Searching for feeds

Searches the iTunes podcast directorie for a given keyword. After executing the script, follow the prompts.

```bash
python3 search.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)