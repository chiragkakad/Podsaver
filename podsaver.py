#!/usr/bin/env python3
"""
Podsaver v0.1: tool for local podcast archive creation

Copyright (c) 2017-2021 Chirag Kakad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import argparse
import sys
import feedparser
import os
import requests
import re
import concurrent.futures
import time


class PodcastDownloader:
    """
    Podcast downloader class.
    """
    def __init__(self, url, path=os.getcwd(), downloader='requests', num_concurrent=3):
        """
            Podcast downloader constructor.
            Parameters:
                url: url for the podcast feed.
                path: path to store the file.
                downloader: the downloader to use to download files.
                    Default is requests.
                num_concurrent: number of files to download  concurrently.
        """
        self.url = url
        self.feed = feedparser.parse(self.url)
        # Checks whether a feed is valid.
        if len(self.feed['feed']) < 2:
            raise ValueError("Invalid feed")
        # Cleans the podcast title.
        self.title = self.clean_char(self.feed['feed']['title'])
        print("Updating %s" % self.title)
        self.items = []
        self.path = os.path.join(path, self.title)
        # Checks if the path exist. If not create a new path for the podcast.
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # Creates the file archive.txt to track the list of downloaded files.
        if not os.path.exists(os.path.join(self.path, 'archive.txt')):
            open(os.path.join(self.path, 'archive.txt'), 'w').close()
        # Open the archive file.
        self.file = open(os.path.join(self.path, 'archive.txt'), 'r+')
        # Gets the list of downloaded files from the archive file.
        self.downloaded = self.file.readlines()
        self.downloader = downloader.lower()
        self.num_concurrent = num_concurrent

    def clean_char(self, str):
        """
            Removes Unwanted characters from str.
        """
        return "".join(re.findall('[a-zA-Z0-9 %\-\_,]+', str))

    def get_items(self):
        """
            Creates a list of podcast files URLS from the podcast feed.
        """
        item_tmp = []
        self.feed.entries.reverse()   # Sort the feed from oldest to newest.
        for ind, item in enumerate(self.feed.entries):
            if hasattr(item, 'enclosures'):
                for link in item.enclosures:
                    if 'audio' in link.type:
                        item_tmp.append(
                            {"Title": "%d - %s" % (ind+1, item.title),
                                "Link": link.href,
                                "Guid": item.guid})
        return item_tmp

    def get_new_items(self):
        """
            First, gets the feed and parces the file url into a list.
            Second, checks the file list against the downloaded list and
            only gets the new item and adds it to the items list to download.
        """
        item_tmp = self.get_items()
        if len(self.downloaded) == 0:  # New podcast.
            self.items = item_tmp
            return True
        self.items = [i for i in item_tmp if '%s\n' % i["Guid"] not in self.downloaded]
        if len(self.items) == 0:
            print("No new episodes detected!")
            return False
        return True

    def download(self):
        """
            Downloads file concurrently using ThreadPoolExecutor.
            Number of concurrent download depends on num_concurrent.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_concurrent) as executor:
            downloaded = [executor.submit(
                self.download_file,
                file["Link"],
                file["Title"],
                file["Guid"])
                for file in self.items]
            for d in concurrent.futures.as_completed(downloaded):
                tmp = d.result()
                # Writes the downloaded GUID to file.
                self.file.write('%s\n' % (tmp[2]))
                self.file.flush()
                print("Downloaded %s" % tmp[0])
        return True

    def download_file(self, url, filename, guid):
        """
            Function to switch between downloaders.
            Parameters:
            URL: The URL for the audio file.
            filename: The name for the downloaded file.
            guid: the file GUID.
        """
        filename = self.clean_char(filename)
        print("Downloading %s" % filename)
        if self.downloader == 'requests':
            return self.requests_downloader(url, filename, guid)
        else:
            raise ValueError("Invalid downloader")

    def requests_downloader(self, url, filename, guid):
        """
            Downloader that uses request.
            Parameters:
                url: The URL for the audio file.
            filename: The name for the downloaded file.
            guid: the file GUID.
        """
        time.sleep(2)
        # Set user agent.
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        headers = {'User-Agent': user_agent}
        r = requests.get(url, allow_redirects=True, headers=headers)
        with open(os.path.join(self.path, '%s.mp3' % (self.clean_char(filename))), 'wb') as f:
            f.write(r.content)
        if r.status_code == 200:
            return [filename, url, guid]
        else:
            raise ValueError("Error downloading!")


def check_arg(args=None):
    parser = argparse.ArgumentParser(description='Script to archive podcast.')
    parser.add_argument('-f', '--file',
                        help='File containing RSS feeds for podcast',
                        default=None)
    parser.add_argument('-p', '--path',
                        help='Path to store podcast files',
                        default=os.getcwd())
    parser.add_argument('-u', '--url',
                        help='RSS URL for podcast',
                        default=None)
    parser.add_argument('-d', '--downloader',
                        help='Downloader to use for downloading files',
                        default='requests')
    parser.add_argument('-c', '--concurrent',
                        help='Number of concurrent downloads.',
                        type=int,
                        default=3)

    results = parser.parse_args(args)
    return (
        results.file,
        results.path,
        results.downloader,
        results.url,
        results.concurrent)


if __name__ == '__main__':
    file, path, downloader, url, num_concurrent = check_arg(sys.argv[1:])
    if file is None and url is None:
        raise ValueError("An input file containing URL or a URL is required!")
    if file is not None:
        if not os.path.isfile(file):
            raise ValueError("File not found!")
        with open(file, 'r') as fp:
            urls = fp.readlines()
            for url1 in urls:
                if url1.startswith('http'):
                    try:
                        pd = PodcastDownloader(
                            url1,
                            path,
                            downloader,
                            num_concurrent)
                        pd.get_new_items()
                        pd.download()
                    except Exception as e:
                        print(e)
    if url is not None:
        pd = PodcastDownloader(url, path, downloader, num_concurrent)
        pd.get_new_items()
        pd.download()
