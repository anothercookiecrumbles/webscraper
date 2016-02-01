import argparse
import sys
import os
import shutil

import unittest
from unittest.mock import patch
from unittest.mock import Mock
from unittest import mock

from src.WebScraper import WebScraper

class WebScraperTest(unittest.TestCase):

    #Tests if usage() is called when none of the mandatory arguments are passed into the WebScraper initializer.
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_no_args_are_passed(self, mock_method):
        with self.assertRaises(Exception) as context:
            ws = WebScraper(None, None, None, None)
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is called when no search term is passed into the WebScraper initializer.
    #I wish there was something similar to Junit Theories here...
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_search_term_is_absent(self, mock_method):
        with self.assertRaises(Exception) as context:
            WebScraper("www.anothercookiecrumbles.com", None, ".", "")
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is called when no website is passed into the WebScraper initializer.
    #I wish there was something similar to Junit Theories here...
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_website_is_absent(self, mock_method):
        with self.assertRaises(Exception) as context:
            WebScraper(None, "Pixar", ".", "")
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is called when the search term passed into the WebScraper initializer is a padded empty string.
    #I wish there was something similar to Junit Theories here...
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_search_term_is_a_padded_empty_string(self, mock_method):
        with self.assertRaises(Exception) as context:
            WebScraper("www.anothercookiecrumbles.com", " ", ".", "")
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is called when the search term passed into the WebScraper initializer is an empty string.
    #I wish there was something similar to Junit Theories here...
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_search_term_is_an_empty_string(self, mock_method):
        with self.assertRaises(Exception) as context:
            WebScraper("www.anothercookiecrumbles.com", "", ".", "")
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is called when the website that's passed into the WebScraper initializer is a padded empty string.
    #I wish there was something similar to Junit Theories here...
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_website_is_a_padded_empty_string(self, mock_method):
        with self.assertRaises(Exception) as context:
            WebScraper("  ", "Pixar", ".", "")
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is called when the website that's passed into the WebScraper initializer is an empty string.
    #I wish there was something similar to Junit Theories here...
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_website_is_an_empty_string(self, mock_method):
        with self.assertRaises(Exception) as context:
            WebScraper("", "Pixar", ".", "")
        self.assertTrue(mock_method.called)
        self.assertEqual(context.exception.args[0], "All mandatory parameters haven't been set.")

    #Tests if usage() is not called and all parameters are correctly set when the initializer is called.
    @mock.patch.object(WebScraper, 'usage')
    def test_init_when_all_parameters_are_set(self, mock_method):
        ws = WebScraper("www.anothercookiecrumbles.com", "Pixar", "download_dir", "pdf")
        self.assertFalse(mock_method.called) #usage() shouldn't be called.

        self.assertEqual(ws.search_term, "Pixar")
        self.assertEqual(ws.website, "www.anothercookiecrumbles.com")
        #The code adds the slash after the directory name if one isn't set when calling WebScraper.
        self.assertEqual(ws.download_directory, "download_dir/")
        self.assertEqual(ws.type, "pdf")

        ws = WebScraper("www.anothercookiecrumbles.com", "Pixar", "download_directory/", "pdf")
        self.assertEqual(ws.search_term, "Pixar")
        self.assertEqual(ws.website, "www.anothercookiecrumbles.com")
        #Ensure that when the user adds a slash, a second slash isn't added, i.e. it's download_directory/ and not
        #download_directory//.
        self.assertEqual(ws.download_directory, "download_directory/")
        self.assertEqual(ws.type, "pdf")

    def remove_directory(self, download_directory):
        if (os.path.exists("download")):
            shutil.rmtree(download_directory, True)
            #os.removedirs("download")

    #Tests setup_download_directory when no dirname is passed, and so the default dirname, download, is used.
    def test_setup_download_directory_when_no_dirname_is_passed(self):
        #Delete the existing download directory if one exists. If one does exist, and it's non-empty, then this method
        #will fail.
        self.remove_directory("download")
        ws = WebScraper("www.anothercookiecrumbles.com", "Pixar", None, "pdf")
        self.assertTrue(os.path.exists("download"))
        self.remove_directory("download") #cleanup

    def test_setup_download_directory_when_correct_dirname_is_passed_in(self):
        #Delete the existing download directory if one exists... is this too risky or can we assume that when people run
        #this test, there won't be data that someone needs still sticking around?
        download_directory = "download/download_test"
        self.remove_directory(download_directory)
        ws = WebScraper("www.anothercookiecrumbles.com", "Pixar", download_directory, "pdf")
        self.assertTrue(os.path.exists(download_directory))
        self.remove_directory(download_directory)

    def test_setup_download_directory_when_incorrect_dirname_is_passed_in(self):
        download_directory = "/boom/goes/the/dynamite"
        with self.assertRaises(Exception) as context:
            ws = WebScraper("www.anothercookiecrumbles.com", "Pixar", download_directory, "pdf")
        self.assertRaises(OSError)
        self.assertEqual(context.exception.args[0], 13)
        self.assertEqual(context.exception.args[1], "Permission denied")

    
