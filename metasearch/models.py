import re
from django.db import models
from tld import get_tld

class ResultItem:
    HIGHESTRANK = 1
    LOWESTRANK = 100
    DEFAULTRANK = LOWESTRANK
    SEARCHENGINES = ["Google", "Yahoo!", "Bing", "Yandex", "DuckDuckGo"]

    def __init__(self, title: str, url: str, engine: str, rank: int=DEFAULTRANK):
        # The title of the page
        self.set_title(title)
        # The URL of this item
        self.url: str = ""
        self.set_url(url)
        # The list of source search engine this item is retrieved from
        self.engine: list = []
        self.set_engine(engine)
        # The place this search result item is displayed on the search result page
        self.highest_rank: int = ResultItem.DEFAULTRANK
        self.lowest_rank: int = ResultItem.DEFAULTRANK
        self.set_rank(rank)

    def set_title(self, title: str):
        self.title = title.replace('\n', '')

    def get_title(self) -> str:
        return self.title

    def set_url(self, url: str) -> bool:
        # if(re.fullmatch(r'https?://(([a-zA-Z0-9])+(\.))+([a-zA-Z]{2,})+/?', url) == None):
        if(re.fullmatch(r"https?://[\w!?/+\-_~:;.,*&@#$%=()'[\]]+", url) == None):
            # When the format of the URL is wrong
            print("The format of the given URL if wrong: ", url)
            return False
        else:
            # When the given URL matches the correct format of the URL
            # Cut '/' at the end of URL if the URL is referencing a html file
            if(re.fullmatch(r"https?://[\w!?/+\-_~:;.,*&@#$%=()'[\]]+.html/", url) == None):
                self.url = url
            else:
                self.url = url.strip('/')
            return True
    
    def get_url(self) -> str:
        return self.url

    def set_engine(self, engine: str) -> bool:
        if(engine in ResultItem.SEARCHENGINES):
            # When the list of search engines contains the given name of search engine brand
            if(engine not in self.engine):
                # When the given name of search engine is not yet registered as the source search engine of this item
                self.engine.append(engine)
                return True
            else:
                # When the given name of search engine is already in the list of its source search engine
                print("This search engine is already in the engine list: ", engine)
                return False
        else:
            # When any unknown name of search engine is given
            print("Undefined search engine detected: ", engine)
            return False

    def get_engine(self):
        return self.engine

    def set_rank(self, rank: int):
        try:
            # Validate if the given rank is in the expected range
            if (rank < ResultItem.HIGHESTRANK or ResultItem.LOWESTRANK < rank):
                raise KeyError

            if (self.highest_rank == ResultItem.DEFAULTRANK and self.lowest_rank == ResultItem.DEFAULTRANK):
                self.highest_rank = rank
                self.lowest_rank = rank
            elif (self.highest_rank > rank):
                self.highest_rank = rank
            elif (self.lowest_rank < rank):
                self.lowest_rank = rank
        except KeyError as e:
            print("Illegal rank given: ", rank)

    def get_highest_rank(self) -> int:
        return self.highest_rank

    def get_lowest_rank(self) -> int:
        return self.lowest_rank

    def set_abstract(self, abstract):
        self.abstract = abstract
        
    def get_abstract(self):
        return self.abstract

    def get_domain(self):
        # domain of its URL
        t_domain = get_tld(self.url, as_object=True)
        domain = str(t_domain.domain) + '.' + str(t_domain)
        return domain
    
    def __str__(self):
        engine_str = ""
        for engine in self.engine:
            engine_str = engine_str + ", " + engine
        return (
            "[Title] " + self.title 
            + " [URL] " + self.url 
            + " [Engine] " + engine_str 
            + " [HRank] " + str(self.highest_rank) 
            + " [LRank] " + str(self.lowest_rank) 
        )
