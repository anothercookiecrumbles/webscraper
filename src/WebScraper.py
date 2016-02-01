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

class WebScraper:

    # If the user doesn't enter any arguments or fails to enter the mandatory arguments (i.e. website and search term),
    # then usage() is called.
    def usage(self):
        print("To use this webscraper, you need to specify the following arguments: ")
        print("-w \t the full URL of the website you want to scrape")
        print("-l \t the number of levels you want to scrape (default is 3)") #to be implemented
        print("-t \t the type of file (e.g. pdf, html). If no type is specified, all types will be searched. While "
              "this is useful, it'll also be slower.")
        print("-d \t the download directory for the file(s). If no directory is specified, the files will be "
              "downloaded to ./downloads")
        print("-g \t find a specific pattern in the file(s)")

    # Parses the URL, finds all links within the URL and then searches them all for the search term.
    # Note: search terms aren't case-insensitive at the moment, which is a bit of a bummer, and that needs
    # to change.
    def run(self):
        web_page = urllib.request.urlopen(self.website).read()
        soup = BeautifulSoup(web_page, "html.parser")

        # Effectively _collects_ all links that need to be searched based on user-input parameters.
        if (self.file_type != "*"):
            links = soup.find_all(href=re.compile("." + file_type))
        else:
            links = soup.find_all('a', href=True)

        # all searches are done in bytes; not sure how suboptimal this decision will be when I want to start handling
        # case-insensitive searches. We'll see.
        self.search_term = bytes(self.search_term, encoding='utf-8')

        # Iterate through all the links and start working your magic.
        # Note: The URL entered by the user isn't searched for the search_term. Should this change?
        for link in links:
            try:
                absolute_url = urljoin(self.website, link.get('href'))
                web_file = urllib.request.urlopen(absolute_url)
                filename = absolute_url.rsplit('/')[-1]
                print("Searching " + filename + "(" + absolute_url + ")")

                #Do this by the extension of the link instead of the file type. This'll allow you to search through
                #all links within a page if the file_type entered is "*" (i.e. ALL).

                #Overriding original file type, because well, at this point, we don't need it.
                #On the other hand, we need a normalised file extension to ensure the correct code path for the given
                #file extension's hit.
                file_type = filename[filename.rfind(".")+1:]

                try:
                    if file_type == 'pdf':
                        #local_file = open(download_dir + filename, 'wb')
                        #searchable = web_file.read()
                        self.search_pdf(absolute_url, filename, web_file)
                    elif file_type == 'txt':
                        self.search_text(filename, web_file)
                    elif file_type == 'docx':
                        # Open the .docx file
                        self.search_docx(filename, web_file)
                    else:
                        self.search_everything_else(soup, filename, web_file)
                except IncompleteRead as ire:
                    print("IncompleteRead Exception while trying to parse " + filename)
                    print(ire)
                    continue
                except Exception as ex:
                    print('Unexpected exception while trying to parse ' + filename)
                    print(ex)
                    continue

            except HTTPError as hte:
                print("Caught an HTTP error while trying to get: " + absolute_url)
                print(hte)
                continue
            except URLError as ue:
                print("Caught URL error while trying to get: " + absolute_url + ":" + ue )
                print(ue)
                continue

            finally:
                if web_file != None:
                    web_file.close()
                print("Finished.")

    # Logic to search PDF files, and if a match is found, download the file.
    def search_pdf(self, absolute_url, filename, web_file):
        with Popen(['ps2ascii'], stdin=PIPE, stdout=PIPE) as proc:
            text, err = proc.communicate(requests.get(absolute_url).content)
            if self.search_term in text:
                self.download(self.download_directory, filename, web_file)

    # Logic to search textfiles, and if a match is found, download the file.
    def search_text(self, filename, web_file):
        text_file = open(filename, "r")
        for line in text_file:
            if (self.search_term in line):
                self.download(self.download_directory, filename, web_file)
                break # breaks out of inner for-loop / if we've found a match once, we don't want to
                    # keep scanning the same file.
        text_file.close()

    # Logic to search docx files, and if a match is found, download the file.
    # TODO: do doc files need to be supported? Or, is docx, in 2016, good enough?
    def search_docx(self, filename, web_file):
        text = opendocx(filename)
        if search(text, self.search_term):
            self.download(self.download_directory, filename, web_file)

    # If the link is something else and the user's search_type is "*," the code path will end up here.
    def search_everything_else(self, soup, filename, web_file):
        find_string = soup.body.findAll(self.search_term);
        if find_string != []:
            self.download(self.download_directory, filename, web_file)

    # Download the file to the download directory that was entered by the user.
    def download(self, download_dir, filename, web_file):
        print("Found " + args.find + " in " + filename + ". Writing local file...")
        local_file = open(download_dir + filename, 'wb')
        local_file.write(web_file.read())
        local_file.close()
        return True

    # Sets up the download directory. If the user specifies a download directory, that's used. Else, the default is
    # used. If the os.makedirs command fails because of dodgy user input, then it fails fast and asks the user to fix
    # the issue.

    def setup_download_directory(self, download_directory):

        self.download_directory = download_directory or "download/"
        # Ensures the download_directory always ends with a "/" – this ensures that we don't have to worry about it
        # later.
        if (not self.download_directory.endswith("/")):
            self.download_directory = self.download_directory + "/"
        try:
            if (not os.path.exists(self.download_directory)):
                # Small window of opportunity here for the directory to be created between the if-check and the creation
                # of directories in the next line. The makedirs implementation, though, catches/passes a FileExistsError.
                os.makedirs(self.download_directory)
        except OSError as ose:
            print("Error caught while attempting to create the specified download directory. Please ensure that the "
                  "directory name ({0}) is valid and that you have correct entitlements and try again. Actual error: "
                  "({1}) -- ({2})".format(download_directory, ose.errno, ose.strerror))
            raise ose


    # Initialises the WebScraper based on arguments entered by the user. Valid arguments at this point are:
    # - website (i.e. the root URL from where the websearching/scraping should start)
    # - type (i.e. the type of URLs that should be searched. e,g.: pdf, docx, txt)
    # - download_directory (i.e. where the files should be downloaded)
    # - find (i.e. the term that the URLs are scanned for)
    # TODO: add a regex check for website to ensure that URLs are verified.
    def __init__(self, website, search_term, download_directory="download/", type="*"):
        if (website == None) or (search_term == None) or (website.strip() == "") or (search_term.strip() == ""):
            self.usage()
            raise Exception("All mandatory parameters haven't been set.")

        # Tries to ensure the download_directory exists and, if not, fails fast.
        self.setup_download_directory(download_directory)

        self.website = website
        self.search_term = search_term
        self.type = type

# Main function
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--website')
    parser.add_argument('-t', '--type')
    parser.add_argument('-d', '--download_directory')
    parser.add_argument('-f', '--find')

    args = parser.parse_args()
    try:
        scraper = WebScraper(args.website, args.find, args.download_directory, args.type)
        scraper.run()
        print("All done.")
        sys.exit(0)
    except Exception as ex:
        print("Caught error while attempting to create the WebScraper. Boom! Please fix the error(s) and try again.")