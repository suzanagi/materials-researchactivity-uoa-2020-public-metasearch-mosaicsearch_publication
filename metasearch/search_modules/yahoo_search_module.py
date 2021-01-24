import requests
import sys
from bs4 import BeautifulSoup
from metasearch.models import ResultItem

def retrieve_result_page(query: str):
    return requests.get('https://search.yahoo.com/search?p='+query)

def yahooSearch(query: str):
    # Get the Yahoo search result page for the query
    page = retrieve_result_page(query)
    # Prepare a list for returning the search results
    result = list()
    # Check the result page encoding to use it in BeautifulSoup composition
    encoding = page.encoding
    # Analyse the result page using BeautifulSoup
    soup = BeautifulSoup(page.content, "html.parser", from_encoding = encoding)
    # Obtain topics and abstract element by the BeautifulSoup function
    # Put the results in the list to be returned
    rank = 1
    result_items = soup.select("div.dd.algo.algo-sr.relsrch")
    for item in result_items:
        # Retrieve title and URL
        title_section = item.find("h3", attrs={"title"})
        title_section = title_section.find("a", attrs={"ac-algo", "fz-l", "ac-21th", "lh-24"})
        title: str = title_section.text
        url: str = title_section.attrs['href']
        snippet: str = ""
        # Retrieve snippets
        snippet_section = item.find("div", attrs={"compText", "aAbs"})
        if snippet_section == None:
            snippet_section = item.find("ul", attrs={"pl-15"})
            if snippet_section == None:
                snippet = ""
            else:
                snippet = snippet_section.text
        else:
            snippet_section = snippet_section.find("p", attrs={"fz-ms", "lh-1_43x"})
            if snippet_section == None:
                snippet = ""
            else:
                snippet: str = snippet_section.text
        r_item: ResultItem = ResultItem(title, url, "Yahoo!")
        r_item.set_rank(rank)
        r_item.set_abstract(snippet)
        rank = rank + 1
        result.append(r_item)

    # Return the result list
    return result

# Main Function
if __name__ == "__main__":
    # Prepare query variable
    query = sys.argv[1]
    # Append multiple query words with "+"
    for arg in sys.argv[2:]:
        query = query + "+" + arg
    # Experiment the search function
    result = yahooSearch(query)
    # Print the result list to the command line
    for item in result:
        print(item)
        print(item.get_abstract())
        
