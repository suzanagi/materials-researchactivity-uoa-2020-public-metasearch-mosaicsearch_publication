import os
import datetime
import urllib
import xml.etree.ElementTree

from time import sleep
from metasearch.models import ResultItem
from metasearch.search_modules.api_keys.yandex_api_info import user_name, api_key

YANDEX_USER_NAME_TO_USE = user_name
YANDEX_API_KEY = api_key
LANG = {
    "English": "en"
}
SORTBY = {
    "relevancy": "rlv",
    "time": "tm",
}
FILTER = {
    "None": "none",
    "Family Filter": "strict",
    "Moderate": "moderate"
}

def build_url(query: str, lang: str, sortby: str, filter: str, maxpassages: int, result_num: int) -> str:
    '''
    For the detailed structure of the request URL to Yandex search engine, access
    https://yandex.com/dev/xml/doc/dg/concepts/get-request.html/
    '''
    # Header part of the URL
    url: str = "https://yandex.com/search/xml?"
    # Add user attribute to the URL
    url = url + "user=" + YANDEX_USER_NAME_TO_USE + "&"
    # Add key attribute to the URL
    url = url + "key=" + YANDEX_API_KEY + "&"
    # Add query attribute to the URL
    url = url + "query=" + query + "&"
    # Add language attribute to the URL
    url = url + "l10n=" + lang + "&"
    # Add sorting attribute to the URL
    url = url + "sortby=" + sortby + "&"
    # Add filter attribute to the URL
    url = url + "filter=" + filter + "&"
    # Add maxpassages attribute to the URL
    url = url + "maxpassages=" + str(maxpassages) + "&"
    # Add groupby (number of result items in the page)  attribute to the URL
    url = url + "groupby=" + "attr%3D%22%22.mode%3Dflat.groups-on-page%3D" + str(result_num) + ".docs-in-group%3D1"
    return url

def request_get(url: str) -> str:
    '''
    This function throw a request to the given URL and return the result of reading the response
    '''
    req = urllib.request.Request(url)
    res = urllib.request.urlopen(req)
    data = res.read()
    return data.decode('utf-8')

def analyze_xml(xml_data: str):
    return xml.etree.ElementTree.fromstring(xml_data)

def push_into_ResultItems(tree_root, num_results: int) -> list:
    # List of ResultItem to return
    results: list = []
    doc_count: int = 1
    for doc in tree_root.iter('doc'):
        try:
            passage: str = ''.join(doc.iter('passages').__next__().itertext())
        except StopIteration:
            try:
                passage: str = ''.join(doc.iter('headline').__next__().itertext())
            except StopIteration:
                passage: str = ""
        passage = passage.replace('<passage>', '')
        passage = passage.replace('</passage>', '<br/>')
        item: ResultItem = create_ResultItem(
            ''.join(doc.iter('title').__next__().itertext()).replace('\n', '').replace('  ', '').replace('&', '&amp;'),
            doc.iter('url').__next__().text.replace('\n', ''),
            doc.iter('modtime').__next__().text,
            replace_and_from(passage),
            doc[8][1].text,
            doc_count
        )
        doc_count = doc_count + 1
        results.append(item)

    return results

def create_ResultItem(title: str, url: str, modtime: str, passages: str, lang: str, rank: int) -> ResultItem:
    item: ResultItem = ResultItem(title, url, "Yandex")
    item.set_rank(rank)
    item.set_abstract(passages)
    return item

def replace_and_from(item: str) -> str:
    return item.replace('&', '&amp;')

def yandexSearch(query: str) -> list:
    # number of search results to return
    num_results = 10
    # adjust the query if it contains space in the string
    query = query.replace(' ', '+')
    # construct the url to make a request
    url_to_access: str = build_url(
        query,
        LANG["English"],
        SORTBY["relevancy"],
        FILTER["None"],
        5,
        num_results
    )
    # get the xml response from the API in string
    xml_data: str = replace_and_from(request_get(url_to_access))
    # build the xml tree by analyzing its structure
    xml_tree_root = analyze_xml(xml_data)
    # summarize the result as ResultItem and build the list of results
    response: list = push_into_ResultItems(xml_tree_root, num_results)

    return response
        
        
if __name__ == '__main__':

    target_keyword = '2021+economic+forecast'

    results = yandexSearch(target_keyword)

    for result in results:
        print(result)

