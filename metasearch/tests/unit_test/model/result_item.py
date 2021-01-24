from django.test import TestCase
from metasearch.tests.test_utils import TestUtils
from metasearch.models import ResultItem

class ResultItemModelTests(TestCase):

  # Check if it correctly extracts the domain from the given URL
  def test_get_domain_extracts_the_domain_correctly(self):

    # [Success] URL with SSL, no subdomains
    item = ResultItem("Test Article 1", "https://example.com", "Google")
    self.assertEqual("example.com", item.get_domain())

    # [Success] URL with SSL, with subdomains (www)
    item = ResultItem("Test Article 2", "https://www.example.com", "Google")
    self.assertEqual("example.com", item.get_domain())

    # [Success] URL with SSL, with subdomains (not www)
    item = ResultItem("Test Article 3", "https://jp.example.com", "Google")
    self.assertEqual("example.com", item.get_domain())

    # [Success] URL without SSL, no subdomains
    item = ResultItem("Test Article 4", "http://example.com", "Google")
    self.assertEqual("example.com", item.get_domain())

    # [Success] URL without SSL, with subdomains (www)
    item = ResultItem("Test Article 5", "http://www.example.com", "Google")
    self.assertEqual("example.com", item.get_domain())

    # [Success] URL without SSL, with subdomains (not www)
    item = ResultItem("Test Article 6", "http://ja.example.com", "Google")
    self.assertEqual("example.com", item.get_domain())

  # Check if it sets the URL correctly
  def test_set_url_sets_the_url_correctly(self):
    # [Success] ResultItem having a correct URL
    item = ResultItem("Test Article 1", "https://example.com", "Google")
    self.assertEqual("https://example.com", item.get_url())
    item = ResultItem("Test Article 2", "https://example.com/join/", "Yahoo!")
    self.assertEqual("https://example.com/join/", item.get_url())
    item = ResultItem("Test Article 3", "http://example.org/handsome.html", "Bing")
    self.assertEqual("http://example.org/handsome.html", item.get_url())
    item = ResultItem("Test Article 4", "http://en.example.org/great/great/great/something", "Yandex")
    self.assertEqual("http://en.example.org/great/great/great/something", item.get_url())
    item = ResultItem("Test Article 5", "http://ex.example.gov/index.html/", "Google")
    self.assertEqual("http://ex.example.gov/index.html", item.get_url())

  # Check if it sets the source search engine correctly
  def test_set_engine_sets_the_source_search_engine_correctly(self):

    # [Success] ResultItem having "Google" as its source search engine
    item = ResultItem("Test Article 1", "https://example.com", "Google")
    self.assertEqual(["Google"], item.get_engine())

    # [Fail] ResultItem having "abcde" (undefined engine) as its source search engine
    item = ResultItem("Test Article 2", "https://example.com", "abcde")
    self.assertEqual([], item.get_engine())

    # [Success] ResultItem having both of "Google" and "Yahoo" as its source search engines
    item = ResultItem("Test Article 2", "https://example.com", "Google")
    self.assertTrue(item.set_engine("Yahoo!"))
    self.assertEqual(["Google", "Yahoo!"], item.get_engine())

    # [Fail] ResultItem having "google" (not capitalized) as its source search engine
    item = ResultItem("Test Article 2", "https://example.com", "google")
    self.assertEqual([], item.get_engine())

  # Check if it sets the rank in the search engine correctly
  def test_set_rank_correctly(self):

    # Returns pre-defined rank if no any ranks set explicitly
    item = ResultItem("Test Article 1", "https://example.com", "Google")
    self.assertEqual(ResultItem.DEFAULTRANK, item.get_highest_rank())
    self.assertEqual(ResultItem.DEFAULTRANK, item.get_lowest_rank())

    # Returns the rank given in the constractor if defined explicitly
    rank: int = 3
    item = ResultItem("Test Article 2", "https://example.com", "Google", rank)
    self.assertEqual(rank, item.get_highest_rank())
    self.assertEqual(rank, item.get_lowest_rank())

    # Returns the explicitly controlled rank even if given by set_rank 
    # after creating the object without explicit rank in the constractor
    rank: int = 3
    item = ResultItem("Test Article 3", "https://example.com", "Google")
    item.set_rank(rank)
    self.assertEqual(rank, item.get_highest_rank())
    self.assertEqual(rank, item.get_lowest_rank())

    # Returns correct ranks if multiple ranks are registered
    first_rank: int = 5
    second_rank: int = 3
    third_rank: int = 8
    item = ResultItem("Test Article 4", "https://example.com", "Google", first_rank)
    item.set_rank(second_rank)
    item.set_rank(third_rank)
    self.assertEqual(second_rank, item.get_highest_rank())
    self.assertEqual(third_rank, item.get_lowest_rank())

    # Returns default rank if illegal rank is given in the argument
    rank = -1024
    item = ResultItem("Test Article 5", "https://example.com", "Google", rank)
    self.assertEqual(ResultItem.DEFAULTRANK, item.get_highest_rank())
    self.assertEqual(ResultItem.DEFAULTRANK, item.get_lowest_rank())

    # Returns correct ranks even if multiple illegal ranks are given
    first_rank: int = 5
    second_rank: int = -1
    third_rank: int = 3
    fourth_rank: int = 800
    fifth_rank: int = 199
    item = ResultItem("Test Article 5", "https://example.com", "Google")
    item.set_rank(first_rank)
    item.set_rank(second_rank)
    item.set_rank(third_rank)
    item.set_rank(fourth_rank)
    item.set_rank(fifth_rank)
    self.assertEqual(third_rank, item.get_highest_rank())
    self.assertEqual(first_rank, item.get_lowest_rank())

  # Check if it sets the abstract (snippet) given from the search engine correctly
  def test_set_snippet_correctly(self):
    snippet: str = "sample snippet, sample snippet. This is a sample snippet."
    item = ResultItem("Test Article 1", "https://example.com", "Google")
    item.set_abstract(snippet)
    self.assertEqual(snippet, item.get_abstract())