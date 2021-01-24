import sys
import json
from urllib import request
from urllib import parse
from bs4 import BeautifulSoup
from metasearch.models import ResultItem

def retrieve_result_page(query: str) -> str:
    '''
    Parameters
    ----------
    query : str
        search query string to be sent to DuckDuckGo
        can contain space character and no need to concatenate with '+'
        ex. "hello world"

    Returns
    ----------
    result_page : str
        obtained HTML result page in string
        ex. "<!DOCTYPE html PUBLIC "-//W3C...</body></html>"
    '''
    # Put the query into the form data (post parameter) and it should be encoded binary
    # Look at "Data" section on the page https://docs.python.org/3.7/howto/urllib2.html
    data = parse.urlencode({
        "q": query,
    }).encode('ascii')

    # To access their result without using web browser just use html version of their page
    url = "https://html.duckduckgo.com/html/"

    # Method should be POST to retrieve their result page correctly
    request_to_throw = request.Request(url, data, method="POST")

    # In case it fails to retrieve the result, return an empty string
    result_page = ""

    with request.urlopen(request_to_throw) as response:
        result_page = response.read().decode('utf-8')

    return result_page

def push_into_ResultItems(page: str) -> list:
    '''
    Parameters
    ----------
    page : str
        DuckDuckGo result HTML page which contains the information about the search results
        ex. "<!DOCTYPE html PUBLIC "-//W3C...</body></html>"
    
    Returns
    ----------
    results : list
        The list of search results summarized in the ResultItem objects
        ex. [ResultItem1, ResultItem2, ResultItem3, ...]
    '''
    # Retrieve the necessary results using BeautifulSoup
    soup: BeautifulSoup = BeautifulSoup(page, "html.parser")
    search_results: list = pick_result_item_parts(soup)
    results: list = []
    rank_count: int = 1
    for item in search_results:
        try:
            title = pick_title_from(item)
            url: str = pick_url_from(item)
            snippet: str = pick_snippet_from(item)
            rank: int = rank_count
            rank_count = rank_count + 1
            result: ResultItem = ResultItem(title, url, "DuckDuckGo")
            result.set_abstract(snippet)
            result.set_rank(rank)
            results.append(result)
        except AttributeError:
            continue
    return results

def pick_snippet_from(item: BeautifulSoup) -> str:
    '''
    Parameters
    ----------
    item : BeautifulSoup
        BeautifulSoup object of the part of result item section
        ex. 
            BeautifulSoup of "
                <div id="r1-0" class="result results_links_deep highlight_d result--url-above-snippet" data-domain="en.wikipedia.org" data-hostname="en.wikipedia.org" data-nir="1">
                    <div class="result__body links_main links_deep">
                        <h2 class="result__title">
                        <a class="result__a" rel="noopener" href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict">
                            <b>Nagorno-Karabakh</b> <b>conflict</b> - Wikipedia
                        </a>
                        <a rel="noopener" class="result__check" href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict">
                            <span class="result__check__tt">Your browser indicates if you've visited this link</span>
                        </a>
                        </h2>
                        <div class="result__extras js-result-extras">
                            <div class="result__extras__url">
                                <span class="result__icon ">
                                    <a href="https://duckduckgo.com/?q=nagorno%2Dkarabakh%20conflict+site:en.wikipedia.org&amp;t=h_" title="Search domain en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" class="js-result-extras-site_search">
                                        <img data-src="/assets/icons/favicons/wikipedia.white.2x.png" height="16" width="16" title="Search domain en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" class="result__icon__img js-lazyload-icons" src="./sample_page_01_files/wikipedia.white.2x.png">
                                    </a>
                                </span>
                                <a href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" rel="noopener" class="result__url js-result-extras-url">
                                    <span class="result__url__domain">https://en.wikipedia.org</span>
                                    <span class="result__url__full">/wiki/Nagorno-Karabakh_conflict</span>
                                </a>
                            </div>
                        </div>
                        <div class="result__snippet js-result-snippet">The <b>Nagorno-Karabakh</b> <b>conflict</b> is an ethnic and territorial <b>conflict</b> between Armenia and Azerbaijan over the disputed region of <b>Nagorno-Karabakh</b>, inhabited mostly by ethnic Armenians, and seven surrounding districts, inhabited mostly by Azerbaijanis until their expulsion during the <b>Nagorno-Karabakh</b> War, which are de facto controlled by the self-declared Republic of Artsakh, but are ...</div>
                    </div>
                </div>
            "
            BeautifulSoup of "
                <div class="result results_links results_links_deep web-result ">
                    <div class="links_main links_deep result__body">
                    <!-- This is the visible part -->
                    <h2 class="result__title"> 
                        <a rel="nofollow" class="result__a" href="https://ssl.japan-drone.com/en_la/">
                            <b>Japan</b> <b>Drone</b> 2020
                        </a> 
                    </h2>
                    <div class="result__extras">
                        <div class="result__extras__url"> 
                            <span class="result__icon">
                                <a rel="nofollow" href="https://ssl.japan-drone.com/en_la/">
                                    <img class="result__icon__img" width="16" height="16" alt=""
                                    src="//external-content.duckduckgo.com/ip3/ssl.japan-drone.com.ico" name="i15" />
                                </a>
                            </span> 
                            <a class="result__url" href="https://ssl.japan-drone.com/en_la/">
                                ssl.japan-drone.com/en_la/
                            </a> 
                        </div>
                    </div> 
                    <a class="result__snippet" href="https://ssl.japan-drone.com/en_la/">
                        &quot;<b>Japan&#x27;s</b> Largest <b>Drone</b> Business Event: <b>Japan</b> <b>Drone</b> 2020 will be held at Makuhari Messe on September 29 and 30.&quot; -We are preparing for it by taking all the necessary safety and security...
                    </a>
                    <div style="clear: both"></div>
                    </div>
                </div>
            "

    Returns
    ----------
    snippet : str
        snippet retrieved from the given part of HTML code wrapped by the BeautifulSoup object
        ex. "The Nagorno-Karabakh conflict is an ethnic and territorial conflict between Armenia and Azerbaijan over the disputed region of Nagorno-Karabakh, inhabited mostly by ethnic Armenians, and seven surrounding districts, inhabited mostly by Azerbaijanis until their expulsion during the Nagorno-Karabakh War, which are de facto controlled by the self-declared Republic of Artsakh, but are ..."
    '''
    # snippet_part: BeautifulSoup = item.find("div", attrs={"result__snippet"})
    snippet_part: BeautifulSoup = item.find_all(class_="result__snippet")
    snippet: str = snippet_part[0].get_text()
    return snippet

def pick_url_from(item: BeautifulSoup) -> str:
    '''
    Parameters
    ----------
    item : BeautifulSoup
        BeautifulSoup object of the part of result item section
        ex. 
            BeautifulSoup of "
                <div id="r1-0" class="result results_links_deep highlight_d result--url-above-snippet" data-domain="en.wikipedia.org" data-hostname="en.wikipedia.org" data-nir="1">
                    <div class="result__body links_main links_deep">
                        <h2 class="result__title">
                        <a class="result__a" rel="noopener" href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict">
                            <b>Nagorno-Karabakh</b> <b>conflict</b> - Wikipedia
                        </a>
                        <a rel="noopener" class="result__check" href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict">
                            <span class="result__check__tt">Your browser indicates if you've visited this link</span>
                        </a>
                        </h2>
                        <div class="result__extras js-result-extras">
                            <div class="result__extras__url">
                                <span class="result__icon ">
                                    <a href="https://duckduckgo.com/?q=nagorno%2Dkarabakh%20conflict+site:en.wikipedia.org&amp;t=h_" title="Search domain en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" class="js-result-extras-site_search">
                                        <img data-src="/assets/icons/favicons/wikipedia.white.2x.png" height="16" width="16" title="Search domain en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" class="result__icon__img js-lazyload-icons" src="./sample_page_01_files/wikipedia.white.2x.png">
                                    </a>
                                </span>
                                <a href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" rel="noopener" class="result__url js-result-extras-url">
                                    <span class="result__url__domain">https://en.wikipedia.org</span>
                                    <span class="result__url__full">/wiki/Nagorno-Karabakh_conflict</span>
                                </a>
                            </div>
                        </div>
                        <div class="result__snippet js-result-snippet">The <b>Nagorno-Karabakh</b> <b>conflict</b> is an ethnic and territorial <b>conflict</b> between Armenia and Azerbaijan over the disputed region of <b>Nagorno-Karabakh</b>, inhabited mostly by ethnic Armenians, and seven surrounding districts, inhabited mostly by Azerbaijanis until their expulsion during the <b>Nagorno-Karabakh</b> War, which are de facto controlled by the self-declared Republic of Artsakh, but are ...</div>
                    </div>
                </div>
            "
            BeautifulSoup of "
                <div class="result results_links results_links_deep web-result ">
                    <div class="links_main links_deep result__body">
                    <!-- This is the visible part -->
                    <h2 class="result__title"> 
                        <a rel="nofollow" class="result__a" href="https://ssl.japan-drone.com/en_la/">
                            <b>Japan</b> <b>Drone</b> 2020
                        </a> 
                    </h2>
                    <div class="result__extras">
                        <div class="result__extras__url"> <span class="result__icon">
                            
                            <a rel="nofollow" href="https://ssl.japan-drone.com/en_la/">
                                <img class="result__icon__img" width="16" height="16" alt=""
                                src="//external-content.duckduckgo.com/ip3/ssl.japan-drone.com.ico" name="i15" />
                            </a>
                        
                        </span> 
                        <a class="result__url" href="https://ssl.japan-drone.com/en_la/">
                            ssl.japan-drone.com/en_la/
                        </a> 
                    </div>
                    </div> <a class="result__snippet" href="https://ssl.japan-drone.com/en_la/">&quot;<b>Japan&#x27;s</b> Largest <b>Drone</b> Business Event: <b>Japan</b> <b>Drone</b> 2020 will be held at Makuhari Messe on September 29 and 30.&quot; -We are preparing for it by taking all the necessary safety and security...</a>
                    <div style="clear: both"></div>
                    </div>
                </div>
            "
    
    Returns
    ----------
    url_text : str
        URL retrieved from the give part of HTML code wrapped by the BeautifulSoup object
        ex. "https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict"
    '''
    url: str = item.find("a", attrs={"result__url"})['href']
    return url

def pick_title_from(item: BeautifulSoup) -> str:
    '''
    Parameters
    ----------
    item : BeautifulSoup
        BeautifulSoup object of the part of result item section
        ex. 
            BeautifulSoup of "
                <div id="r1-0" class="result results_links_deep highlight_d result--url-above-snippet" data-domain="en.wikipedia.org" data-hostname="en.wikipedia.org" data-nir="1">
                    <div class="result__body links_main links_deep">
                    <h2 class="result__title">
                        <a class="result__a" rel="noopener" href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict">
                            <b>Nagorno-Karabakh</b> <b>conflict</b> - Wikipedia
                        </a>
                        <a rel="noopener" class="result__check" href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict">
                            <span class="result__check__tt">Your browser indicates if you've visited this link</span>
                        </a>
                    </h2>
                    <div class="result__extras js-result-extras">
                            <div class="result__extras__url"><span class="result__icon "><a href="https://duckduckgo.com/?q=nagorno%2Dkarabakh%20conflict+site:en.wikipedia.org&amp;t=h_" title="Search domain en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" class="js-result-extras-site_search"><img data-src="/assets/icons/favicons/wikipedia.white.2x.png" height="16" width="16" title="Search domain en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" class="result__icon__img js-lazyload-icons" src="./sample_page_01_files/wikipedia.white.2x.png"></a></span><a href="https://en.wikipedia.org/wiki/Nagorno-Karabakh_conflict" rel="noopener" class="result__url js-result-extras-url"><span class="result__url__domain">https://en.wikipedia.org</span><span class="result__url__full">/wiki/Nagorno-Karabakh_conflict</span></a></div>
                    </div>
                    <div class="result__snippet js-result-snippet">The <b>Nagorno-Karabakh</b> <b>conflict</b> is an ethnic and territorial <b>conflict</b> between Armenia and Azerbaijan over the disputed region of <b>Nagorno-Karabakh</b>, inhabited mostly by ethnic Armenians, and seven surrounding districts, inhabited mostly by Azerbaijanis until their expulsion during the <b>Nagorno-Karabakh</b> War, which are de facto controlled by the self-declared Republic of Artsakh, but are ...</div>
                    </div>
                </div>
            "
            BeautifulSoup of "
                <div class="result results_links results_links_deep web-result ">
                    <div class="links_main links_deep result__body">
                    <!-- This is the visible part -->
                    <h2 class="result__title"> 
                        <a rel="nofollow" class="result__a" href="https://ssl.japan-drone.com/en_la/">
                            <b>Japan</b> <b>Drone</b> 2020
                        </a> 
                    </h2>
                    <div class="result__extras">
                        <div class="result__extras__url"> <span class="result__icon">
                            
                            <a rel="nofollow" href="https://ssl.japan-drone.com/en_la/">
                                <img class="result__icon__img" width="16" height="16" alt=""
                                src="//external-content.duckduckgo.com/ip3/ssl.japan-drone.com.ico" name="i15" />
                            </a>
                        
                        </span> <a class="result__url" href="https://ssl.japan-drone.com/en_la/">
                        ssl.japan-drone.com/en_la/
                        </a> </div>
                    </div> <a class="result__snippet" href="https://ssl.japan-drone.com/en_la/">&quot;<b>Japan&#x27;s</b> Largest <b>Drone</b> Business Event: <b>Japan</b> <b>Drone</b> 2020 will be held at Makuhari Messe on September 29 and 30.&quot; -We are preparing for it by taking all the necessary safety and security...</a>
                    <div style="clear: both"></div>
                    </div>
                </div>
            "

    Returns
    ----------
    title : str
        Title retrieved from the given part of HTML code wrapped by the BeautifulSoup object
        ex. "2020 Nagorno-Karabakh conflict - Wikipedia"
    '''
    title_part: BeautifulSoup = item.find("h2", attrs={"result__title"})
    title_part = title_part.find("a", attrs={"result__a"})
    title: str = title_part.get_text()
    return title

def pick_result_item_parts(page: BeautifulSoup) -> list:
    '''
    Parameters
    ----------
    page : BeautifulSoup
        The BeautifulSoup object created from the retrieved web page
        ex. BeautifulSoup created from "<!DOCTYPE html PUBLIC "-//W3C...</body></html>"

    Returns
    ----------
    result_item_parts : list
        List of BeautifulSoup objects created from the search result items in the retrieved web page
        Practically, these are picked from the given BeautifulSoup object created by the source page
        ex. []
    '''
    result_item_parts: list = page.find_all("div", attrs={"result", "result_links", "result_links_deep", "web-result"})
    return result_item_parts

def duckduckgoSearch(query: str):
    # Get the DuckDuckGo search result page for the query
    page: str = retrieve_result_page(query)
    # Prepare a list for returning the search results
    results: list = push_into_ResultItems(page)
    # Return the result list
    return results

# Main Function
if __name__ == "__main__":
    # Prepare query variable
    query = sys.argv[1]
    # Append multiple query words with "+"
    for arg in sys.argv[2:]:
        query = query + "+" + arg
    # Experiment the search function
    result = duckduckgoSearch(query)
    # Print the result list to the command line
    for item in result:
        print(item)
        print(item.abstract)
