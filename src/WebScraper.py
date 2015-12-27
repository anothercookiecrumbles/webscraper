import argparse
import os
import re
import sys
import urllib.request
from http.client import IncompleteRead
from subprocess import PIPE, Popen
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def usage():
    print("To use this webscraper, you need to specify the following arguments: ")
    print("-w \t the full URL of the website you want to scrape")
    print("-l \t the number of levels you want to scrape (default is 3)") #to be implemented
    print("-t \t the type of file (e.g. pdf, html")
    print("-d \t the download directory for the file(s)")
    print("-g \t find a specific pattern in the file(s)")

def run(args):
    if args.website != None:
        web_page = urllib.request.urlopen(args.website).read()
        soup = BeautifulSoup(web_page, "html.parser")

        file_type = args.type or "html" #default file_type to download is html
        links = soup.find_all(href=re.compile("." + file_type))

        download_dir = args.download_directory or "downloads/"
        if (not download_dir.endswith("/")):
            download_dir = download_dir + "/"
        if (links) and (not os.path.exists(download_dir)):
            # Small window of opportunity here for the directory to be created between the if-check and the creation
            # of directories in the next line. The makedirs implementation, though, catches/passes a FileExistsError.
                os.makedirs(download_dir)


        for link in links:
            absolute_url = urljoin(args.website, link.get('href'))
            web_file = urllib.request.urlopen(absolute_url)
            filename = absolute_url.rsplit('/')[-1]
            search_term = bytes(args.find, encoding='utf-8')
            try:
                #local_file = open(download_dir + filename, 'wb')
                #searchable = web_file.read()
                with Popen(['ps2ascii'], stdin=PIPE, stdout=PIPE) as proc:
                    text, err = proc.communicate(requests.get(absolute_url).content)
                    print("Searching " + filename)
                    if search_term in text:
                        print("Found " + args.find + " in " + filename + ". Writing local file...")
                        local_file = open(download_dir + filename, 'wb')
                        local_file.write(web_file.read())
                        local_file.close()
            except IncompleteRead:
                print("Error while trying to parse " + filename)
                continue
            web_file.close()

    else:
        usage()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--website')
    parser.add_argument('-t', '--type')
    parser.add_argument('-d', '--download_directory')
    parser.add_argument('-f', '--find')

    args = parser.parse_args()
    run(args)
    sys.exit(0)