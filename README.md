**README.md**

**SIMPLE WEBSITE CRAWLER**

This is a straightforward Python script that:
- Given a URL searches all links within (nested to one level at the moment) based on the file type specified. By default, it looks for HTML but can handle PDFs as well.
- Looks for the search term in all _links_ of the chosen type
- Downloads these _links_ if a matching file type is found

To-do:
- Split up the different search functions by file type, i.e. PDFSearcher, TextSearcher, HTMLSearcher
- Write tests
- Allow for further nesting up to x levels deep, where x can be passed in by the user or default to 3.
- Probably make it slightly smarter such that it can run tasks in parallel and hence doesn’t take forever

This script has been written and tested on Mac OS X El Capitan with Python 3.5.

_Dependencies_

[Ghostscript v 9.18]
BeautifulSoup v 4.4.1
Python-requests v 2.6.0

_Usage_
 Simply run the script with the following parameters:

WebScraper.py -w <website> -t <file\_type> -f <search\_term> -d <download\_directory>