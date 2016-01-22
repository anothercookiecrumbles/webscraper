import argparse
import os
import re
import sys
import urllib.request

from http.client import IncompleteRead
from subprocess import PIPE, Popen
from urllib.parse import urljoin
from urllib.error import HTTPError
from urllib.error import URLError
from docx import search
from docx import opendocx

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

        file_type = args.type or "*" #default file_type to download is html

        if (file_type != "*"):
            links = soup.find_all(href=re.compile("." + file_type))
        else:
            links = soup.find_all('a', href=True)

        print(links)

        download_dir = args.download_directory or "downloads/"
        if (not download_dir.endswith("/")):
            download_dir = download_dir + "/"
        if (links) and (not os.path.exists(download_dir)):
            # Small window of opportunity here for the directory to be created between the if-check and the creation
            # of directories in the next line. The makedirs implementation, though, catches/passes a FileExistsError.
                os.makedirs(download_dir)

        for link in links:
            try:
                absolute_url = urljoin(args.website, link.get('href'))
                web_file = urllib.request.urlopen(absolute_url)
                filename = absolute_url.rsplit('/')[-1]
                search_term = bytes(args.find, encoding='utf-8')
                print("Searching " + filename + "(" + absolute_url + ")")

                #Do this by the extension of the link instead of the file type. This'll allow you to search through
                #all links within a page if the file_type entered is "*" (i.e. ALL).

                #Overriding original file type, because well, at this point, we don't need it.
                file_type = filename[filename.rfind(".")+1:]

                try:
                    if file_type == 'pdf':
                        #local_file = open(download_dir + filename, 'wb')
                        #searchable = web_file.read()
                        with Popen(['ps2ascii'], stdin=PIPE, stdout=PIPE) as proc:
                            text, err = proc.communicate(requests.get(absolute_url).content)
                            if search_term in text:
                                download(download_dir, filename, web_file)
                    elif file_type == 'txt':
                        text_file = open(filename, "r")
                        for line in text_file:
                            if (search_term in line):
                                download(download_dir, filename, web_file)
                                break # breaks out of inner for-loop / if we've found a match once, we don't want to
                                      # keep scanning the same file.
                        text_file.close()
                    elif file_type == 'docx':
                        # Open the .docx file
                            text = opendocx(filename)
                            if search(text, search_term):
                                download(text, download_dir, filename, web_file)
                    else:
                        find_string = soup.body.findAll(args.find);
                        if find_string != []:
                            download(download_dir, filename, web_file)
                except IncompleteRead as ire:
                    print("IncompleteRead Exception while trying to parse " + filename)
                    print(ire)
                    continue
                except Exception as ex:
                    print('Unexpected Exception while trying to parse ' + filename)
                    print(ex)
                    continue

            except HTTPError as hte:
                print("Caught an HTTP error while trying to get: " + absolute_url)
                print(hte)
                continue
            except URLError as ue:
                print("Caught URL error while trying to get: " + absolute_url)
                print(ue)
                continue

            finally:
                if web_file != None:
                    web_file.close()
                print("Finished.")

    else:
        usage()

def download(download_dir, filename, web_file):
    print("Found " + args.find + " in " + filename + ". Writing local file...")
    local_file = open(download_dir + filename, 'wb')
    local_file.write(web_file.read())
    local_file.close()
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--website')
    parser.add_argument('-t', '--type')
    parser.add_argument('-d', '--download_directory')
    parser.add_argument('-f', '--find')

    args = parser.parse_args()
    run(args)
    print("All done.")
    sys.exit(0)