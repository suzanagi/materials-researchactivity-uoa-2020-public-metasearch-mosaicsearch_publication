from bs4 import BeautifulSoup
from django.test import TestCase
from metasearch.models import ResultItem
from metasearch.search_modules.duckduckgo_search_module import (
  push_into_ResultItems,
  retrieve_result_page,
  pick_result_item_parts,
  pick_title_from,
  pick_url_from,
  pick_snippet_from
)


TEST_DATA_DIR = 'metasearch/tests/unit_test/view/scraping_modules/duckduckgo/test_data/'

class SearchModuleTests(TestCase):

  def test_retrieving_contents_01(self):
    # assert the picked result item part for the first item and the last item in the sample page
    expected_soup_01: BeautifulSoup = None
    expected_soup_10: BeautifulSoup = None
    with open(TEST_DATA_DIR + 'sample_result_item_part_01_01.html', mode='r') as f:
      expected_item_part_html: str = f.read()
      expected_soup_01 = BeautifulSoup(expected_item_part_html, "html.parser")
    with open(TEST_DATA_DIR + 'sample_result_item_part_01_10.html', mode='r') as f:
      expected_item_part_html: str = f.read()
      expected_soup_10 = BeautifulSoup(expected_item_part_html, "html.parser")
    actual_soups: list = None
    with open(TEST_DATA_DIR + 'sample_page_01.html', mode='r') as f:
      raw_result_page_html: str = f.read()
      soup = BeautifulSoup(raw_result_page_html, "html.parser")
      actual_soups = pick_result_item_parts(soup)
    self.assertEqual(str(expected_soup_01), str(actual_soups[0]))
    self.assertEqual(str(expected_soup_10), str(actual_soups[9]))

    # assert the picked title for the first item and the last item in the sample page
    expected_title: str = "Nagorno-Karabakh conflict - Wikipedia"
    actual_title: str = pick_title_from(actual_soups[0])
    self.assertEqual(expected_title, actual_title)
    expected_title = "Nagorno-Karabakh profile - BBC News"
    actual_title: str = pick_title_from(actual_soups[9])
    self.assertEqual(expected_title, actual_title)

    # assert the picked URL for the first item and the last item in the sample page
    expected_url: str = "https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict"
    actual_url: str = pick_url_from(actual_soups[0])
    self.assertEqual(expected_url, actual_url)
    expected_url = "https://www.bbc.com/news/world-europe-18270325"
    actual_url: str = pick_url_from(actual_soups[9])
    self.assertEqual(expected_url, actual_url)

    # assert the picked snippet for the first item and the last item in the sample page
    expected_snippet: str = "The Nagorno-Karabakh conflict is an ethnic and territorial conflict between Armenia and Azerbaijan over the disputed region of Nagorno-Karabakh, inhabited mostly by ethnic Armenians, and seven surrounding districts, inhabited mostly by Azerbaijanis until their expulsion during the Nagorno-Karabakh War, which are de facto controlled by the self-declared Republic of Artsakh, but are ..."
    actual_snippet: str = pick_snippet_from(actual_soups[0])
    self.assertEqual(expected_snippet, actual_snippet)
    expected_snippet = "The landlocked mountainous region of Nagorno-Karabakh is the subject of an unresolved dispute between Azerbaijan, in which it lies, and its ethnic Armenian majority, backed by neighbouring Armenia."
    actual_snippet = pick_snippet_from(actual_soups[9])
    self.assertEqual(expected_snippet, actual_snippet)

  def test_retrieving_contents_02(self):
    # assert the picked result item part for the first item and the last item in the sample page
    expected_soup_01: BeautifulSoup = None
    expected_soup_10: BeautifulSoup = None
    with open(TEST_DATA_DIR + 'sample_result_item_part_02_01.html', mode='r') as f:
      expected_item_part_html: str = f.read()
      expected_soup_01 = BeautifulSoup(expected_item_part_html, "html.parser")
    with open(TEST_DATA_DIR + 'sample_result_item_part_02_10.html', mode='r') as f:
      expected_item_part_html: str = f.read()
      expected_soup_10 = BeautifulSoup(expected_item_part_html, "html.parser")
    actual_soups: list = None
    with open(TEST_DATA_DIR + 'sample_page_02.html', mode='r') as f:
      raw_result_page_html: str = f.read()
      soup = BeautifulSoup(raw_result_page_html, "html.parser")
      actual_soups = pick_result_item_parts(soup)
    self.assertEqual(str(expected_soup_01), str(actual_soups[0]))
    self.assertEqual(str(expected_soup_10), str(actual_soups[9]))

    # assert the picked title for the first item and the last item in the sample page
    expected_title: str = "5G - The Japan Times"
    actual_title: str = pick_title_from(actual_soups[0])
    self.assertEqual(expected_title, actual_title)
    expected_title = "5G Availability Around the World - Lifewire"
    actual_title: str = pick_title_from(actual_soups[9])
    self.assertEqual(expected_title, actual_title)

    # assert the picked URL for the first item and the last item in the sample page
    expected_url: str = "https://www.japantimes.co.jp/tag/5g/"
    actual_url: str = pick_url_from(actual_soups[0])
    self.assertEqual(expected_url, actual_url)
    expected_url = "https://www.lifewire.com/5g-availability-world-4156244"
    actual_url: str = pick_url_from(actual_soups[9])
    self.assertEqual(expected_url, actual_url)

    # assert the picked snippet for the first item and the last item in the sample page
    expected_snippet: str = "Business / Corporate May 3, 2020. SoftBank's super-fast 5G network isn't very useful just yet. by Pavel Alpeyev. SoftBank Corp.'s fifth-generation wireless service in Japan is living up to ..."
    actual_snippet: str = pick_snippet_from(actual_soups[0])
    self.assertEqual(expected_snippet, actual_snippet)
    expected_snippet = "In 2018, Russia's largest mobile operator, Mobile TeleSystems (MTS), partnered with Samsung to run various 5G tests that included video calls, ultra-low latency video games, and 4K video streaming.These were performed to show that not only is 5G coming but that Samsung's 5G routers, tablets, and other devices are fully capable of running on a 5G network."
    actual_snippet = pick_snippet_from(actual_soups[9])
    self.assertEqual(expected_snippet, actual_snippet)

  def test_retrieving_contents_03(self):
    # assert the picked result item part for the first item and the last item in the sample page
    expected_soup_01: BeautifulSoup = None
    expected_soup_10: BeautifulSoup = None
    with open(TEST_DATA_DIR + 'sample_result_item_part_03_01.html', mode='r') as f:
      expected_item_part_html: str = f.read()
      expected_soup_01 = BeautifulSoup(expected_item_part_html, "html.parser")
    with open(TEST_DATA_DIR + 'sample_result_item_part_03_10.html', mode='r') as f:
      expected_item_part_html: str = f.read()
      expected_soup_10 = BeautifulSoup(expected_item_part_html, "html.parser")
    actual_soups: list = None
    with open(TEST_DATA_DIR + 'sample_page_03.html', mode='r') as f:
      raw_result_page_html: str = f.read()
      soup = BeautifulSoup(raw_result_page_html, "html.parser")
      actual_soups = pick_result_item_parts(soup)
    
    # assert the picked title for the first item and the last item in the sample page
    expected_title: str = "Japan Drone 2020"
    actual_title: str = pick_title_from(actual_soups[0])
    self.assertEqual(expected_title, actual_title)
    expected_title = "Drone Laws in Japan (Regulation updated for 2020)"
    actual_title: str = pick_title_from(actual_soups[9])
    self.assertEqual(expected_title, actual_title)

    # assert the picked URL for the first item and the last item in the sample page
    expected_url: str = "https://ssl.japan-drone.com/en_la/"
    actual_url: str = pick_url_from(actual_soups[0])
    self.assertEqual(expected_url, actual_url)
    expected_url = "https://dronesgator.com/japan-drone-laws/"
    actual_url: str = pick_url_from(actual_soups[9])
    self.assertEqual(expected_url, actual_url)

    # assert the picked snippet for the first item and the last item in the sample page

    expected_snippet: str = "\"Japan\'s Largest Drone Business Event: Japan Drone 2020 will be held at Makuhari Messe on September 29 and 30.\" -We are preparing for it by taking all the necessary safety and security..."
    actual_snippet: str = pick_snippet_from(actual_soups[0])
    self.assertEqual(expected_snippet, actual_snippet)

    expected_snippet = "What\'s interesting about flying drones in Japan? When you hear Unmanned aerial vehicle, the first With more people adopting the use of drones in Japan, few are aware of the laws involved given the..."
    actual_snippet = pick_snippet_from(actual_soups[9])
    self.assertEqual(expected_snippet, actual_snippet)
    

  def test_push_into_resultitems(self):
    search_results: list = []
    with open(TEST_DATA_DIR + 'sample_page_01.html', mode='r') as f:
      result_page: str = f.read()
      search_results = push_into_ResultItems(result_page)
    self.assertEqual(10, len(search_results))
    expected_first_item: ResultItem = ResultItem("Nagorno-Karabakh conflict - Wikipedia", "https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict", "DuckDuckGo", 1)
    self.assertEqual(str(expected_first_item), str(search_results[0]))
    expected_last_item: ResultItem = ResultItem("Nagorno-Karabakh profile - BBC News", "https://www.bbc.com/news/world-europe-18270325", "DuckDuckGo", 10)
    self.assertEqual(str(expected_last_item), str(search_results[9]))

  def test_retrieve_result_page_01(self):
    query: str = "5G in japan"
    result_page: str = retrieve_result_page(query)
    test_soup: BeautifulSoup = BeautifulSoup(result_page, "html.parser")
    result_part_soup: BeautifulSoup = test_soup.find("div", attrs={"results"})
    self.assertNotEqual(None, result_part_soup)

  def test_retrieve_result_page_02(self):
    query: str = repr('"5G in japan"')
    print(query)
    result_page: str = retrieve_result_page(query)
    test_soup: BeautifulSoup = BeautifulSoup(result_page, "html.parser")
    result_part_soup: BeautifulSoup = test_soup.find("div", attrs={"results"})
    self.assertNotEqual(None, result_part_soup)