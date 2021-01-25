import os
import datetime
import json

from time import sleep
from googleapiclient.discovery import build
from metasearch.models import ResultItem
from metasearch.search_modules.api_keys.google_api_info import api_key, api_id

GOOGLE_API_KEY = api_key
CUSTOM_SEARCH_ENGINE_ID = api_id

DATA_DIR = 'data'

def makeDir(path):
    if not os.path.isdir(path):
        os.mkdir(path)

def googleSearch(query):
    # build the request to the custom search api
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    # number of pages to get the search results
    page_limit = 1
    # get from the first search result
    start_index = 1
    # number of search results to return
    num_results = 10
    # variable to save the result retrieved through the API
    result = []
    # variable to save the response
    response = []

    # look through the results page by page
    # for n_page in range(0, page_limit):
    for n_page in range(page_limit):
        # print("before try \n")
        try:
            sleep(1)
            result.append(service.cse().list(
                # Input the query
                q=query,
                # The programmable search engine ID to use for this request
                cx=CUSTOM_SEARCH_ENGINE_ID,
                # Restricts the search to documents written in a particular language (e.g., lr=lang_ja)
                # lr='lang_ja',
                # Number of search results to return
                num=num_results,
                # The index of the first result to return
                start=start_index
            ).execute())
            if(n_page != 0):
                start_index = response[n_page].get("queries").get("nextPage")[0].get("startIndex")

        except Exception as e:
            print(e)
            break

    for i in range(0, num_results, 1):
        json_item = result[0]['items'][i]
        r_item = ResultItem(json_item['title'], json_item['link'], "Google")
        r_item.set_rank(i+1)
        r_item.set_abstract(json_item['snippet'])
        response.append(r_item)
    return response
        
        
if __name__ == '__main__':

    target_keyword = 'trump twitter'

    results = googleSearch(target_keyword)

    for result in results:
        print(result)

