<h1>README.md</h1>

<h2>SIMPLE WEBSITE CRAWLER</h2>

This is a straightforward Python script that:
- Given a URL searches all links within (nested to one level at the moment) based on the file type specified. By default, it looks for HTML but can handle PDFs as well.
- Looks for the search term in all _links_ of the chosen type
- Downloads these _links_ if a matching file type is found

To-do:
- Case-insensitive searches
- More complex searches (including searching with regexes)
- Write tests
- Allow for further nesting up to x levels deep, where x can be passed in by the user or default to 3.
- Probably make it slightly smarter such that it can run tasks in parallel and hence doesn’t take forever

This script has been written and tested on Mac OS X El Capitan with Python 3.5.

**Dependencies**

- Ghostscript v 9.18
- BeautifulSoup v 4.4.1
- Python-requests v 2.6.0
- lxml v 3.5
- docx v 0.2.4

**Usage**
 Simply run the script with the following parameters:

WebScraper.py -w website -t file_type -f search_term -d download_directory

where: 
- website is the website you want to look at 
- file_type is the type of file you want to scan
- search_term is the term you're looking for across all files
- download_directory is the directory where you want all the matched files downloaded
