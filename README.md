# MosaicSearch

This system is an implementation of the metasearch engine mechanism with the [filtering schema presented by Nemoto et al.](http://www.thinkmind.org/index.php?view=article&articleid=icds_2020_3_30_10023) based on the [logic advocated by Klyuev](https://ieeexplore.ieee.org/abstract/document/8701334?casa_token=HAg6hTmd4pAAAAAA:INfqoDS-R4hApVCSaCm1Pcp89YyMM5x3JM5iVUTxgVkGzQU8ZP0W1SQe_hIJuhTXtby0EDoaeEo9).

You can use this application as an approach to reduce the effect of filters imposed by commercial search engines.
It retrieves the search results presented by multiple search engines (Google, Yahoo!, DuckDuckGo, and Yandex), pick the results in a transparant way, and present them to you. 
For the details, please look at the references above.
Summary of the implementation of this system and the evaluation might be published as an article in early 2021.

## Requirements before running the application
  Before running the application on your own server or local environment, there are two requirements you need to prepare.
  1. Type the following command right under the MosaicSearchForPublication/ directory.
  ~~~
  python DjangoMetasearch/get_random_secret_key.py > DjangoMetasearch/local_settings.py
  ~~~

  2. Acquire API keys for Google Search API and Yandex.XML. Your obtained keys should be stored in the files: google_api_info.py and yandex_api_info.py under metasearch/search_modules/api_keys.

## How does it work?
  The main workflow of this system consists of 4 layers: a collection of search results, classification of them, selection of them, and the presentation of them to the users.
  For the details, please look at the abovementioned articles.
  

## Limits related to the number of the throwable queries to each search engine
### Google
  **10,000 queries** per day. Look at the "Summary of Programmable Search Engine Offerings" section on [this page](https://developers.google.com/custom-search/docs/overview).
  This search system is utilizing **Custom Search JSON API** officially provided by Google

### Yahoo!
  Theoritically, **no limits**. Search Results from this search engine is retrieved by scraping.

### DuckDuckGo
  Theoritically, **no limits**. Search Results from this search engine is retrieved by scraping.

### Yandex
  **10,000 queries** per day. Look at the "Limits on the number of results sent." section on [this page](https://yandex.com/dev/xml/doc/dg/concepts/restrictions.html/). 
  The registered account owning the API access key this system uses, has completed the registration of the "Telephone number" written in the above documennt, so the restrictions for "Telephone number confirmed" is applied to this API key.
