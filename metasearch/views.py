from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from . import forms
import random
import copy
import pathlib
import urllib.request
import time
import json
from time import gmtime, strftime
from bs4 import BeautifulSoup
from metasearch.models import ResultItem
from metasearch.search_modules import yahoo_search_module
from metasearch.search_modules import google_search_module
from metasearch.search_modules import duckduckgo_search_module
from metasearch.search_modules import yandex_search_module

CATEGORIES = {
    "Encyclopedia": 1,
    "Famous News Agencies": 2,
    "Online News Agencies": 3,
    "Portals": 4,
    "Blogs": 5,
    "Portals and Blogs": 6
}

def index(request):
    '''
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))
    '''
    form = forms.SearchForm(None)
    return render(request, 'metasearch/index.html', {'form': form})

def metasearch(query: str) -> list:
    # Collect the search results retrieved from search engines
    results: list = collect_search_results_from_multiple_search_engines(query)
    # dump_log_with_timestamp("_collected_results", "ResultItems collected from several search engines", results)

    # Remove duplication from the collected search results
    duplication_free_results: list = remove_result_item_duplication(results)
    # dump_log_with_timestamp("_duplication_free_results", "ResultItems after removing duplication of URLs", duplication_free_results)

    # Remove unnecessary contents: Movie contents, detecting by its domain
    usable_results: list = remove_movie_contents_from(duplication_free_results)

    # Classify the results into categories defined as CATEGORIES and store it in an dictionary
    classified_results: dict = separate_items_by_categories(
        result_classification(usable_results)
    )
    # dump_log_with_timestamp("_classified_results", "Classification results", classified_results)

    # Select from the classified results and organize the result items to present
    selected_results: list = result_selection(classified_results)
    # dump_log_with_timestamp("_selected_results", "Selection results", selected_results)

    # Return the list of results
    return selected_results

def collect_search_results_from_multiple_search_engines(query: str) -> list:
    # Variable to store the search results from multiple search engines
    results = []

    # Get the search results retrieved from Google
    google_results = google_search_module.googleSearch(query)
    for item in google_results:
        results.append(item)
    # Get the search results retrieved from Yahoo
    yahoo_results = yahoo_search_module.yahooSearch(query)
    for item in yahoo_results:
        results.append(item)

    # Get the search results retrieved from DuckDuckGo
    duckduckgo_results = duckduckgo_search_module.duckduckgoSearch(query)
    # for item in duckduckgo_results:
    # In order to restrict the number of documents from DuckDuckGo, access by index
    # Generally they returns almost 30 items at once
    for i in range(0, 10):
        try:
            results.append(duckduckgo_results[i])
            # results.append(item)
        except IndexError:
            break
    
    # Get the search results retrieved from Yandex
    yandex_results = yandex_search_module.yandexSearch(query)
    for item in yandex_results:
        results.append(item)

    return results

def result_classification(items: list) -> list:
    # Variable to store the categorized results without duplications
    categorized_results: list = []

    # Classify the encyclopedia items
    classified: list = pick_encyclopedia_from_items(items)
    for item in classified[0]:
        categorized_results.append([CATEGORIES["Encyclopedia"], item])

    # Classify the famous news agency items
    classified = pick_famous_news_agencies_from_items(classified[1])
    for item in classified[0]:
        categorized_results.append([CATEGORIES["Famous News Agencies"], item])

    # Classify the online news agency items
    classified = pick_online_news_agencies_from_items(classified[1])
    for item in classified[0]:
        categorized_results.append([CATEGORIES["Online News Agencies"], item])

    # Classify the portal and blog items (for now it returns the given items exactly as it is)
    classified = pick_portal_and_blog_from_items(classified[1])
    for item in classified[0]:
        categorized_results.append([CATEGORIES["Portals and Blogs"], item])

    return categorized_results
        

# Remove the duplication in the list of search results
def remove_result_item_duplication(items: list) -> list:
    # Sort the list of search results by their URL
    sorted_items = sorted(items, key=lambda item: item.get_url())
    # Go through the sorted list, then move the search engine to another one and remove it if it's duplicated
    for i in range(len(sorted_items) - 1, 0, -1):
        if(sorted_items[i].get_url() == sorted_items[i - 1].get_url() or sorted_items[i].get_title() == sorted_items[i - 1].get_title()):
            # Inherit the search engine item registered on sorted_items[i]
            for engine in sorted_items[i].get_engine():
                sorted_items[i - 1].set_engine(engine)
            # Inherit the highest and lowest rank of the sorted_items[i]
            sorted_items[i - 1].set_rank(sorted_items[i].get_highest_rank())
            sorted_items[i - 1].set_rank(sorted_items[i].get_lowest_rank())
            # Pop the current item to remove duplication
            sorted_items.pop(i)
    # Return the sorted search results without duplication
    return sorted_items

# Detect the result item categorized as an "Encyclopedia"
# Returned result: [list of result items categorizedas an Encyclopedia, list of result items not categorized (the items except Encyclopedia)]
def pick_encyclopedia_from_items(items: list) -> list:
    # Prepare the list of domains which are the symbol of encyclopedia
    encyclopedia_domains: list = ["wikipedia.org"]
    # Return the search results including the above domains in its URL
    return pick_items_with_domain(items, encyclopedia_domains)

# Detect the result item categorized as an "Famous news agency"
def pick_famous_news_agencies_from_items(items: list) -> list:
    # Prepare the list of domains which are the symbol of famous news agencies
    famous_news_agencies_domains: list = [
        "xinhuanet.com",
        "reuters.com",
        "ria.ru",
        "prnewswire.com",
        "apnews.com",
        "tass.com",
        "tass.ru",
        "ansa.it",
        "yna.co.kr",
        "aljazeera.com",
        "aljazeera.net",
        "upi.com",
        "afp.com",
        "irna.ir",
        "aa.com.tr",
        "alternet.org",
        "antaranews.com",
        "newswire.ca",
        "jiji.com",
        "focustaiwan.tw",
        "cna.com.tw",
        "efe.com",
        "ipsnews.net",
        "newswise.com",
        "agi.it",
        "belta.by",
        "telam.com.ar",
        "ukrinform.net",
        "ukrinform.ua",
        "trend.az",
        "kyodonews.net",
        "kyodonews.jp",
        "bernama.com",
        "sana.sy",
        "pap.pl",
        "mediafax.ro",
        "iha.com.tr",
        "apa.az",
        "azertag.az",
        "ptinews.com",
        "kuna.net.kw",
        "dpa.com",
        "apa.at",
        "agerpres.ro",
        "unian.info",
        "interfax.com",
        "aps.dz",
        "amna.gr",
        "akipress.com",
        "centralasia.media",
        "armenpress.am",
        "uniindia.com",
        "thecanadianpress.com",
        "fides.org",
        "lusa.pt",
        "tanjug.rs",
        "anp.nl",
        "wafa.ps",
        "ians.in",
        "mti.hu",
        "bna.bh",
        "pna.gov.ph",
        "sta.si",
        "vnanet.vn",
        "tt.se",
        "petra.gov.jo",
        "aap.com.au",
        "notimex.mx",
        "avn.info.ve",
        "bnonews.com",
        "bta.bg",
        "app.com.pk",
        "bns.lt",
        "pa.media",
        "bssnews.net",
        "baptistnews.com",
        "cna.org.cy",
        "belapan.by",
        "moldpres.md",
        "belga.be",
        "tap.info.tn",
        "hina.hr",
        "mapnews.ma",
        "bns.ee",
        "pressenza.com",
        "abi.bo",
        "mia.mk",
        "akipress.com",
        "ntb.no",
        "acn.com.ve",
        "abnnewswire.net",
        "bolpress.com",
        "montsame.mn",
        "kurdpress.com",
        "stt.fi",
        "ata.gov.al",
        "catalannews.com",
        "acn.cat",
        "frifagbevegelse.no",
        "bakhtarnews.com.af",
        "pina.com.fj",
        "zumapress.com",
        "nampa.org",
        "akp.gov.kh",
        "afghanislamicpress.com",
        "unbnews.org",
        "wna-news.com",
        "latviannewsservice.lv",
        "csrwire.ca",
        "ebc.com.br",
        "ppinewsagency.com",
        "aninews.in",
        "indymedia.org"
    ]
    # Return the search results including the above domains in its URL
    return pick_items_with_domain(items, famous_news_agencies_domains)

# Detect the result item categorized as an "Online news agency"
def pick_online_news_agencies_from_items(items: list) -> list:
    # Prepare the list of domains which are the symbol of online news agency
    online_news_agencies_domains: list = [
        "nbcnews.com",
        "time.com",
        # domains listed on https://www.ohio.edu/global/international
        "allafrica.com",
        "africaonline.com.na",
        "thenewhumanitarian.org",
        "panapress.com",
        "bbc.com",
        "cnn.com",
        "buenosairesherald.com",
        "clarin.com",
        "folha.uol.com.br",
        "estadao.com.br",
        "theglobeandmail.com",
        "cbc.ca",
        "ctv.ca",
        "ctvnews.ca",
        "emol.com",
        "latercera.com",
        "eluniversal.com.mx",
        "voanews.com",
        "abcnews.go.com",
        "eluniversal.com",
        "people.com.cn",
        "taipeitimes.com",
        "indiatimes.com",
        "indianexpress.com",
        "koreatimes.co.kr",
        "nst.com.my",
        "kantipuronline.com",
        "abs-cbn.com",
        "manilatimes.net",
        "philstar.com",
        "bangkokpost.com",
        "nationmultimedia.com",
        "dw.com",
        "spiegel.de",
        "rnw.org",
        "tdg.ch",
        "sverigesradio.se",
        "hurriyetdailynews.com",
        "ahram.org.eg",
        "palestine-info.net",
        "haaretz.com",
        "abc.net.au",
        # domains listed on https://www.4imn.com/top200/
        "nytimes.com",
        "theguardian.com",
        "washingtonpost.com",
        "dailymail.co.uk",
        "kompas.com",
        "ltn.com.tw",
        "usatoday.com",
        "wsj.com",
        "telegraph.co.uk",
        "chinadaily.com.cn",
        "independent.co.uk",
        "elpais.com",
        "marca.com",
        "latimes.com",
        "nypost.com",
        "manoramaonline.com",
        "ft.com",
        "chron.com",
        "repubblica.it",
        "inquirer.net",
        "thesun.co.uk",
        "lemonde.fr",
        "mirror.co.uk",
        "nikkei.com",
        "elbalad.news",
        "express.co.uk",
        "elmundo.es",
        "as.com",
        "bild.de",
        "asahi.com",
        "lefigaro.fr",
        "kp.ru",
        "thehill.com",
        "hurriyet.com.tr",
        "chicagotribune.com",
        "udn.com",
        "welt.de",
        "infobae.com",
        "hollywoodreporter.com",
        "corriere.it",
        "thehindu.com",
        "prothomalo.com",
        "smh.com.au",
        "nydailynews.com",
        "indianexpress.com",
        "abc.es",
        "inquirer.net",
        "mathrubhumi.com",
        "metro.co.uk",
        "theglobeandmail.com",
        "scmp.com",
        "thetimes.co.uk",
        "chosun.com",
        "hindustantimes.com",
        "clarin.com",
        "dawn.com",
        "milliyet.com.tr",
        "lun.com",
        "zeit.de",
        "donga.com",
        "thestar.com",
        "denverpost.com",
        "lanacion.com.ar",
        "axs.com",
        "hpenews.com",
        "sueddeutsche.de",
        "idnes.cz",
        "csmonitor.com",
        "bostonglobe.com",
        "japantimes.co.jp",
        "rg.ru",
        "standard.co.uk",
        "mk.ru",
        "washingtontimes.com",
        "mercurynews.com",
        "aksam.com.tr",
        "seattletimes.com",
        "ce.cn",
        "irishtimes.com",
        "gazzetta.it",
        "startribune.com",
        "leparisien.fr",
        "lavanguardia.com",
        "chinatimes.com",
        "dallasnews.com",
        "azcentral.com",
        "theage.com.au",
        "faz.net",
        "yomiuri.co.jp",
        "abola.pt",
        "sozcu.com.tr",
        "20minutos.es",
        "jpost.com",
        "iz.ru",
        "appledaily.com",
        "oregonlive.com",
        "miamiherald.com",
        "business-standard.com",
        "nation.africa",
        "baltimoresun.com",
        "aif.ru",
        "livemint.com",
        "sabah.com.tr",
        "straitstimes.com",
        "lequipe.fr",
        "ajc.com",
        "mainichi.jp",
        "liberation.fr",
        "yenisafak.com",
        "elcomercio.com",
        "independent.ie",
        "andhrajyothy.com",
        "theaustralian.com.au",
        "nzherald.co.nz",
        "freep.com",
        "aftonbladet.se",
        "theonion.com",
        "mundodeportivo.com",
        "gazeta.pl",
        "newsday.com",
        "standardmedia.co.ke",
        "lastampa.it",
        "punchng.com",
        "nationalpost.com",
        "cleveland.com",
        "kommersant.ru",
        "post-gazette.com",
        "alwafd.news",
        "nouvelobs.com",
        "ynet.co.il",
        "tempo.co",
        "eluniversal.com.mx",
        "estadao.com.br",
        "dailystar.co.uk",
        "vg.no",
        "sacbee.com",
        "20minutes.fr",
        "derstandard.at",
        "gulfnews.com",
        "tagesspiegel.de",
        "inquirer.com",
        "thestar.com.my",
        "sakshi.com",
        "elcomercio.pe",
        "thenews.com.pk",
        "scotsman.com",
        "eltiempo.com",
        "ilsole24ore.com",
        "thenationalnews.com",
        "iol.co.za",
        "sun-sentinel.com",
        "vanguardngr.com",
        "sport.es",
        "handelsblatt.com",
        "prensalibre.com",
        "orlandosentinel.com",
        "jsonline.com",
        "stltoday.com",
        "ocregister.com",
        "tampabay.com",
        "lesechos.fr",
        "sfchronicle.com",
        "nikkansports.com",
        "ouest-france.fr",
        "eenadu.net",
        "sapo.pt",
        "bostonherald.com",
        "heraldsun.com.au",
        "vedomosti.ru",
        "bhaskar.com",
        "detroitnews.com",
        "sapo.pt",
        "investors.com",
        "sport-express.ru",
        "avaz.ba",
        "eleconomista.es",
        "theadvocate.com",
        "manchestereveningnews.co.uk",
        "expressen.se",
        "thejakartapost.com",
        "sltrib.com",
        "elperiodico.com",
        "kansascity.com",
        "diariolibre.com",
        "financialexpress.com",
        "dailytelegraph.com.au",
        "ycwb.com",
        "expansion.com",
        "reviewjournal.com",
        "pravda.ru",
        "20min.ch",
        "afr.com",
        "seattlepi.com",
        "dagbladet.no",
        "observer.com",
        "nzz.ch",
        "eluniverso.com",
        "vancouversun.com",
        "khaleejtimes.com",
        "hankyung.com"
    ]
    # Return the search results including the above domains in its URL
    return pick_items_with_domain(items, online_news_agencies_domains)

# Detect the result item categorized as an "Portal"
def pick_portal_from_items(items: list) -> list:
    return [[], items]

# Detect the result items categorized as an "Blog"
def pick_blog_from_items(items: list) -> list:
    # Just returns all the items for now
    return [items, []]

# Detect the result items categorized as an "Portal" or "Blog"
def pick_portal_and_blog_from_items(items: list) -> list:
    # Just returns all the items for now
    return [items, []]

def remove_movie_contents_from(items: list) -> list:
    # Prepare the list of domains which are providing movie contents should not be included in the search result
    domains_to_be_removed = [
        "youtube.com"
    ]
    # If item in the list given as an argument includes the domains to be removed as its URL, simply remove it from the list and return it.
    for i in range(len(items), 0, -1):
        if items[i - 1].get_domain() in domains_to_be_removed:
            items.pop(i - 1)
    return items

# Detect the result item having the particular domain in its URL 
# Arguments: 
# - list of search result items
# - list of domains to specify in the result items' URL
# Return the result: list of the following 2 list
# - list of result items haveing the domains specified in the given domain list in its URL
# - list of result items which doesn't have the specified domains
def pick_items_with_domain(items: list, domains: list) -> list:
    items_having_the_specific_domain = []
    for i in range(len(items) - 1, -1, -1):
        for domain in domains:
            if(items[i].get_domain() == domain):
                items_having_the_specific_domain.append(items.pop(i))
                break
    return [items_having_the_specific_domain, items]

# Pick the highest-ranked item from the given set of search result items
def pick_highest_ranked_result_item(items: list) -> list:
    # Check what is the highest rank in the given result item list
    highest_rank: int = ResultItem.LOWESTRANK
    for item in items:
        try:
            items_rank: int = item.get_highest_rank()
            if items_rank < highest_rank:
                highest_rank = items_rank
            if items_rank <= ResultItem.HIGHESTRANK:
                break
        except AttributeError:
            print("[ERROR LOG] In pick_highest_ranked_result_item, while checking the highest rank in the given result items, AttributeError detected.")
            continue

    # Pick the result items which have the highest rank
    highest_items: list = []
    for item in items:
        try:
            if item.get_highest_rank() == highest_rank:
                highest_items.append(item)
        except AttributeError:
            print("[ERROR LOG] In pick_highest_ranked_result_item, while searching the highest ranked item in the given result items, AttributeError detected. BTW, the highest rank is " + str(highest_rank))

    return highest_items

# Pick the lowest-ranked item from the given set of search result items
def pick_lowest_ranked_result_item(items: list) -> list:
    # Check what is the lowest rank in the given result item list
    lowest_rank: int = ResultItem.HIGHESTRANK
    for item in items:
        try:
            items_rank: int = item.get_lowest_rank()
            if items_rank > lowest_rank:
                lowest_rank = items_rank
            if items_rank >= ResultItem.LOWESTRANK:
                break
        except AttributeError:
            print("[ERROR LOG] In pick_lowest_ranked_result_item, while checking the lowest rank in the given result items, AttributeError detected.")
            continue

    # Pick the result items which have the highest rank
    lowest_items: list = []
    for item in items:
        try:
            if item.get_highest_rank() == lowest_rank:
                lowest_items.append(item)
        except AttributeError:
            print("[ERROR LOG] In pick_lowest_ranked_result_item, while checking the lowest rank in the given result items, AttributeError detected. BTW, the lowest rank is " + str(lowest_rank))
            continue

    return lowest_items

# Separate the result items in the given list by their categories
def separate_items_by_categories(items: list) -> list:
    '''
    Parameters
    ----------
    items : list
        List of tuples including the category symbol defined as CATEGORIES and the ResultItem object
        in other words, list of tuples (category: int, ResultItem)
        ex.
        items = [
            (CATEGORIES["Encyclopedia"], ResultItem1),
            (CATEGORIES["Encyclopedia"], ResultItem2),
            ...
            (CATEGORIES["Famous News Agencies"], ResultItem5),
            ...
        ]

    Returns
    ----------
    separated_items : dict
        Dictionary with the information of categorization
        ex.
        separated_items = {
            CATEGORIES["Encyclopedia"]: [ResultItem1, ResultItem2, ResultItem3], 
            CATEGORIES["Famous News Agencies"]: [ResultItem4, ResultItem5], 
            ...
        }
    '''

    # Prepare a dictionary to store the separated items
    separated_items = {}
    for category in CATEGORIES.values():
        separated_items[category] = []
    # Put the items in the given list into the dictionary
    for item in items:
        separated_items[item[0]].append(item[1])

    return separated_items

# Select result items by pre-defined criteria
def result_selection(classified_result_items: dict) -> list:
    '''
    Parameters
    ----------
    classified_result_items : dict
        Dictionary of search result lists which are already classified
        ex.
        separated_items = {
            CATEGORIES["Encyclopedia"]: [ResultItem1, ResultItem2, ResultItem3], 
            CATEGORIES["Famous News Agencies"]: [ResultItem4, ResultItem5], 
            ...
        }
    
    Returns
    ----------
    selected_result_items : list
        List of result items which are selected according to pre-defined selection criteria
        ex.
        selected_result_items = [
            ResultItem1, ResultItem2, ResultItem3, ...
        ]
    '''

    # Later, implement a if-else structure to checkout the selection criteria between PC and smartphone
    # for now, directly returns the result selected by the criteria for PC
    return selection_for_general_computers(classified_result_items)

# Selection process for general computers
def selection_for_general_computers(classified_result_items: dict) -> list:
    '''
    Parameters
    ----------
    classified_result_items : dict
        Dictionary of search result lists which are already classified
        ex.
        separated_items = {
            CATEGORIES["Encyclopedia"]: [ResultItem1, ResultItem2, ResultItem3], 
            CATEGORIES["Famous News Agencies"]: [ResultItem4, ResultItem5], 
            ...
        }

    Returns
    ----------
    selected_result_items : list
        List of selected items according to pre-defined criteria
        The size of this list is expected to be less than 10
        ex.
        selected_result_items = [
            ResultItem1, ResultItem2, ResultItem3, ...
        ]
    '''
    # Pick only highest and lowest-ranked item from a duplicated domain of its URL
    classified_result_item_separated_by_domain: dict = {}
    classified_result_item_only_highest_and_lowest_for_a_domain: dict = {}
    for category in classified_result_items.keys():
        # Put the dictionary grouped by their domain into the mother dictionary
        classified_result_item_separated_by_domain[category]: dict = separate_items_by_domain(classified_result_items[category])
        if category == CATEGORIES["Encyclopedia"]:
            # For the items categorized as Encyclopedia, pick only 1 item randomly and remove all others
            picked_encyclopedia: ResultItem = pick_one_from(classified_result_items[CATEGORIES["Encyclopedia"]])
            if picked_encyclopedia != None:
                classified_result_item_only_highest_and_lowest_for_a_domain[CATEGORIES["Encyclopedia"]] = [picked_encyclopedia]
            else:
                classified_result_item_only_highest_and_lowest_for_a_domain[CATEGORIES["Encyclopedia"]] = []
        else:
            # For all categories except Encyclopedia
            classified_result_item_only_highest_and_lowest_for_a_domain[category]: list = []
            for results_with_particular_url_domain in classified_result_item_separated_by_domain[category].values():
                # For all list grouped by results' URL domain
                # make the list to contain only the highest and lowest-ranked ones if it contains multiple items
                # or keep it as it is if contains less than 3 items
                for item in pick_highest_and_lowest_if_contains_multiple_items(results_with_particular_url_domain):
                    classified_result_item_only_highest_and_lowest_for_a_domain[category].append(item)
        
    # Pick only highest and lowest-ranked item from a category
    selected_result_items: list = []
    for category in classified_result_items.keys():
        items_list: list = classified_result_item_only_highest_and_lowest_for_a_domain[category]
        for item in pick_highest_and_lowest_if_contains_multiple_items(items_list):
            if item != None:
                selected_result_items.append(item)

    return selected_result_items
    

# Returns a list of highest and lowest-ranked item if the given list is including multiple items
def pick_highest_and_lowest_if_contains_multiple_items(items: list) -> list:
    '''
    Parameters
    ----------
    items : list
        List of ResultItem which have the same domain of URL

    Returns
    ----------
    highest_and_lowest : list
        List of 2 items (highest-ranked and lowest-ranked) if the given list contains multiple items
        or return the given list directly if the size of the list is less than or equal to 2
    '''
    if len(items) > 2:
        # if the given list contains multiple items
        return pick_one_highest_and_one_lowest(items)
    else:
        # if the size of the given list is less than 2, means only one item or it's just a empty list
        return items


# Collect the search result items which have the same domain
def separate_items_by_domain(items: list) -> dict:
    separated_items: dict = {}
    for item in items:
        domain: str = item.get_domain()
        if domain not in separated_items.keys():
            separated_items[domain] = [item]
        else:
            separated_items[domain].append(item)

    return separated_items

# Pick highest and lowest-ranked item from the given result items
def pick_one_highest_and_one_lowest(items: list) -> list:
    '''
    Parameters
    ----------
    items : list
        List of ResultItem objects

    Returns
    ----------
    results : list
        List of the highest and lowest-ranked item in the given result items
        If multiple items having the same rank returned, choose one randomly
    '''
    # If the original results list is empty, return an empty list
    if len(items) == 0:
        return []
    # Make a deepcopy of the given result item list to avoid make changes to the original items
    results: list = copy.deepcopy(items)
    # Get the highest-ranked items, put them into a list and pick one randomly if it contains multiple items
    highests: list = pick_highest_ranked_result_item(results)
    highest: ResultItem = pick_one_from(highests)
    # Remove the item picked as highest, to avoid duplication between highest and lowest item
    results.remove(highest)
    # If the current size of the results list is empty, return the highest
    if len(results) == 0:
        return [highest]
    # Get the lowest-ranked items, put them into a list and pick one randomly if it contains multiple items
    lowests: list = pick_lowest_ranked_result_item(results)
    lowest: ResultItem = pick_one_from(lowests)
    # Make the results list empty and append highest and lowest to return it back
    results = []
    results.append(highest)
    results.append(lowest)
    return results

def pick_one_from(items: list) -> ResultItem:
    if len(items) == 0:
        return None
    else:
        return random.choice(items)

def get_timestamp() -> str:
    return strftime("%Y%m%d%H%M%S", gmtime())

def dump_log_with_timestamp(f_name: str, message: str, items: set):
    f_name = get_timestamp() + f_name
    dump_log(f_name, message, items)

def dump_log(f_name: str, message: str, items): 
    log_file = pathlib.Path('./metasearch/log_files/'+f_name+'.txt')
    with log_file.open(mode='w') as f:
        f.write(message)
        dump_log_to_file(items, f)

def dump_log_to_file(item, f):
    if isinstance(item, list):
        for an_item in item:
            dump_log_to_file(an_item, f)
    elif isinstance(item, dict):
        for an_item in item.keys():
            f.write("\n<<" + str(an_item) + ">>")
            dump_log_to_file(item[an_item], f)
    else:
        f.write('\n'+str(item))

def stringify_result_items_list_for_logging(results: list) -> str:
    result_txt: str = ""
    for item in results:
        result_txt = result_txt + str(item) + "\n"
    return result_txt

def stringify_result_items_dict_for_logging(results: dict) -> str:
    result_txt: str = ""
    for key in results:
        result_txt = result_txt + "<<< " +  str(key) + " >>>\n"
        result_txt = result_txt + stringify_result_items_list_for_logging(results[key])
        result_txt = result_txt + "\n"
    return result_txt

def push_into_json(*args) -> str:
    '''
    Parameters
    ----------
    *args : tuple of (str, str)
        tuple of couples of json string attribute name and its content in string
        ex. (("title1", "content1"), ("title2", "content2"), ("title3", "content3"))

    Returns
    ----------
    json_str : str
        contents stored in json string
        ex. "
                {
                    "title1": "content1",
                    "title2": "content2",
                    "title3": "content3"
                }
            "
    '''
    content: dict = {}
    for arg in args:
        content[arg[0]] = arg[1]
    json_str: str = json.dumps(content)
    return json_str

def search(request):
    search_query = request.GET.get('query')
    results = metasearch(search_query)

    context = {
        'query': search_query,
        'search_results': results,
        'form': forms.SearchForm({'query': search_query})
    }
    
    return render(request, 'metasearch/result.html', context)

