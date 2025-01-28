from abc import ABC, abstractmethod
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rusta_crawler.spiders.rusta_spider import NewEcomSpider
from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings as settings
# from rusta_crawler.spiders.rusta_spider import settings as settings
# from scrapy.settings import Settings
from scrapy.spiders import Spider
import argparse
import datetime
import logging


# Step 1: Define the Spider interface
class Spider(ABC):
    @abstractmethod
    def create(self):
        pass

# Step 2: Create concrete classes
class NewSiteSpider(Spider):
    def create(self, *args, **kwargs) -> NewEcomSpider:
        return NewEcomSpider
    
# Step 3: Define the SpiderFactory class
class SpiderFactory(ABC):
    @abstractmethod
    def create_spider(self,  *args, **kwargs) -> Spider:
        pass

# Step 4: Implement concrete factories
class NewEcomSpiderFactory(SpiderFactory):

    def create_spider(self, *args, **kwargs) -> Spider:
        return NewSiteSpider()


# Client code
class SpiderClient():

    def __init__(self):
        home = os.path.expanduser("~")

        log_dir = os.path.join(home, "rusta_logs")

        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directory: {e}")
            SystemExit(1)

        log_file = os.path.join(log_dir, f"spider factory {datetime.date.today().strftime('%Y-%m-%d')}.log")

        try:
            self.log = logging.getLogger(__name__)
            fh = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            fh.setFormatter(formatter)
            fh.setLevel(logging.INFO)
            self.log.addHandler(fh) 

        except Exception as e:
            print(f"Error setting up logging: {e}")

        self.log.info("SPIDER FACTORY - Initialized SpiderClient")
        
    def create_spider(self, factory: SpiderFactory, *args, **kwargs) -> list:
        spider_factory = factory.create_spider(*args, **kwargs)
        process = CrawlerProcess({
            'ITEM_PIPELINES': {'__main__.ResultPipeline': 1},
            'LOG_LEVEL': 'INFO',  # Set log level to INFO to see more details
        })

        if kwargs.get('ctr'):
            ctr = kwargs.get('ctr')
            for c in ctr:
                sp = spider_factory.create()
                kwargs['ctr'] = c
                process.crawl(sp, **kwargs)
        else:
            sp = spider_factory.create()
            process.crawl(sp, **kwargs)
        
        process.start()
    def run_new_ecom_site_spider(self, scrape_type, ctr=None, debug=None):
        
        if ctr:
            ctr = [c.upper() for c in ctr]
        kwargs = { "ctr": ctr, "scrape": scrape_type, "debug": debug}
        new_site_factory = NewEcomSpiderFactory()  
        results = self.create_spider(new_site_factory, **kwargs)
        self.log.info(f"SPIDER FACTORY - Results: {results}")
        return results

    def list_of_strings(arg):
        return arg.split(',')

    def run_spider(self, parser):
        args = parser.parse_args()
        if args.scrape in ['week', 'rolling']:
            self.log.info("SPIDER FACTORY - Creating spider")
            results = self.run_new_ecom_site_spider(scrape_type=args.scrape)
            self.log.info(f"SPIDER FACTORY - Final Results: {results}")
        elif args.scrape == 'active' and args.ctr:
            for ctr in args.ctr:
                if ctr.upper() not in ['SE', 'NO', 'FI', 'DE']:
                    parser.error(f"Invalid country code: {ctr}")
            self.log.info(f"SPIDER FACTORY - Running spider for {ctr}")
            results = self.run_new_ecom_site_spider(ctr=args.ctr, scrape_type=args.scrape, debug=args.debug)
            self.log.info(f"SPIDER FACTORY - Final Results: {results}")
        else:
            parser.error("Please provide required arguments")
    

def list_of_strings(arg):
    return arg.split(',')


if __name__ == "__main__":
    spider_client = SpiderClient()
    parser = argparse.ArgumentParser(description='Run Scrapy spiders with common input.')
    parser.add_argument('--scrape', type=str, help='week rolling active', required=True)
    parser.add_argument('--ctr', type=list_of_strings, help='Countries. SE NO DE FI. For multiple countries seperate with "," ', required=False)
    parser.add_argument('--debug', type=str, required=False)
    spider_client.run_spider(parser)



