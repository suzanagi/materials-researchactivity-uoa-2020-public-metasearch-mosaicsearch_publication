import sys
from django.test import TestCase
from unittest.mock import patch
from metasearch.tests.test_utils import TestUtils
from metasearch.models import ResultItem
from metasearch.views import (
    CATEGORIES,
    metasearch, 
    result_classification,
    remove_result_item_duplication, 
    remove_movie_contents_from,
    pick_items_with_domain, 
    pick_encyclopedia_from_items, 
    pick_famous_news_agencies_from_items, 
    pick_online_news_agencies_from_items,
    pick_portal_and_blog_from_items,
    pick_highest_ranked_result_item,
    pick_lowest_ranked_result_item,
    pick_one_highest_and_one_lowest,
    pick_highest_and_lowest_if_contains_multiple_items,
    pick_one_from,
    separate_items_by_categories,
    separate_items_by_domain,
    selection_for_general_computers
)

class TestDataProvider:
  @staticmethod
  # Returns the test data with only one search result
  def test_data_duplication_01() -> list:
    items = []
    items.append(ResultItem("Article 01", "http://www.example1.com/example", "Google", 1))
    return items

  @staticmethod
  # Returns the test data with 3 totally same web page with the same URL
  def test_data_duplication_02() -> list:
    items = []
    items.append(ResultItem("Article 01", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 01", "http://www.example1.com/example", "Yahoo!", 2))
    items.append(ResultItem("Article 01", "http://www.example1.com/example", "Bing", 3))
    return items

  @staticmethod
  # Expected result item list after removing duplication from test_data_duplication_02
  def test_data_duplication_02_expected() -> list:
    items = []
    item = ResultItem("Article 01", "http://www.example1.com/example", "Google", 1)
    item.set_engine("Yahoo!")
    item.set_engine("Bing")
    item.set_rank(3)
    items.append(item)
    return items

  @staticmethod
  # Returns the test data with 10 result items including 2 articles having the totally same URL
  def test_data_duplication_03() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 8))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 1))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 2))
    items.append(ResultItem("Article 4", "http://www.example4.com/example", "Yandex", 1))
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Yahoo!", 8))
    items.append(ResultItem("Article 5", "http://www.example5.com/example", "Yahoo!", 1))
    items.append(ResultItem("Article 6", "http://www.example6.com/example", "Yahoo!", 2))
    items.append(ResultItem("Article 7", "http://www.example7.com/example", "Bing", 1))
    items.append(ResultItem("Article 8", "http://www.example8.com/example", "Bing", 2))
    items.append(ResultItem("Article 9", "http://www.example9.com/example", "Bing", 3))
    return items

  @staticmethod
  # Expected result item list after reoving duplication from test_data_duplication_03
  def test_data_duplication_03_expected() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 8))
    items[0].set_engine("Yahoo!")
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 1))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 2))
    items.append(ResultItem("Article 4", "http://www.example4.com/example", "Yandex", 1))
    items.append(ResultItem("Article 5", "http://www.example5.com/example", "Yahoo!", 1))
    items.append(ResultItem("Article 6", "http://www.example6.com/example", "Yahoo!", 2))
    items.append(ResultItem("Article 7", "http://www.example7.com/example", "Bing", 1))
    items.append(ResultItem("Article 8", "http://www.example8.com/example", "Bing", 2))
    items.append(ResultItem("Article 9", "http://www.example9.com/example", "Bing", 3))
    return items

  @staticmethod
  # Return the test data with 10 result items
  def test_data_domain_classification_01() -> list:
    # Search result items data to test the detection of following 5 domains: 
    # "abcde.com", 
    # "example.org", 
    # "sample.net", 
    # "abc.tokyo", 
    # "abcde.gov"
    # And all the appended items are including above domains

    items = []
    items.append(ResultItem("Article 1", "http://abc.tokyo/example", "Google"))
    items.append(ResultItem("Article 2", "https://abcde.gov/random.html", "Google"))
    items.append(ResultItem("Article 3", "https://abcde.gov", "Google"))
    items.append(ResultItem("Article 4", "https://www.abcde.gov/example", "Yandex"))
    items.append(ResultItem("Article 5", "http://www.abcde.com/example", "Yahoo!"))
    items.append(ResultItem("Article 6", "http://sample.net", "Yahoo!"))
    items.append(ResultItem("Article 7", "http://www.sample.net/example.html", "Yahoo!"))
    items.append(ResultItem("Article 8", "https://www.sample.net/example/example/images/example/example/example", "Bing"))
    items.append(ResultItem("Article 9", "http://www.example.org", "Bing"))
    items.append(ResultItem("Article 10", "https://example.org/example/samplepage.html", "Bing"))
    return items

  @staticmethod
  # Expected result item list after picking
  def test_data_domain_classification_01_expected() -> list:
    items = TestDataProvider.test_data_domain_classification_01()
    return [items, []]

  @staticmethod
  # Return the test data with 10 result items
  def test_data_domain_classification_02() -> list:
    # Search result items data to test the detection of following 5 domains: 
    # "abcde.com", 
    # "example.org", 
    # "sample.net", 
    # "abc.tokyo", 
    # "abcde.gov"
    # And none of the appended items are including above domains

    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google"))
    items.append(ResultItem("Article 4", "http://www.example4.com/example", "Yandex"))
    items.append(ResultItem("Article 5", "http://www.example1.com/example", "Yahoo!"))
    items.append(ResultItem("Article 6", "http://www.example5.com/example", "Yahoo!"))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    items.append(ResultItem("Article 10", "http://www.example9.com/example", "Bing"))
    return items

  @staticmethod
  # Expected result item list after picking
  def test_data_domain_classification_02_expected() -> list:
    items = TestDataProvider.test_data_domain_classification_02()
    return [[], items]

  @staticmethod
  # Return the test data with 10 result items
  def test_data_domain_classification_03() -> list:
    # Search result items data to test the detection of following 5 domains: 
    # "abcde.com", 
    # "example.org", 
    # "sample.net", 
    # "abc.tokyo", 
    # "abcde.gov"
    # And 3 of these domains are included in the following search result items

    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google"))
    items.append(ResultItem("Article 4", "https://example.org/example", "Yandex"))
    items.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!"))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!"))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing"))
    return items

  @staticmethod
  # Expected result item list after picking
  def test_data_domain_classification_03_expected() -> list:
    results = []
    results.append(ResultItem("Article 4", "https://example.org/example", "Yandex"))
    results.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!"))
    results.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!"))
    results.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing"))
    remains = []
    remains.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    remains.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    remains.append(ResultItem("Article 3", "http://www.example3.com/example", "Google"))
    remains.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    remains.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    remains.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    return [results, remains]

  @staticmethod
  # Return the test data with 10 result items including 2 search results from "wikipedia.org" domain
  def test_data_domain_classification_encyclopedia_01() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.org/example", "Google"))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    items.append(ResultItem("Article 3", "http://www.example3.co.jp/example", "Google"))
    items.append(ResultItem("Article 4", "http://example4.com/example", "Yandex"))
    items.append(ResultItem("Cyclone Ianos - Wikipedia", "https://en.wikipedia.org/wiki/Cyclone_Ianos", "Google"))
    items.append(ResultItem("Article 5", "http://www.example5.com/example", "Yahoo!"))
    items.append(ResultItem("Article 6", "http://www.example6.com/example", "Yahoo!"))
    items.append(ResultItem("Cyclone - Wikipedia", "https://en.wikipedia.org/wiki/Cyclone", "Bing"))
    items.append(ResultItem("Article 8", "http://www.example8.com", "Bing"))
    items.append(ResultItem("Article 9", "http://www.example9.com/example/sample/ex_pression", "Bing"))
    return items

  @staticmethod
  # Expected result item list after picking 
  def test_data_domain_classification_encyclopedia_01_expected() -> list:
    encyclopedia_items = []
    encyclopedia_items.append(ResultItem("Cyclone Ianos - Wikipedia", "https://en.wikipedia.org/wiki/Cyclone_Ianos", "Google"))
    encyclopedia_items.append(ResultItem("Cyclone - Wikipedia", "https://en.wikipedia.org/wiki/Cyclone", "Bing"))
    other_items = []
    other_items.append(ResultItem("Article 1", "http://www.example1.org/example", "Google"))
    other_items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    other_items.append(ResultItem("Article 3", "http://www.example3.co.jp/example", "Google"))
    other_items.append(ResultItem("Article 4", "http://example4.com/example", "Yandex"))
    other_items.append(ResultItem("Article 5", "http://www.example5.com/example", "Yahoo!"))
    other_items.append(ResultItem("Article 6", "http://www.example6.com/example", "Yahoo!"))
    other_items.append(ResultItem("Article 8", "http://www.example8.com", "Bing"))
    other_items.append(ResultItem("Article 9", "http://www.example9.com/example/sample/ex_pression", "Bing"))
    return [encyclopedia_items, other_items]

  @staticmethod
  # Return the test data with 10 result items including 1 result from aljazeera.com and 2 results from ruiters.com
  def test_data_domain_classification_famous_news_agency_01() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    items.append(ResultItem("焦点：米大統領選で空前の訴訟合戦", "https://jp.reuters.com/article/us-legal-battle-idJPKCN26G0OM", "Google"))
    items.append(ResultItem("Who is Amy Coney Barrett, Trump’s Supreme ...", "https://www.aljazeera.com/news/2020/9/26/who-is-amy-coney-barrett-trumps-nominee-to-supreme-court", "Yandex"))
    items.append(ResultItem("U.S. Supreme Court nominee Barrett would ...", "https://www.reuters.com/article/us-usa-court-recusal/u-s-supreme-court-nominee-barrett-would-have-final-say-on-recusal-calls-idUSKBN26I0D8", "Yahoo!"))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!"))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing"))
    return items

  @staticmethod
  # Expected result item list after picking
  def test_data_domain_classification_famous_news_agency_01_expected() -> list:
    results = []
    results.append(ResultItem("焦点：米大統領選で空前の訴訟合戦", "https://jp.reuters.com/article/us-legal-battle-idJPKCN26G0OM", "Google"))
    results.append(ResultItem("Who is Amy Coney Barrett, Trump’s Supreme ...", "https://www.aljazeera.com/news/2020/9/26/who-is-amy-coney-barrett-trumps-nominee-to-supreme-court", "Yandex"))
    results.append(ResultItem("U.S. Supreme Court nominee Barrett would ...", "https://www.reuters.com/article/us-usa-court-recusal/u-s-supreme-court-nominee-barrett-would-have-final-say-on-recusal-calls-idUSKBN26I0D8", "Yahoo!"))
    remains = []
    remains.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    remains.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    remains.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!"))
    remains.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    remains.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    remains.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    remains.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing"))
    return [results, remains]

  @staticmethod
  # Return the test data with 10 result items including 1 result from nytimes.com and 2 results from theguardian.com
  def test_data_domain_classification_online_news_agency_01() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    items.append(ResultItem("New York Times publishes Donald Trump's tax returns in election bombshell", "https://www.theguardian.com/us-news/2020/sep/27/new-york-times-publishes-donald-trumps-tax-returns-election", "Google"))
    items.append(ResultItem("Long-Concealed Records Show Trump’s Chronic Losses and Years of Tax Avoidance", "https://www.nytimes.com/interactive/2020/09/27/us/donald-trump-taxes.html", "Yandex"))
    items.append(ResultItem("US election polls look good for Joe Biden. But can they be trusted?", "https://www.theguardian.com/us-news/2020/sep/28/us-election-2020-are-polls-accurate", "Yahoo!"))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!"))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing"))
    return items

  @staticmethod
  # Expected result item list after picking
  def test_data_domain_classification_online_news_agency_01_expected() -> list:
    results = []
    results.append(ResultItem("New York Times publishes Donald Trump's tax returns in election bombshell", "https://www.theguardian.com/us-news/2020/sep/27/new-york-times-publishes-donald-trumps-tax-returns-election", "Google"))
    results.append(ResultItem("Long-Concealed Records Show Trump’s Chronic Losses and Years of Tax Avoidance", "https://www.nytimes.com/interactive/2020/09/27/us/donald-trump-taxes.html", "Yandex"))
    results.append(ResultItem("US election polls look good for Joe Biden. But can they be trusted?", "https://www.theguardian.com/us-news/2020/sep/28/us-election-2020-are-polls-accurate", "Yahoo!"))
    remains = []
    remains.append(ResultItem("Article 1", "http://www.example1.com/example", "Google"))
    remains.append(ResultItem("Article 2", "http://www.example2.com/example", "Google"))
    remains.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!"))
    remains.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!"))
    remains.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing"))
    remains.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing"))
    remains.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing"))
    return [results, remains]

  @staticmethod
  # Return the test data with 17 result items including 
  # 1 wikipedia, 
  # 5 famous news, 
  # 4 non-duplicated online news agency, 
  # and 7  other articles
  def test_data_domain_classification_complex_01() -> list:
    items = []
    # 1 wikipedia
    items.append(ResultItem("COVID-19 pandemic", "https://en.wikipedia.org/wiki/COVID-19_pandemic", "Google"))
    # 5 non-duplicated famous news (3 from Reuters and 2 from Aljazeera)
    item2 = ResultItem("Neanderthal genes linked to severe COVID-19; Mosquitoes cannot transmit the coronavirus", "https://www.reuters.com/article/us-health-coronavirus-science/neanderthal-genes-linked-to-severe-covid-19-mosquitoes-cannot-transmit-the-coronavirus-idUSKBN26L3HC", "Google")
    item2.set_engine("Yahoo!")
    item2.set_engine("Yandex")
    items.append(item2)
    items.append(ResultItem("Amazon and Big Tech cozy up to Biden camp with cash and connections", "https://www.reuters.com/article/us-usa-election-tech/amazon-and-big-tech-cozy-up-to-biden-camp-with-cash-and-connections-idUSKBN26M5O2", "Yahoo!"))
    items.append(ResultItem("How the year 2020 confounded Wall Street strategists", "https://www.reuters.com/article/us-usa-stocks-research-insight/how-the-year-2020-confounded-wall-street-strategists-idUSKBN26M5OG", "Google"))
    items.append(ResultItem("Putin, Macron call for Nagorno-Karabakh ceasefire as deaths mount", "https://www.aljazeera.com/news/2020/10/1/putin-macron-call-for-nagorno-karabakh-ceasefire-as-deaths-mount", "Yandex"))
    items.append(ResultItem("EU prepares for standoff over Turkish sanctions", "https://www.aljazeera.com/news/2020/10/1/eu-prepares-for-standoff-over-turkish-sanctions", "Google"))
    # 4 non-duplicated online news agency (3 from nytimes.com and 1 from theguardian.com)
    item7 = ResultItem("Trump Renews Fears of Voter Intimidation as G.O.P. Poll Watchers Mobilize", "https://www.nytimes.com/2020/09/30/us/trump-election-poll-watchers.html", "Google")
    item7.set_engine("Yahoo!")
    items.append(item7)
    items.append(ResultItem("Chris Wallace Calls Debate ‘a Terrible Missed Opportunity’", "https://www.nytimes.com/2020/09/30/business/media/chris-wallace-debate-moderator.html", "Google"))
    items.append(ResultItem("G.O.P. Alarmed by Trump’s Comments on Extremist Group, Fearing a Drag on the Party", "https://www.nytimes.com/2020/09/30/us/politics/trump-debate-white-supremacy.html", "Bing"))
    items.append(ResultItem("Brexit: EU launches legal action against UK for breaching withdrawal agreement", "https://www.theguardian.com/politics/2020/oct/01/brexit-eu-launches-legal-action-against-uk-for-breaching-withdrawal-agreement", "Bing"))
    # 7 non-duplicated other articles
    items.append(ResultItem("Latest Polls | FiveThirtyEight", "https://projects.fivethirtyeight.com/polls/", "Google"))
    items.append(ResultItem("Election 2020 - Forbes", "https://www.forbes.com/election-2020/#1a031cc0230b", "Google"))
    items.append(ResultItem("Election Dates for 2020 - Division of Elections - Florida ...", "https://dos.myflorida.com/elections/for-voters/election-dates/", "Yahoo!"))
    items.append(ResultItem("Nostradamus predictions on 2020 presidential elections and ...", "https://www.yearly-horoscope.org/nostradamus-predictions-on-2020-presidential-elections-and-donald-trump/", "Yahoo!"))
    items.append(ResultItem("US Presidential Election 2020 Winner Betting Odds | Politics ...", "https://www.oddschecker.com/politics/us-politics/us-presidential-election-2020/winner", "Yahoo!"))
    items.append(ResultItem("2020 Presidential Election Site - ProCon.org", "https://2020election.procon.org/", "Yahoo!"))
    items.append(ResultItem("2020 Primary Election Results | USA TODAY", "https://www.usatoday.com/elections/results/primaries/", "Yahoo!"))
    return items

  @staticmethod
  # Expected result item list after the classification
  def test_data_domain_classification_complex_01_expected() -> list:
      results = []
      # 1 wikipedia
      results.append([CATEGORIES["Encyclopedia"], ResultItem("COVID-19 pandemic", "https://en.wikipedia.org/wiki/COVID-19_pandemic", "Google")])
      # 5 famous news (3 from Reuters and 2 from Aljazeera)
      item: ResultItem = ResultItem("Neanderthal genes linked to severe COVID-19; Mosquitoes cannot transmit the coronavirus", "https://www.reuters.com/article/us-health-coronavirus-science/neanderthal-genes-linked-to-severe-covid-19-mosquitoes-cannot-transmit-the-coronavirus-idUSKBN26L3HC", "Google")
      item.set_engine("Yahoo!")
      item.set_engine("Yandex")
      results.append([CATEGORIES["Famous News Agencies"], item])
      results.append([CATEGORIES["Famous News Agencies"], ResultItem("Amazon and Big Tech cozy up to Biden camp with cash and connections", "https://www.reuters.com/article/us-usa-election-tech/amazon-and-big-tech-cozy-up-to-biden-camp-with-cash-and-connections-idUSKBN26M5O2", "Yahoo!")])
      results.append([CATEGORIES["Famous News Agencies"], ResultItem("How the year 2020 confounded Wall Street strategists", "https://www.reuters.com/article/us-usa-stocks-research-insight/how-the-year-2020-confounded-wall-street-strategists-idUSKBN26M5OG", "Google")])
      results.append([CATEGORIES["Famous News Agencies"], ResultItem("Putin, Macron call for Nagorno-Karabakh ceasefire as deaths mount", "https://www.aljazeera.com/news/2020/10/1/putin-macron-call-for-nagorno-karabakh-ceasefire-as-deaths-mount", "Yandex")])
      results.append([CATEGORIES["Famous News Agencies"], ResultItem("EU prepares for standoff over Turkish sanctions", "https://www.aljazeera.com/news/2020/10/1/eu-prepares-for-standoff-over-turkish-sanctions", "Google")])
      # 5 online news agency (3 from nytimes.com and 1 from theguardian.com, and 1 from usatoday)
      item = ResultItem("Trump Renews Fears of Voter Intimidation as G.O.P. Poll Watchers Mobilize", "https://www.nytimes.com/2020/09/30/us/trump-election-poll-watchers.html", "Google")
      item.set_engine("Yahoo!")
      results.append([CATEGORIES["Online News Agencies"], item])
      results.append([CATEGORIES["Online News Agencies"], ResultItem("Chris Wallace Calls Debate ‘a Terrible Missed Opportunity’", "https://www.nytimes.com/2020/09/30/business/media/chris-wallace-debate-moderator.html", "Google")])
      results.append([CATEGORIES["Online News Agencies"], ResultItem("G.O.P. Alarmed by Trump’s Comments on Extremist Group, Fearing a Drag on the Party", "https://www.nytimes.com/2020/09/30/us/politics/trump-debate-white-supremacy.html", "Bing")])
      results.append([CATEGORIES["Online News Agencies"], ResultItem("Brexit: EU launches legal action against UK for breaching withdrawal agreement", "https://www.theguardian.com/politics/2020/oct/01/brexit-eu-launches-legal-action-against-uk-for-breaching-withdrawal-agreement", "Bing")])
      results.append([CATEGORIES["Online News Agencies"], ResultItem("2020 Primary Election Results | USA TODAY", "https://www.usatoday.com/elections/results/primaries/", "Yahoo!")])
      # 6 other articles
      results.append([CATEGORIES["Portals and Blogs"], ResultItem("Latest Polls | FiveThirtyEight", "https://projects.fivethirtyeight.com/polls/", "Google")])
      results.append([CATEGORIES["Portals and Blogs"], ResultItem("Election 2020 - Forbes", "https://www.forbes.com/election-2020/#1a031cc0230b", "Google")])
      results.append([CATEGORIES["Portals and Blogs"], ResultItem("Election Dates for 2020 - Division of Elections - Florida ...", "https://dos.myflorida.com/elections/for-voters/election-dates/", "Yahoo!")])
      results.append([CATEGORIES["Portals and Blogs"], ResultItem("Nostradamus predictions on 2020 presidential elections and ...", "https://www.yearly-horoscope.org/nostradamus-predictions-on-2020-presidential-elections-and-donald-trump/", "Yahoo!")])
      results.append([CATEGORIES["Portals and Blogs"], ResultItem("US Presidential Election 2020 Winner Betting Odds | Politics ...", "https://www.oddschecker.com/politics/us-politics/us-presidential-election-2020/winner", "Yahoo!")])
      results.append([CATEGORIES["Portals and Blogs"], ResultItem("2020 Presidential Election Site - ProCon.org", "https://2020election.procon.org/", "Yahoo!")])
      return results

  @staticmethod
  # Return the test data with 10 result with ranks
  # 1 x #1
  # 4 x #5
  # 3 x #7
  # 1 x #8
  # 1 x #9
  def test_data_rank_comparison_01() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 5))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 7))
    items.append(ResultItem("Article 4", "https://example.org/example", "Yandex", 5))
    items.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 5))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!", 7))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 8))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing", 5))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing", 7))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 9))
    return items

  @staticmethod
  # Expected result item after picking the highest ranked item
  def test_data_rank_comparison_01_expected_highest() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    return items

  @staticmethod
  # Expected result item after picking the lowest ranked item
  def test_data_rank_comparison_01_expected_lowest() -> list:
    items = []
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 9))
    return items

  @staticmethod
  # Return the test data with with 10 result with ranks
  # 3 x #1
  # 2 x #5
  # 3 x #7
  # 2 x #9
  def test_data_rank_comparison_02() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 5))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 7))
    items.append(ResultItem("Article 4", "https://example.org/example", "Yandex", 1))
    items.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 1))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!", 7))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 9))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing", 5))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing", 7))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 9))
    return items

  @staticmethod
  # Expected result item after picking the highest ranked item
  def test_data_rank_comparison_02_expected_highest() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 4", "https://example.org/example", "Yandex", 1))
    items.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 1))
    return items

  @staticmethod
  # Expected result item after picking the lowest ranked item
  def test_data_rank_comparison_02_expected_lowest() -> list:
    items = []
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 9))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 9))
    return items

  @staticmethod
  # Return the 10 piece of test data with categorization information defined as CATEGORIES
  def test_data_separate_items_by_categories_01() -> list:
    items = []
    items.append((CATEGORIES["Encyclopedia"], ResultItem("Article 1", "http://www.example1.com/example", "Google", 1)))
    items.append((CATEGORIES["Famous News Agencies"], ResultItem("Article 2", "http://www.example2.com/example", "Google", 5)))
    item = ResultItem("Article 3", "http://www.example3.com/example", "Google", 7)
    item.set_engine("Yahoo!")
    item.set_rank(9)
    items.append((CATEGORIES["Famous News Agencies"], item))
    items.append((CATEGORIES["Online News Agencies"], ResultItem("Article 4", "https://example.org/example", "Yandex", 1)))
    items.append((CATEGORIES["Online News Agencies"], ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 1)))
    items.append((CATEGORIES["Online News Agencies"], ResultItem("Article 6", "https://www.abcde.com", "Yahoo!", 7)))
    items.append((CATEGORIES["Portals and Blogs"], ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 9)))
    items.append((CATEGORIES["Portals and Blogs"], ResultItem("Article 8", "http://www.example7.com/example", "Bing", 5)))
    items.append((CATEGORIES["Portals and Blogs"], ResultItem("Article 9", "http://www.example8.com/example", "Bing", 7)))
    items.append((CATEGORIES["Portals and Blogs"], ResultItem("Article 10", "http://www.sample.net/example", "Bing", 9)))
    return items

  @staticmethod
  # Expected result item after separating by categories
  def test_data_separate_items_by_categories_01_expected() -> dict:
    item3 = ResultItem("Article 3", "http://www.example3.com/example", "Google", 7)
    item3.set_engine("Yahoo!")
    item3.set_rank(9)
    items: dict = {
      CATEGORIES["Encyclopedia"]: [
        ResultItem("Article 1", "http://www.example1.com/example", "Google", 1)
      ],
      CATEGORIES["Famous News Agencies"]: [
        ResultItem("Article 2", "http://www.example2.com/example", "Google", 5),
        item3
      ],
      CATEGORIES["Online News Agencies"]: [
        ResultItem("Article 4", "https://example.org/example", "Yandex", 1),
        ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 1),
        ResultItem("Article 6", "https://www.abcde.com", "Yahoo!", 7)
      ],
      CATEGORIES["Portals"]: [],
      CATEGORIES["Blogs"]: [],
      CATEGORIES["Portals and Blogs"]: [
        ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 9),
        ResultItem("Article 8", "http://www.example7.com/example", "Bing", 5),
        ResultItem("Article 9", "http://www.example8.com/example", "Bing", 7),
        ResultItem("Article 10", "http://www.sample.net/example", "Bing", 9)
      ]
    }
    return items

  @staticmethod
  # Return the test data with 10 result with ranks
  def test_data_separate_items_by_domains_01() -> list:
    items = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 8))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 1))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 2))
    items.append(ResultItem("Article 4", "http://www.example3.com/samplepage.html", "Yandex", 1))
    items.append(ResultItem("Article 5", "https://example3.com/example/hogehoge/abcde.html", "Yahoo!", 1))
    items.append(ResultItem("Article 6", "http://example3.com/example", "Yahoo!", 2))
    items.append(ResultItem("Article 7", "http://example3.com/example/abcde", "Bing", 1))
    items.append(ResultItem("Article 8", "http://www.example3.org/example", "Bing", 2))
    items.append(ResultItem("Article 9", "http://www.example9.co.jp/example", "Bing", 3))
    items.append(ResultItem("Article 10", "https://example9.co.jp/hogehoge/example/abcde.html", "Bing", 5))
    return items

  @staticmethod
  # Expected result item after separating the data from test_data_separate_items_by_domains_01 by domains 
  def test_data_separate_items_by_domains_01_expected() -> dict:
    items: dict = {
      "example1.com": [ResultItem("Article 1", "http://www.example1.com/example", "Google", 8)],
      "example2.com": [ResultItem("Article 2", "http://www.example2.com/example", "Google", 1)],
      "example3.com": [
        ResultItem("Article 3", "http://www.example3.com/example", "Google", 2),
        ResultItem("Article 4", "http://www.example3.com/samplepage.html", "Yandex", 1),
        ResultItem("Article 5", "https://example3.com/example/hogehoge/abcde.html", "Yahoo!", 1),
        ResultItem("Article 6", "http://example3.com/example", "Yahoo!", 2),
        ResultItem("Article 7", "http://example3.com/example/abcde", "Bing", 1)
      ],
      "example3.org": [ResultItem("Article 8", "http://www.example3.org/example", "Bing", 2)],
      "example9.co.jp": [
        ResultItem("Article 9", "http://www.example9.co.jp/example", "Bing", 3),
        ResultItem("Article 10", "https://example9.co.jp/hogehoge/example/abcde.html", "Bing", 5)
      ]
    }
    return items

  @staticmethod
  # Return one result data with rank to check if the random pick function works correctly
  def test_data_pick_one_highest_and_one_lowest_01() -> list:
    items: list = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 8))
    return items

  @staticmethod
  # Expected result item after picking 1 item from the above test data
  def test_data_pick_one_highest_and_one_lowest_01_expected() -> list:
    return TestDataProvider.test_data_pick_one_highest_and_one_lowest_01()

  @staticmethod
  # Return two results data with ranks to check if the random pick function works correctly
  def test_data_pick_one_highest_and_one_lowest_02() -> list:
    items: list = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 8))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 1))
    return items

  @staticmethod
  # Expected result item after picking 2 item from the above test data
  def test_data_pick_one_highest_and_one_lowest_02_expected() -> list:
    return TestDataProvider.test_data_pick_one_highest_and_one_lowest_02()

  @staticmethod
  # Return normal 10 results data with different ranks
  def test_data_pick_one_highest_and_one_lowest_03() -> list:
    items: list = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 2))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 3))
    items.append(ResultItem("Article 4", "https://example.org/example", "Yandex", 4))
    items.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 5))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!", 6))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 7))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing", 8))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing", 9))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 10))
    return items
  
  @staticmethod
  # Expected result item after picking 2 items (highest and lowest-ranked item) from the above test data
  def test_data_pick_one_highest_and_one_lowest_03_expected() -> list:
    items: list = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 10))
    return items

  @staticmethod
  # Return 10 results data including duplciated ranks between different search engines
  def test_data_pick_one_highest_and_one_lowest_04() -> list:
    items: list = []
    items.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    items.append(ResultItem("Article 2", "http://www.example2.com/example", "Google", 2))
    items.append(ResultItem("Article 3", "http://www.example3.com/example", "Google", 3))
    items.append(ResultItem("Article 4", "https://example.org/example", "Yandex", 3))
    items.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 1))
    items.append(ResultItem("Article 6", "https://www.abcde.com", "Yahoo!", 2))
    items.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 10))
    items.append(ResultItem("Article 8", "http://www.example7.com/example", "Bing", 8))
    items.append(ResultItem("Article 9", "http://www.example8.com/example", "Bing", 9))
    items.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 10))
    return items

  @staticmethod
  # Expected result item after picking 2 items (highest and lowest-ranked items) from the above test data
  # Returns the candidates for the highest-ranked items in the first element of the retured list
  # and the candidates for the lowest-ranked items in the second element of the returned list
  def test_data_pick_one_highest_and_one_lowest_04_expected() -> list:
    highest: list = []
    highest.append(ResultItem("Article 1", "http://www.example1.com/example", "Google", 1))
    highest.append(ResultItem("Article 5", "http://abcde.com/example.html", "Yahoo!", 1))
    lowest: list = []
    lowest.append(ResultItem("Article 7", "http://www.example6.com/example", "Yahoo!", 10))
    lowest.append(ResultItem("Article 10", "http://www.sample.net/example", "Bing", 10))
    return [highest, lowest]

class MockSearchModule:
  def mock_google_search(self) -> list:
    results = []
    results.append(ResultItem("Article 01", "http://www.googleexample1.com", "Google"))  
    results.append(ResultItem("Article 02", "http://www.googleexample2.com", "Google"))
    results.append(ResultItem("Article 03", "http://www.googleexample3.com", "Google"))
    results.append(ResultItem("Article 04", "https://googleexample4.org/start.html", "Google"))
    results.append(ResultItem("Article 05", "https://googleexample5.org/middle.html", "Google"))
    results.append(ResultItem("Article 06", "https://googleexample6.org/end.pdf", "Google"))
    results.append(ResultItem("Article 07", "https://www.googleexample7.com", "Google"))
    results.append(ResultItem("Article 08", "https://www.googleexample8.com", "Google"))
    results.append(ResultItem("Article 09", "https://www.googleexample9.com", "Google"))
    results.append(ResultItem("Article 10", "http://en.commonexample.com/trial/", "Google"))
    for i in range(0, 10):
      results[i].set_rank(i + 1)
    return results  

  def mock_yahoo_search(self) -> list:
    results = []
    results.append(ResultItem("Article 01", "http://www.yahooexample1.com", "Yahoo!"))  
    results.append(ResultItem("Article 02", "http://www.yahooexample2.com", "Yahoo!"))
    results.append(ResultItem("Article 03", "http://www.yahooexample3.com", "Yahoo!"))
    results.append(ResultItem("Article 04", "https://yahooexample4.org/start.html", "Yahoo!"))
    results.append(ResultItem("Article 05", "https://yahooexample5.org/middle.html", "Yahoo!"))
    results.append(ResultItem("Article 06", "https://yahooexample6.org/end.pdf", "Yahoo!"))
    results.append(ResultItem("Article 07", "https://www.yahooexample7.com", "Yahoo!"))
    results.append(ResultItem("Article 08", "https://www.yahooexample8.com", "Yahoo!"))
    results.append(ResultItem("Article 09", "https://www.yahooexample9.com", "Yahoo!"))
    results.append(ResultItem("Article 10", "http://en.commonexample.com/trial/", "Yahoo!"))
    for i in range(0, 10):
      results[i].set_rank(i + 1)
    return results  

class MetasearchFunctionTests(TestCase):
  # Check whether the actual list of search results contains the element of the expected list of search results by the length of the list and 3 points of each result item: title, URL, and string expression of the ResultItem object
  def compare_the_list_of_result_items(self, method_name: str, expected: list, actual: list):
    # Make a log
    print("\nChecking by comparing two lists for the test", str(method_name))

    # Make an instance list of title, URL, string expression to compare for the actual and expected list data
    actual_title_list = TestUtils.get_title_list_from(actual)
    actual_url_list = TestUtils.get_url_list_from(actual)
    actual_str_expression_list = TestUtils.get_str_expression_list_from(actual)

    # Assertion
    try:
      self.assertEqual(len(expected), len(actual))
      for i in range(0, len(expected)):
        self.assertTrue(expected[i].get_title() in actual_title_list)
        self.assertTrue(expected[i].get_url() in actual_url_list)
        self.assertTrue(str(expected[i]) in actual_str_expression_list)
      print("OK")
    except AssertionError as e:
      print("Assert FAILED.")
      print("Expected: ")
      TestUtils.print_search_result_item_list(expected)
      print("Actual: ")
      TestUtils.print_search_result_item_list(actual)
      raise e
  
  @patch('metasearch.search_modules.google_search_module.googleSearch', MockSearchModule.mock_google_search)
  @patch('metasearch.search_modules.yahoo_search_module.yahooSearch', MockSearchModule.mock_yahoo_search)
  def test_metasearch(self):
    pass

  def test_removing_search_result_item_duplication_works_correctly(self):
    # Removing of the duplication of search result items works fine with only one item
    raw_search_results: list = TestDataProvider.test_data_duplication_01()
    search_result_without_duplication: list = remove_result_item_duplication(raw_search_results)
    expected_search_result: list = raw_search_results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": first case", expected_search_result, search_result_without_duplication)
    # Removing of the duplication works correctly with only one article retrieved from 3 search engines
    raw_search_results: list = TestDataProvider.test_data_duplication_02()
    search_result_without_duplication: list = remove_result_item_duplication(raw_search_results)
    expected_search_result: list = TestDataProvider.test_data_duplication_02_expected() 
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": second case", expected_search_result, search_result_without_duplication)
    # Removing of the duplicaiton works correctly with only one duplicaiton in the result list
    raw_search_results: list = TestDataProvider.test_data_duplication_03()
    search_result_without_duplication: list = remove_result_item_duplication(raw_search_results)
    expected_search_result: list = TestDataProvider.test_data_duplication_03_expected()
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": third case", expected_search_result, search_result_without_duplication)

  def test_categorize_search_result_item_classification_by_domain(self): 
    # Prepare the domain to be detected
    domains = ["abcde.com", "example.org", "sample.net", "abc.tokyo", "abcde.gov"]
    
    # Prepare the first search result items to detect their domains
    items = TestDataProvider.test_data_domain_classification_01()
    expected_items = TestDataProvider.test_data_domain_classification_01_expected()
    expected_results_with_domains = expected_items[0]
    expected_remains_without_domains = expected_items[1]
    # Pick up the search results including the above domains
    actual_results_picked_up = pick_items_with_domain(items, domains)
    actual_results_with_domains = actual_results_picked_up[0]
    actual_remains_without_domains = actual_results_picked_up[1]

    # Compare to check the results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": first case", expected_results_with_domains, actual_results_with_domains)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": first case", expected_remains_without_domains, actual_remains_without_domains)

    # Prepare the second search result items to detect their domains
    items = TestDataProvider.test_data_domain_classification_02()
    expected_items = TestDataProvider.test_data_domain_classification_02_expected()
    expected_results_with_domains = expected_items[0]
    expected_remains_without_domains = expected_items[1]
    # Pick up the search results including the above domains
    actual_results_picked_up = pick_items_with_domain(items, domains)
    actual_results_with_domains = actual_results_picked_up[0]
    actual_remains_without_domains = actual_results_picked_up[1]
    # Compare to check the results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": second case", expected_results_with_domains, actual_results_with_domains)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": second case", expected_remains_without_domains, actual_remains_without_domains)

    # Prepare the third search result items to detect their domains
    items = TestDataProvider.test_data_domain_classification_03()
    expected_items = TestDataProvider.test_data_domain_classification_03_expected()
    expected_results_with_domains = expected_items[0]
    expected_remains_without_domains = expected_items[1]
    # Pick up the search results including the above domains
    actual_results_picked_up = pick_items_with_domain(items, domains)
    actual_results_with_domains = actual_results_picked_up[0]
    actual_remains_without_domains = actual_results_picked_up[1]
    # Compare to check the results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": third case", expected_results_with_domains, actual_results_with_domains)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": third case", expected_remains_without_domains, actual_remains_without_domains)
 
  def test_categorize_search_result_item_classified_as_encyclopedia(self):
    # Pick up the search results categorized as an "Encyclopedia" 
    original_search_results: list = TestDataProvider.test_data_domain_classification_encyclopedia_01()
    expected_categorization_results: list = TestDataProvider.test_data_domain_classification_encyclopedia_01_expected()[0]
    expected_categorization_remains: list = TestDataProvider.test_data_domain_classification_encyclopedia_01_expected()[1]
    actual_results: list = pick_encyclopedia_from_items(original_search_results)
    actual_categorization_results: list = actual_results[0]
    actual_categorization_remains: list = actual_results[1]
    # Assert the "Categorized" results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": categorized results", expected_categorization_results, actual_categorization_results)
    # Assert not categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": not categorized results", expected_categorization_remains, actual_categorization_remains)

  def test_categorize_search_result_item_classified_as_famous_news_media(self):
    # Pick up the search results categorized as an "Famous news media"
    original_search_results: list = TestDataProvider.test_data_domain_classification_famous_news_agency_01()
    expected_categorization_results: list = TestDataProvider.test_data_domain_classification_famous_news_agency_01_expected()[0]
    expected_categorization_remains: list = TestDataProvider.test_data_domain_classification_famous_news_agency_01_expected()[1]
    actual_results: list = pick_famous_news_agencies_from_items(original_search_results)
    actual_categorization_results: list = actual_results[0]
    actual_categorization_remains: list = actual_results[1]
    # Assert categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": categorized results", expected_categorization_results, actual_categorization_results)
    # Assert not categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": not categorized results", expected_categorization_remains, actual_categorization_remains)

  def test_categorize_search_result_item_classified_as_online_news_agency(self):
    original_search_results: list = TestDataProvider.test_data_domain_classification_online_news_agency_01()
    expected_categorization_results: list = TestDataProvider.test_data_domain_classification_online_news_agency_01_expected()[0]
    expected_categorization_remains: list = TestDataProvider.test_data_domain_classification_online_news_agency_01_expected()[1]
    actual_results: list = pick_online_news_agencies_from_items(original_search_results)
    actual_categorization_results: list = actual_results[0]
    actual_categorization_remains: list = actual_results[1]
    # Assert categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": categorized results", expected_categorization_results, actual_categorization_results)
    # Assert not categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": not categorized results", expected_categorization_remains, actual_categorization_remains)

  def test_categorize_uncategorized_portals_and_blogs(self):
    # pick_portal_and_blog_from_items function now just returns all items given to the argument
    # so check if it returns the given items array as it is

    '''test set 1'''
    original_search_results: list = TestDataProvider.test_data_domain_classification_01()
    expected_categorization_results: list = original_search_results
    expected_categorization_remains: list = []
    actual_results: list = pick_portal_and_blog_from_items(original_search_results)
    actual_categorization_results: list = actual_results[0]
    actual_categorization_remains: list = actual_results[1]
    # Assert categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": categorized results", expected_categorization_results, actual_categorization_results)
    # Assert not categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": not categorized results", expected_categorization_remains, actual_categorization_remains)

    '''test set 2'''
    original_search_results: list = TestDataProvider.test_data_domain_classification_02()
    expected_categorization_results: list = original_search_results
    expected_categorization_remains: list = []
    actual_results: list = pick_portal_and_blog_from_items(original_search_results)
    actual_categorization_results: list = actual_results[0]
    actual_categorization_remains: list = actual_results[1]
    # Assert categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": categorized results", expected_categorization_results, actual_categorization_results)
    # Assert not categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": not categorized results", expected_categorization_remains, actual_categorization_remains)

    '''test set 3'''
    original_search_results: list = TestDataProvider.test_data_domain_classification_03()
    expected_categorization_results: list = original_search_results
    expected_categorization_remains: list = []
    actual_results: list = pick_portal_and_blog_from_items(original_search_results)
    actual_categorization_results: list = actual_results[0]
    actual_categorization_remains: list = actual_results[1]
    # Assert categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": categorized results", expected_categorization_results, actual_categorization_results)
    # Assert not categorized results
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": not categorized results", expected_categorization_remains, actual_categorization_remains)

  def test_remove_movie_contents_from_works_correctly(self):
    ''' test set 1 : in case the list doesn't contains any items '''
    original_search_results: list = []
    actual_results: list = remove_movie_contents_from(original_search_results)
    self.assertTrue(len(actual_results) == 0)

    ''' test set 2 : in case the list doesn't contains any items having the domains to be removed '''
    original_search_results: list = [
      ResultItem("Article 1", "http://www.example1.com/example", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo", 2)
    ]
    actual_results: list = remove_movie_contents_from(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 1", original_search_results, actual_results)

    ''' test set 3 : in case the list is including an item which has the domain to be removed in its URL '''
    original_search_results: list = [
      ResultItem("Article 1", "https://www.youtube.com/watch?v=abcdefghijklmn", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo", 2) 
    ]
    expected_results: list = [
      original_search_results[1]
    ]
    actual_results: list = remove_movie_contents_from(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 2", expected_results, actual_results)

    ''' test set 4 : in case all of the items in the list are having the domains should be removed from the list '''
    original_search_results: list = [
      ResultItem("Article 1", "https://www.youtube.com/watch?v=abcdefghijklmn", "Google", 1),
      ResultItem("Article 2", "https://www.youtube.com/watch?v=ABCDEFGHIJKLMN", "Yahoo", 2) 
    ]
    actual_results: list = remove_movie_contents_from(original_search_results)
    self.assertEqual(0, len(actual_results))

  def test_result_classification(self):
    original_search_results: list = TestDataProvider.test_data_domain_classification_complex_01()
    expected_categorization: list = TestDataProvider.test_data_domain_classification_complex_01_expected()
    actual_results: list = result_classification(original_search_results)

    # Assert the number of categorizations
    ex_enc: int = 0
    ex_fam: int = 0
    ex_onl: int = 0
    ex_por: int = 0
    ex_blo: int = 0
    ex_pab: int = 0
    ac_enc: int = 0
    ac_fam: int = 0
    ac_onl: int = 0
    ac_por: int = 0
    ac_blo: int = 0
    ac_pab: int = 0
    for item in expected_categorization:
      if item[0] == CATEGORIES["Encyclopedia"]:
        ex_enc = ex_enc + 1
      elif item[0] == CATEGORIES["Famous News Agencies"]:
        ex_fam = ex_fam + 1
      elif item[0] == CATEGORIES["Online News Agencies"]:
        ex_onl = ex_onl + 1
      elif item[0] == CATEGORIES["Portals"]:
        ex_por = ex_por + 1
      elif item[0] == CATEGORIES["Blogs"]:
        ex_blo = ex_blo + 1
      elif item[0] == CATEGORIES["Portals and Blogs"]:
        ex_pab = ex_pab + 1
      else:
        raise KeyError
    for item in actual_results:
      if item[0] == CATEGORIES["Encyclopedia"]:
        ac_enc = ac_enc + 1
      elif item[0] == CATEGORIES["Famous News Agencies"]:
        ac_fam = ac_fam + 1
      elif item[0] == CATEGORIES["Online News Agencies"]:
        ac_onl = ac_onl + 1
      elif item[0] == CATEGORIES["Portals"]:
        ac_por = ac_por + 1
      elif item[0] == CATEGORIES["Blogs"]:
        ac_blo = ac_blo + 1
      elif item[0] == CATEGORIES["Portals and Blogs"]:
        ac_pab = ac_pab + 1
      else:
        raise KeyError
    self.assertEqual(ex_enc, ac_enc)
    self.assertEqual(ex_fam, ac_fam)
    self.assertEqual(ex_onl, ac_onl)
    self.assertEqual(ex_por, ac_por)
    self.assertEqual(ex_blo, ac_blo)
    ex_list: list = []
    for results in expected_categorization:
      ex_list.append(results[1])
    ac_list: list = []
    for results in actual_results:
      ac_list.append(results[1])
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name, ex_list, ac_list)

  def test_pick_highest_ranked_item_works_correctly(self):
    ''' test set 1 '''
    original_search_results: list = TestDataProvider.test_data_rank_comparison_01()
    expected_results: list = TestDataProvider.test_data_rank_comparison_01_expected_highest()
    actual_results: list = pick_highest_ranked_result_item(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 1", expected_results, actual_results)

    ''' test set 2 '''
    original_search_results: list = TestDataProvider.test_data_rank_comparison_02()
    expected_results: list = TestDataProvider.test_data_rank_comparison_02_expected_highest()
    actual_results: list = pick_highest_ranked_result_item(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 2", expected_results, actual_results)

  def test_pick_lowest_ranked_item_works_correctly(self):
    ''' test set 1 '''
    original_search_results: list = TestDataProvider.test_data_rank_comparison_01()
    expected_results: list = TestDataProvider.test_data_rank_comparison_01_expected_lowest()
    actual_results: list = pick_lowest_ranked_result_item(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 1", expected_results, actual_results)

    ''' test set 2 '''
    original_search_results: list = TestDataProvider.test_data_rank_comparison_02()
    expected_results: list = TestDataProvider.test_data_rank_comparison_02_expected_lowest()
    actual_results: list = pick_lowest_ranked_result_item(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 2", expected_results, actual_results)

  def test_pick_one_highest_and_one_lowest_works_correctly(self):
    ''' test set 1 '''
    original_search_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_01()
    expected_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_01_expected()
    actual_results: list = pick_one_highest_and_one_lowest(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 1", expected_results, actual_results)
    
    ''' test set 2 '''
    original_search_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_02()
    expected_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_02_expected()
    actual_results: list = pick_one_highest_and_one_lowest(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 2", expected_results, actual_results)

    ''' test set 3 '''
    original_search_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_03()
    expected_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_03_expected()
    actual_results: list = pick_one_highest_and_one_lowest(original_search_results)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 3", expected_results, actual_results)

    ''' test set 4 '''
    original_search_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_04()
    expected_results: list = TestDataProvider.test_data_pick_one_highest_and_one_lowest_04_expected()
    expected_highests: list = expected_results[0]
    expected_lowests: list = expected_results[1]
    actual_results: list = pick_one_highest_and_one_lowest(original_search_results)
    self.assertEqual(2, len(actual_results))
    self.assertTrue(str(actual_results[0]) in TestUtils.get_str_expression_list_from(expected_highests))
    self.assertTrue(str(actual_results[1]) in TestUtils.get_str_expression_list_from(expected_lowests))

  def test_separate_items_by_categories_works_correctly(self):
    original_categorized_search_result_list: list = TestDataProvider.test_data_separate_items_by_categories_01()
    expected_results: dict = TestDataProvider.test_data_separate_items_by_categories_01_expected()
    actual_results: dict = separate_items_by_categories(original_categorized_search_result_list)
    # For assertion it looks through the list stored in the dictionary one by one
    for key in actual_results.keys():
      self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": comparing for the key - " + str(key), expected_results[key], actual_results[key])

  def test_separate_items_by_domains_works_correctly(self):
    original_search_results_separated_by_category: list = TestDataProvider.test_data_separate_items_by_domains_01()
    expected_results: dict = TestDataProvider.test_data_separate_items_by_domains_01_expected()
    actual_results: dict = separate_items_by_domain(original_search_results_separated_by_category)
    # For assertion it looks through the list stored in the dictionary one by one
    for key in actual_results.keys():
      self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": comparing for the key - " + str(key), expected_results[key], actual_results[key])

  def test_pick_highest_and_lowest_if_contains_multiple_items_works_correctly(self):
    ''' test set 1 : in case the given list is empty '''
    original_items: list = []
    expected_items: list = original_items
    actual_items: list = pick_highest_and_lowest_if_contains_multiple_items(original_items)
    self.assertEqual(expected_items, actual_items)

    ''' test set 2 : in case the given list contains only 1 item '''
    original_items: list = [ResultItem("Article 1", "http://www.example1.com/example", "Google")]
    expected_items: list = original_items
    actual_items: list = pick_highest_and_lowest_if_contains_multiple_items(original_items)
    self.assertEqual(expected_items, actual_items)

    ''' test set 3 : in case the given list contains 2 items which have different rank each other '''
    original_items: list = [
      ResultItem("Article 1", "http://www.example1.com/example", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo", 2)
    ]
    expected_items: list = original_items
    actual_items: list = pick_highest_and_lowest_if_contains_multiple_items(original_items)
    self.assertEqual(expected_items, actual_items)

    ''' test set 4 : in case the given list contains 2 items which have totally same rank each other '''
    original_items: list = [
      ResultItem("Article 1", "http://www.example1.com/example", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo", 1)
    ]
    expected_items: list = original_items
    actual_items: list = pick_highest_and_lowest_if_contains_multiple_items(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 4", expected_items, actual_items)

    ''' test set 5 : in case the given list contains 3 items which have different ranks each other '''
    original_items: list = [
      ResultItem("Article 1", "http://www.example1.com/example", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo", 2),
      ResultItem("Article 3", "https://example3.org", "Bing", 3)
    ]
    expected_items: list = [original_items[0], original_items[2]]
    actual_items: list = pick_highest_and_lowest_if_contains_multiple_items(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 5", expected_items, actual_items)

  def test_selection_for_general_computers_works_correctly(self):
    ''' test set 1 : in case the given dict is empty '''
    original_items: dict = {}
    actual_items: list = selection_for_general_computers(original_items)
    self.assertEqual(0, len(actual_items))

    ''' test set 2 : in case the given dict contains only one Encyclopedia '''
    original_items = {
      CATEGORIES["Encyclopedia"]: [ResultItem("Article 1", "http://en.example1.org/example", "Google", 1)]
    }
    expected_items = original_items[CATEGORIES["Encyclopedia"]]
    actual_items = selection_for_general_computers(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 2", expected_items, actual_items)

    ''' test set 3 : in case the given dict contains only one Famous News Agencies '''
    original_items = {
      CATEGORIES["Famous News Agencies"]: [ResultItem("Article 1", "http://www.example2.com/example", "Google", 5)]
    }
    expected_items = original_items[CATEGORIES["Famous News Agencies"]]
    actual_items = selection_for_general_computers(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 3", expected_items, actual_items)

    ''' test set 4 : in case the given dict contains 1 Encyclopedia and 2 for FamousNewsAgencies, OnlineNewsAgencies, and PortalsandBlogs category '''
    original_items = {
      CATEGORIES["Encyclopedia"]: [ResultItem("Article 1", "http://en.example1.org/example", "Google", 1)],
      CATEGORIES["Famous News Agencies"]: [
        ResultItem("Article 2", "http://www.example2.com/example", "Google", 5),
        ResultItem("Article 3", "https://example3.co.jp/abcde.html", "Yahoo!", 1)
      ],
      CATEGORIES["Online News Agencies"]: [
        ResultItem("Article 4", "https://www.example4.com/example", "Google", 4),
        ResultItem("Article 5", "https://example5.gov/abcde", "Yahoo!", 2)
      ],
      CATEGORIES["Portals and Blogs"]: [
        ResultItem("Article 6", "http://example6.ac.jp/dosdos/dosdos/gg.php", "Google", 8),
        ResultItem("Article 7", "https://jp.example7.net/lalalalala/lalalalala", "Yahoo!", 9)
      ]
    }
    expected_items = [
      original_items[CATEGORIES["Encyclopedia"]][0],
      original_items[CATEGORIES["Famous News Agencies"]][0], original_items[CATEGORIES["Famous News Agencies"]][1],
      original_items[CATEGORIES["Online News Agencies"]][0], original_items[CATEGORIES["Online News Agencies"]][1],
      original_items[CATEGORIES["Portals and Blogs"]][0], original_items[CATEGORIES["Portals and Blogs"]][1],
    ]
    actual_items = selection_for_general_computers(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 4", expected_items, actual_items)

    ''' test set 5 : in case the given dict contains 1 Encyclopedia and 3 for others '''
    original_items = {
      CATEGORIES["Encyclopedia"]: [
        ResultItem("Article 1", "http://en.example1.org/example", "Google", 1),
      ],
      CATEGORIES["Famous News Agencies"]: [
        ResultItem("Article 2", "http://www.example2.com/example", "Google", 5),
        ResultItem("Article 3", "https://example3.co.jp/abcde.html", "Yahoo!", 1),
        ResultItem("Article 9", "https://example9.co.jp/abcde.html", "Yahoo!", 10)
      ],
      CATEGORIES["Online News Agencies"]: [
        ResultItem("Article 4", "https://www.example4.com/example", "Google", 4),
        ResultItem("Article 5", "https://example5.gov/abcde", "Yahoo!", 2),
        ResultItem("Article 10", "https://example10.gov/abcde", "Google", 3)
      ],
      CATEGORIES["Portals and Blogs"]: [
        ResultItem("Article 6", "http://example6.ac.jp/dosdos/dosdos/gg.php", "Google", 8),
        ResultItem("Article 7", "https://jp.example7.net/lalalalala/lalalalala", "Yahoo!", 7),
        ResultItem("Article 11", "https://jp.example11.net/lalalalala/lalalalala", "Yahoo!", 6)
      ]
    }
    expected_items = [
      original_items[CATEGORIES["Encyclopedia"]][0],
      original_items[CATEGORIES["Famous News Agencies"]][1], original_items[CATEGORIES["Famous News Agencies"]][2],
      original_items[CATEGORIES["Online News Agencies"]][1], original_items[CATEGORIES["Online News Agencies"]][0],
      original_items[CATEGORIES["Portals and Blogs"]][2], original_items[CATEGORIES["Portals and Blogs"]][0],
    ]
    actual_items = selection_for_general_computers(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 5", expected_items, actual_items)

    ''' test set 6 : in case the given dict contains 0 Encyclopedia and 3 for others '''
    original_items = {
      CATEGORIES["Encyclopedia"]: [],
      CATEGORIES["Famous News Agencies"]: [
        ResultItem("Article 2", "http://www.example2.com/example", "Google", 5),
        ResultItem("Article 3", "https://example3.co.jp/abcde.html", "Yahoo!", 1),
        ResultItem("Article 9", "https://example9.co.jp/abcde.html", "Yahoo!", 10)
      ],
      CATEGORIES["Online News Agencies"]: [
        ResultItem("Article 4", "https://www.example4.com/example", "Google", 4),
        ResultItem("Article 5", "https://example5.gov/abcde", "Yahoo!", 2),
        ResultItem("Article 10", "https://example10.gov/abcde", "Google", 3)
      ],
      CATEGORIES["Portals and Blogs"]: [
        ResultItem("Article 6", "http://example6.ac.jp/dosdos/dosdos/gg.php", "Google", 8),
        ResultItem("Article 7", "https://jp.example7.net/lalalalala/lalalalala", "Yahoo!", 7),
        ResultItem("Article 11", "https://jp.example11.net/lalalalala/lalalalala", "Yahoo!", 6)
      ]
    }
    expected_items = [
      original_items[CATEGORIES["Famous News Agencies"]][1], original_items[CATEGORIES["Famous News Agencies"]][2],
      original_items[CATEGORIES["Online News Agencies"]][1], original_items[CATEGORIES["Online News Agencies"]][0],
      original_items[CATEGORIES["Portals and Blogs"]][2], original_items[CATEGORIES["Portals and Blogs"]][0],
    ]
    actual_items = selection_for_general_computers(original_items)
    self.compare_the_list_of_result_items(sys._getframe().f_code.co_name + ": test set 5", expected_items, actual_items)


  def test_pick_one_from_works_correctly(self):
    ''' test set 1 : in case the list has 3 documents '''
    original_search_results: list = [
      ResultItem("Article 1", "http://www.example1.com/example", "Google", 1),
      ResultItem("Article 2", "http://www.example2.com", "Yahoo", 2),
      ResultItem("Article 3", "https://example3.org", "Bing", 3)
    ]
    actual_result: ResultItem = pick_one_from(original_search_results)
    self.assertTrue(actual_result in original_search_results)

    ''' test set 2 : in case the list doesn't have any items '''
    original_search_results: list = []
    actual_result: ResultItem = pick_one_from(original_search_results)
    self.assertEqual(None, actual_result)

