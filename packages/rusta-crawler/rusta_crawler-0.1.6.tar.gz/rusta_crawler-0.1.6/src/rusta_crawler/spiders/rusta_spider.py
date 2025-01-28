import os
import sys
import json
from decimal import Decimal

import scrapy.core.engine
import scrapy.exceptions
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)



import scrapy.crawler
from scrapy.spiders import Spider as ScrapySpider
from scrapy.http import Request
from requests.exceptions import RequestException
from scrapy import signals
from typing import Optional
from scrapy.utils.project import get_project_settings
from files import constants as const

from snowflake.connector.errors import DatabaseError as snowflake_errors
import datetime
from tools import logger
from typing import Optional
import scrapy.utils.misc
import scrapy.core.scraper

import time
from rusta_tools.snowflake_connection import Snowflake
from re import error as re_error



# Stub function to suppress warning. Used for PyInstaller
def warn_on_generator_with_return_value_stub(spider, callable):
    pass

scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub


    

class NewEcomSpider(ScrapySpider):
    name = "NewEcomSpider"

    def __init__(self, *args, **kwargs):
        ScrapySpider.__init__(self, *args, **kwargs)
        import logging
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        logging.getLogger('scrapy.core.engine').setLevel(logging.ERROR)
        logging.getLogger('scrapy.downloadermiddlewares.redirect').setLevel(logging.ERROR)
        logging.getLogger('snowflake.connector').setLevel(logging.ERROR)
        logging.getLogger('pymongo').setLevel(logging.INFO)

        logger.log_info("Spider - NewEcomSpider initialized")

        self.snow_db_handler = Snowflake()
        
        self.start_time = time.time()  # Start the timer
        self.result = []
        self.scrape_articles = []  # List of articles to scrape
        self.scrape_article_table = ""
        self.running_ctr = ""
        self.result_table_name = ""
        self.debug = kwargs.get('debug')
        self.failed = False

        self.ctr = kwargs.get('ctr')
        scrape = kwargs.get('scrape')
        self.scrape = ""
        self.camp_to_check = ""
        self.result_table_name = ""
        if scrape == const.WEEK:
            self.camp_sql = const.CAMPAIGN_OF_THE_WEEK
            self.scrape = const.WEEK
            self.result_table_name = const.TBL_CAMPAIGN_SCRAPE_RESULT
            self.scrape_article_table = const.TBL_CAMPAIGN_SCRAPE_ARTICLES
        elif scrape == const.ROLLING:
            self.camp_sql = const.ROLLING_CAMPAIGNS
            self.scrape = const.ROLLING
            self.result_table_name = const.TBL_CAMPAIGN_SCRAPE_RESULT
            self.scrape_article_table = const.TBL_CAMPAIGN_SCRAPE_ARTICLES
        elif scrape == const.ACTIVE:
            self.scrape = const.ACTIVE
            if self.debug == None:
                self.result_table_name = const.TBL_ACTIVE_SCRAPE_RESULT
                self.scrape_article_table = const.TBL_ACTIVE_SCRAPE_DATA
            else:
                self.result_table_name = const.TBL_ACTIVE_SCRAPE_RESULT_TEMP
                self.scrape_article_table = const.TBL_ACTIVE_SCRAPE_DATA
                                
        logger.log_info(f"Spider - Scrape type: {self.scrape}, Country: {self.ctr}")
        self.headers =  {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Cookie': 'js_enabled=true; is_cookie_active=true;'
        }

    def get_country_query(self, country):
        sql = ""
        active_web_ctr = ""
        active_ctr = ""
        if country == const.SE:
            sql = const.SE_SQL
            active_web_ctr = const.ACTIVE_WEB_SE
            active_ctr = const.ACTIVE_SE
        elif country == const.NO:
            sql = const.NO_SQL
            active_web_ctr = const.ACTIVE_WEB_NO
            active_ctr = const.ACTIVE_NO
        elif country == const.FI:
            sql = const.FI_SQL
            active_web_ctr = const.ACTIVE_WEB_FI
            active_ctr = const.ACTIVE_FI
        elif country == const.DE:
            sql = const.DE_SQL
            active_web_ctr = const.ACTIVE_WEB_DE
            active_ctr = const.ACTIVE_DE
        return active_ctr, active_web_ctr, sql

    def remove_file_if_exists(self, filepath):
        result = True
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
                logger.log_info(f"File {filepath} removed successfully.")
                logger.log_info(f"File {filepath} does not exist.")
            result = False
        except Exception as e:
            logger.log_info(f"Error removing file {filepath}: {e}")
            result = False
        return result
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NewEcomSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.engine_stopped, signal=signals.engine_stopped)
        # crawler.settings = get_project_settings()
        # crawler.settings.set("REQUEST_FINGERPRINTER_IMPLEMENTATION", "2.7")
        # crawler.settings.set("DOWNLOAD_DELAY", "2")
        crawler.settings.set("COOKIES_ENABLED", True)  # Enable cookies
        crawler.settings.set("ITEM_PIPELINES", {"rusta_crawler.pipelines.RustaCrawlerPipeline": 300})

        return spider
    
    def engine_stopped(self):
        if self.crawler.stats.get_value('log_count/ERROR'):
            logger.log_error("Spider - Core engine errors occurred during the crawl.")
            
    def terminate(self):
        #termination logic here
        logger.log_info("Spider - Terminating the spider functions.")
        
        home = os.path.expanduser("~")
        log_dir = os.path.join(home, "rusta_script_data")
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directory: {e}")
            SystemExit(1)

        if self.scrape == const.ACTIVE:
            log_file = os.path.join(log_dir, f"{self.ctr}.failed")
        elif self.scrape == const.WEEK:
            log_file = os.path.join(log_dir, f"week.failed")
        elif self.scrape == const.ROLLING:
            log_file = os.path.join(log_dir, f"rolling.failed")
        self.remove_file_if_exists(log_file)
        with open(log_file, 'w') as file:
            file.write("failed")
        self.failed = True
        from scrapy.crawler import CrawlerProcess
        self.crawler_process = CrawlerProcess(get_project_settings())
        self.crawler_process.stop()
   

    def spider_opened(self, spider):
        logger.log_info("==========================NewEcomSpider opened==========================")
    
    def spider_closed(self, spider):
        if self.result:
            self.save_data_to_db(self.result, self.result_table_name)
            request_count = self.crawler.stats.get_value('downloader/request_count')
            response_count = self.crawler.stats.get_value('downloader/response_count')
            error_count = self.crawler.stats.get_value('log_count/ERROR')
            status_200 = self.crawler.stats.get_value('downloader/response_status_count/200')
            status_302 = self.crawler.stats.get_value('downloader/response_status_count/302')
            status_404 = self.crawler.stats.get_value('downloader/response_status_count/404')
            status_500 = self.crawler.stats.get_value('downloader/response_status_count/500')
            status_301 = self.crawler.stats.get_value('downloader/response_status_count/301')

            logger.log_info(f"""Sent {request_count} 
                            requests and received {response_count} responses.
                            Status 200: {status_200}, 302: {status_302}, 404: {status_404}, 500: {status_500},
                            301: {status_301}. Errors: {error_count}""")
            elapsed_time = time.time() - self.start_time  # Calculate the elapsed time
            logger.log_info(f"Spider - Spider ran for {elapsed_time:.2f} seconds")


        if not self.failed:
            home = home = os.path.expanduser("~")

            log_dir = os.path.join(home, "rusta_script_data")
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                print(f"Error creating log directory: {e}")
                SystemExit(1)
            if self.scrape == const.ACTIVE:
                if status_500:
                    log_file = os.path.join(log_dir, f"{self.ctr}.failed")
                else:
                    log_file = os.path.join(log_dir, f"{self.ctr}.success")
            elif self.scrape == const.WEEK:
                log_file = os.path.join(log_dir, f"week.success")
            elif self.scrape == const.ROLLING:
                log_file = os.path.join(log_dir, f"rolling.success")
            
            self.remove_file_if_exists(log_file)
            with open(log_file, 'w') as file:
                file.write("success")

    def extract_article_data(self, data):
        data.pop(const.DOWNLOAD_TIMEOUT, None)
        data.pop(const.DOWNLOAD_SLOT, None)
        data.pop(const.DOWNLOAD_LATENCY, None)
        data.pop(const.DEPTH, None)
        data.pop("handle_httpstatus_list") if "handle_httpstatus_list" in data else None
        data.pop("redirect_ttl") if "redirect_ttl" in data else None
        data.pop("redirect_urls") if "redirect_urls" in data else None
        data.pop("redirect_reasons") if "redirect_reasons" in data else None
        data.pop("redirect_times") if "redirect_times" in data else None
        data.pop("retry_times") if "retry_times" in data else None
        return data
    def load_query(self, query_to_read):
        try:
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one directory level
            parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
            query_dir = os.path.join(parent_dir, 'sql')
            query_file = os.path.join(os.path.join(query_dir, query_to_read))
            query = ""
            with open(query_file, 'r') as file:
                query = file.read()
            return query
        except Exception as e:
            raise Exception(f"DB - An error occurred while loading the query: {e}")

    # def process_all_active_and_save(self, articles, active_ctr, active_web_ctr, country):


    def process_all_active_articles(self, articles, active_ctr, active_web_ctr, country):
        article_data = []
        for  article in articles:

            article_id = article.get(const.ARTICLE_ID)
            start_url = const.COMPANY_URLS_NEW_SITE.get( int(article.get(const.COMPANY))) + article_id

            article_data.append({const.START_URL: start_url,
                                        const.ARTICLE_ID: article.get(const.ARTICLE_ID),  
                                        const.ARTICLE_NAME: article.get(const.ARTICLE_NAME), 
                                        const.COMPANY : article.get(const.COMPANY), 
                                        const.ACTIVE_CTR: (True if article.get(active_ctr) == "Y" else False),
                                        const.ACTIVE_WEB: (True if article.get(active_web_ctr)=="Yes" else False),
                                        const.PRODUCT_COORDINATOR: article.get(const.PRODUCT_COORDINATOR),
                                        const.LIFE_CYCLE_STATUS: article.get(const.LIFE_CYCLE_STATUS),
                                        const.DATE: datetime.datetime.now().strftime("%Y-%m-%d"),
                                        const.RETAIL_PRICE: article.get(const.RETAIL_PRICE),
                                        const.ACTUAL_PRICE: article.get(const.ACTUAL_PRICE),
                                        const.DEPARTMENT: article.get(const.DEPARTMENT),
                                        const.SALES_AREA: article.get(const.SALES_AREA) 
                                        
                                        })
        return article_data
    
    def process_and_save_campaign_data(self, articles):        
        article_data = []   
        for campaign in articles:
            if campaign.get(const.ACTIVE_WEB) == const.YES:
                article_id = campaign.get(const.ARTICLE_ID)
                start_url = const.COMPANY_URLS_NEW_SITE.get( int(campaign.get(const.COMPANY))) + article_id
                article_data.append({const.START_URL: start_url,
                                            const.CAMPAIGN_ID: campaign.get(const.CAMPAIGN_ID), const.CAMPAIGN_DESCRIPTION: campaign.get(const.CAMPAIGN_DESCRIPTION),
                                            const.SALES_START:campaign.get(const.SALES_START), const.SALES_END: campaign.get(const.SALES_END),
                                            const.DEPARTMENT: campaign.get(const.DEPARTMENT), const.SALESGROUP: campaign.get(const.SALESGROUP),
                                            const.PROMOTION_DESC: campaign.get(const.PROMOTION_DESC), const.ARTICLE_ID: campaign.get(const.ARTICLE_ID),
                                            const.ARTICLE_NAME: str(campaign.get(const.ITEM_NAME)), const.COMPANY:  campaign.get(const.COMPANY_NAME),
                                            const.LIFE_CYCLE_STATUS: campaign.get(const.LIFE_CYCLE_STATUS),
                                            const.PROMOTION_TYPE: campaign.get(const.PROMOTION_TYPE),
                                            const.ACTIVE_WEB: campaign.get(const.ACTIVE_WEB),const.COMPANY: campaign.get(const.COMPANY),
                                            const.PRODUCT_COORDINATOR: campaign.get(const.PRODUCT_COORDINATOR), const.CAMPAIGN_COORDINATOR: campaign.get(const.CAMPAIGN_COORDINATOR),
                                            const.DATE: datetime.datetime.now().strftime("%Y-%m-%d"),
                                            const.CAMPAIGN_PERIOD: self.scrape
                                            })
        try:
            import snowflake.connector.errors as snowflake_errors
            self.delete_same_day_data(table=self.scrape_article_table, dwh="RUSTA_CRAWLER_DWH", scrape_type=self.scrape)
            self.save_data_to_db(article_data, self.scrape_article_table)
            logger.log_info(f"Spider - Campaign data to be scraped saved to DB. Total of {len(article_data)} articles.")
            return article_data
        except snowflake_errors.Error as e:
            logger.log_error(f"Spider - Error saving data to DB. Terminating execution: {e}")
            self.terminate()
        
    def errback_http(self, failure):
            self.logger.error(repr(failure))
            if failure.check(HttpError):
                response = failure.value.response
                self.logger.error("HttpError on %s", response.url)
            elif failure.check(DNSLookupError):
                request = failure.request
                self.logger.error("DNSLookupError on %s", request.url)
            elif failure.check(TimeoutError, TCPTimedOutError):
                request = failure.request
                self.logger.error("TimeoutError on %s", request.url)

    def start_requests(self):
            if self.scrape == const.ACTIVE:
                self.parsed = 0
                active_ctr, active_web_ctr, query_file = self.get_country_query(self.ctr)
                sql_query = self.load_query(query_file)
                articles = self.load_scrap_data(sql_query)
                article_data = self.process_all_active_articles(articles, active_ctr, active_web_ctr, self.ctr)
                try:
                    import snowflake.connector.errors as snowflake_errors
                    self.delete_same_day_data(table=self.scrape_article_table, company=const.COMPANY_NAME_TO_ID[self.ctr], dwh="RUSTA_CRAWLER_DWH")
                    self.save_data_to_db(article_data, self.scrape_article_table)
                    logger.log_info(f"Spider - Active article data to be scraped saved to DB. Total of {len(article_data)} articles for {self.ctr}.")

                except snowflake_errors.Error as e:
                    logger.log_error(f"Spider - Error saving data to DB. Terminating execution: {e}")
                    self.terminate()
                if article_data:
                    self.delete_same_day_data(table=self.result_table_name, dwh="RUSTA_CRAWLER_DWH",
                                                                company=const.COMPANY_NAME_TO_ID.get(self.ctr))
                    for article in article_data:
                        article |= {'handle_httpstatus_list': [302]}
                        try:
                            yield Request(url=article.get(const.START_URL), callback=self.parse_search_page, meta=article, dont_filter=True,
                                    errback=self.errback_http)
                        except RequestException as e:
                            logger.log_error(f"Spider - Error sending request to {article.get(const.START_URL)}: {e}. Article ID: {article.get(const.ARTICLE_ID)}")
                        except scrapy.core as e:
                            logger.log_error(f"Spider - Error sending request to {article.get(const.START_URL)}: {e}. Article ID: {article.get(const.ARTICLE_ID)}")
            elif self.scrape in (const.WEEK, const.ROLLING):
                query_file = const.CAMPAIGN_DATA_TO_LOAD.get(self.scrape)
                sql_query = self.load_query(query_file)
                articles = self.load_scrap_data(sql_query)
                article_data = self.process_and_save_campaign_data(articles)

                self.delete_same_day_data(table=self.result_table_name, dwh="RUSTA_CRAWLER_DWH", scrape_type=self.scrape)
                
                for article in article_data:
                    article |= {'handle_httpstatus_list': [302]}
                    url = article.get(const.START_URL)
                    try:
                        yield Request(url=url, callback=self.parse_search_page, meta=article, dont_filter=True, errback=self.errback_http)
                    except RequestException as e:
                        logger.log_error(f"Spider - Error sending request to {url}: {e}. Article ID: {article.get(const.ARTICLE_ID)}")
            else:
                logger.log_error("Spider - Scrape type not defined. Terminating execution.")
                self.terminate()

    def load_scrap_data(self, query):
        import snowflake.connector.errors as snowflake_errors   
        try:
            article_data = self.snow_db_handler.fetch_article_data(query=query, dwh="CAMPAIGN_VERIFICATION")
            return article_data
        
        except snowflake_errors as e:
            logger.log_error(f"{e}")
            logger.log_info("Spider - Terminating execution.")
            self.terminate()
        except Exception as e:
            logger.log_error(e)
            logger.log_info("Spider - Terminating execution.")
            self.terminate()

    def save_data_to_db(self, data, table):
        import snowflake.connector.errors as snowflake_errors
        try:
            if data:
                self.snow_db_handler.save_data_to_db(data, table)
                logger.log_info(f"Spider - Data saved to DB. Total of {len(data)} rows. For company: {self.ctr}")
            else:
                logger.log_warning("Spider - No data to save.")
                self.terminate()
        except snowflake_errors.DatabaseError as e:
            logger.log_error(f"{e}")
            logger.log_info("Spider - Terminating execution.")
            self.terminate()

    def delete_same_day_data(self, table, dwh, company=None, scrape_type=None):
        import snowflake.connector.errors as snowflake_errors
        try:
            self.snow_db_handler.delete_same_day_data(table_name=table, dwh=dwh, company=company, scrape_type=scrape_type)
        except snowflake_errors.DatabaseError as e:
            logger.log_error(f"Spider - Error deleting data from DB: {e}")    

    def parse_search_page(self, response):
        
        if self.scrape in (const.WEEK, const.ROLLING):
            result = spiderCampaignDict().data 
        
        else:
            result = spiderDict().data

        data = response.meta
        article_found = False
        search_url = ""
        releated = False
        pdp_result = None

        if response.status == 302:
            redirect_url = ""
            if response.headers.get('Location').decode('utf-8').find("rusta.com") == -1:
                redirect_url = f"https://rusta.com{response.headers.get('Location').decode('utf-8')}"  
                try:
                    yield Request(url=redirect_url, callback=self.parse_search_page, meta=response.meta, headers=self.headers, dont_filter=True, errback=self.errback_http)
                except RequestException as e:
                    self.log.error(f"Error redirecting to {redirect_url}: {e}. Article ID: {data.get(const.ARTICLE_ID)}") 
            else:
                logger.log_info(f"Article shouldn't be active. Article ID: {data.get(const.ARTICLE_ID)}")
                data.update({const.ARTICLE_NAME: "Not active"})
            
        elif response.status == 500:
            logger.log_error(f"Spider - Server error. Url: {response.url}")

        elif response.status == 200:
            found_releated = response.xpath("//*[@id='container']//main/div[1]/div[2]/div[1]/div[2]/section/h1").get()
            if found_releated:
                # logger.log_info(f"Spider - Article found with releated products. Url: {response.url}")
                article_found = True
                data |= {"RELATED": True}
                search_url = response.request.url
                releated_article_url = None

                import re
                pattern = re.compile(r'"products":.*?\[.*?"facets"', re.DOTALL)
                prod =  re.search(pattern, response.text)
                
                json_str = prod.group(0)
                # Remove all new lines from json_str
                json_str = re.sub(r'\s+', '', json_str)
                json_str = re.sub(r',\"facets\"', '', json_str)
                if json_str.startswith("'") and json_str.endswith("'"):
                    json_str = json_str[1:-1]

                json_str = '{' + json_str +'}'

                try:
                    products = json.loads(json_str)
                   
                    # logger.log_info(f"Spider - Extracted JSON: for article {response.request.url}")
                    list_of_products = products["products"]
                    for product in list_of_products:
                        if product.get("code") == data.get(const.ARTICLE_ID):
                            releated_article_url = "https://www.rusta.com" + product.get("url")
                            search_url = releated_article_url
                            break
                        else:
                            logger.log_info(f"Spider - Main article was not found for {data.get(const.COMPANY)}: {data.get(const.ARTICLE_ID)}")

                except json.JSONDecodeError as e:
                         logger.log.error(f"Spider - Error decoding JSON: {e}")
                         logger.log.info("Spider - Releated wont be parsed")
                except Exception as e:
                         logger.log.error(f"Spider - Error getting pdp url: {e}")
                         logger.log.info("Spider - Releated wont be parsed")
                if releated_article_url:
                    yield Request(url=releated_article_url, callback=self.parse_search_page, meta=response.meta, headers=self.headers, dont_filter=True, errback=self.errback_http)

            elif response.xpath("//meta[@property='product:retailer_item_id']/@content").get():
                article_found = True
                pdp_result = self.parse_pdp(response)
                search_url = response.url 
            else:
                #Article not found
                article_found = False
                search_url = response.url
                
            if data.get(const.RELATED):
                releated = data.get(const.RELATED)
           

            result.update({const.ARTICLE_FOUND: article_found, const.SEARCH_URL: search_url, 
                           const.ACTIVE_WEB : data.get(const.ACTIVE_WEB), const.RELATED : releated, 
                            const.COMPANY: data.get(const.COMPANY), const.ARTICLE_ID: data.get(const.ARTICLE_ID),
                            const.ARTICLE_NAME: data.get(const.ARTICLE_NAME),
                            const.DATE: datetime.datetime.now().strftime("%Y-%m-%d"),
                            const.PRODUCT_COORDINATOR: data.get(const.PRODUCT_COORDINATOR), 
                            const.LIFE_CYCLE_STATUS: data.get(const.LIFE_CYCLE_STATUS)})
            
            if self.scrape in (const.WEEK, const.ROLLING):
                result.update({const.CAMPAIGN_COORDINATOR: data.get(const.CAMPAIGN_COORDINATOR),
                               const.CAMPAIGN_ID: data.get(const.CAMPAIGN_ID), const.CAMPAIGN_DESCRIPTION: data.get(const.CAMPAIGN_DESCRIPTION),
                               const.SALES_START: data.get(const.SALES_START), const.SALES_END: data.get(const.SALES_END),
                               const.DEPARTMENT: data.get(const.DEPARTMENT), const.SALESGROUP: data.get(const.SALESGROUP),
                               const.PROMOTION_DESC: data.get(const.PROMOTION_DESC), const.CAMPAIGN_PERIOD: self.scrape,
                               const.PROMOTION_TYPE: data.get(const.PROMOTION_TYPE)})
                
            if self.scrape == const.ACTIVE:
                result.update({const.ACTUAL_PRICE: data.get(const.ACTUAL_PRICE), const.RETAIL_PRICE: data.get(const.RETAIL_PRICE),
                               const.ACTIVE_CTR: data.get(const.ACTIVE_CTR), const.DEPARTMENT: data.get(const.DEPARTMENT),
                               const.SALES_AREA: data.get(const.SALES_AREA)})

            if pdp_result:
                result.update(pdp_result)

                # if pdp_result.get(const.PROMOTION_TYPE_WEB) != "Multi" and  (pdp_result.get(const.VISIBLE_PRICE) != data.get(const.ACTUAL_PRICE)):
                #         result.update({const.PRICE_CORRECT: const.FALSE})
                self.result.append(result)
            elif not releated:
                self.result.append(result)

    def save_result(self, result, url:Optional[str]=None):
        if result:
            self.save_data_to_db(result, self.result_table_name)
        else:
            logger.log_warning(f"Spider - Error parsing the search page. {url}")

    def parse_pdp(self, response):
        import re
        result = {}
        data = response.meta
   


        response.xpath("//section//path[@fill='url(#club-rusta-a)']").get()
        save = response.xpath("//*[@id='container']//main/div[2]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]").get()
        discount = response.xpath("//*[@id='container']//main/div[2]/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]").get()
        show_original_price = response.xpath("//*[@id='container']//main/div[2]/div[2]/div[1]/div[2]/div/div[2]/section/div[2]/span/span[2]").get()
        visible_price = response.xpath("//*[@id='container']//main/div[2]/div[2]/div[1]/div[2]/div/div[2]/section/div[2]/span/span[1]").get()
        multi_combo_package = response.xpath("//*[@id='container']//main/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/section/div[2]").get()
        multi_combo_package = response.xpath("//*[@id='container']//main/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/section/div[2]").get()

        price = None
        original_price = ""
        save_amount = ""
        discount_type = ""
        promotion_type = ""
        promotion_text_web = ""
        promotion_type_web = ""
        euro_html = False
        search_terms = ["Spara", "Lagre", "Tallentaa", "Speichern", "Säästä","Spar", "Spare"]
        # Create a regular expression pattern to search for any of the terms
        pattern = re.compile("|".join(search_terms))
        try: 
            if  save != None and pattern.search(save):
                if re.search(r'>\d+%<', save):
                    discount_type = "Percentage"
                elif re.search(r'>\d+<', save):
                    discount_type = "Fixed"
                elif re.search(r'>\d+€</', save):
                    discount_type = "Fixed"
                    euro_html = True

                  
                elif re.search(r'>\d+/%<', save) or (re.search(r'>\d+<span', save) and re.search(r'>-</span', save) and re.search(r'>.</span', save)):
                    discount_type = ""
                    logger.log_warning(f"Spider - Discount 'Save' present but text not recognized. Url: {response.url}")

                else:
                    discount_type = ""

            if discount_type == "Percentage":
                save_amount = (re.search(r'>\d+%<', discount).group()).replace(">", "").replace("<", "")
            
            elif discount_type == "Fixed":
                if euro_html:
                    save_amount = (re.search(r'>\d+€<', discount).group()).replace(">", "").replace("<", "")
                else:
                    save_amount = (re.search(r'>\d+<', discount).group()).replace(">", "").replace("<", "")
               
            club_pattern = re.compile(r'fill="url\(#club-rusta-a\)"')
            club = response.xpath("//section//path[@fill='url(#club-rusta-a)']").get()

            if club:
                if club_pattern.search(club):
                    discount_type = "Club"
            elif multi_combo_package:
                multi_pattern = r'>\d+ för<|>\d+ hintaan<|>\d+ for<|>\d+ für<'
                combo_pattern = r'>\d+ för \d+<|>Ota \d+, maksa \d+<|>\d for \d+<|>\d für \d+<'
                if re.search(multi_pattern, multi_combo_package):
                    promotion_text_web = re.search(multi_pattern, multi_combo_package).group().replace(">", "").replace("<", "")
                    promotion_type_web = "Multi"

                elif re.search(combo_pattern, multi_combo_package):
                    promotion_type_web = "Combo"
                    promotion_text_web = re.search(combo_pattern, multi_combo_package).group().replace(">", "").replace("<", "")  

                elif re.search(r'Package', multi_combo_package):
                    promotion_type_web = "Package"
                else:
                    promotion_type_web = "" if self.scrape in(const.ACTIVE) else const.PROMOTION_NOT_FOUND
            if visible_price:
                if re.search(r'>\d+', visible_price):
                    price = re.search(r'>\d+', visible_price).group().replace(">", "") 
                    float_price = re.search(r'\d+</span></span>', visible_price)
                    if float_price:
                        price += '.' + float_price.group().replace("</span></span>", "")
                    price = Decimal(price) if price != None else None
            if show_original_price:
                if re.search(r'>', show_original_price):
                    if re.search(r'\((.*?)\)', show_original_price):
                        original_price = re.search(r'\((.*?)\)', show_original_price).group()
                    else:
                        original_price = re.search(r'>(.*?)<', show_original_price).group().replace(">", "").replace("<", "")

            save_amount = re.escape(save_amount) if save_amount != None else None
            if self.scrape in (const.WEEK, const.ROLLING):
                result = {const.DISCOUNT_TYPE: discount_type, const.PROMOTION_TYPE_WEB : promotion_type_web, const.PROMOTION_TEXT_WEB: promotion_text_web,
                    const.SAVE_AMOUNT: save_amount, const.VISIBLE_PRICE: price, const.PRICE_INFO: original_price, const.PROMOTION_TYPE:data.get(const.PROMOTION_TYPE),
                    const.PROMOTION_DESC: data.get(const.PROMOTION_DESC), const.SALES_START: data.get(const.SALES_START), const.SALES_END: data.get(const.SALES_END)}
            elif self.scrape == const.ACTIVE:
                result = {const.DISCOUNT_TYPE: discount_type, const.PROMOTION_TYPE_WEB : promotion_type_web, const.PROMOTION_TEXT_WEB: promotion_text_web,
                    const.SAVE_AMOUNT: save_amount, const.VISIBLE_PRICE: price, const.PRICE_INFO: original_price}
            return result
        except re_error as e:
            logger.log_error(f"Spider - Error parsing PDP. Url: {response.url}: {e}")


    def get_crawler(self):
        return self.crawler

    
class spiderDict():
    def __init__(self):
        self.data =  {   
                    const.ARTICLE_ID: "",
                    const.ARTICLE_NAME: "",
                    const.COMPANY: "",
                    const.ACTIVE_CTR: False,
                    const.ACTIVE_WEB: False,
                    const.PRODUCT_COORDINATOR: "",
                    const.LIFE_CYCLE_STATUS: "",
                    const.DATE: "",
                    const.RETAIL_PRICE: Decimal,
                    const.ACTUAL_PRICE: Decimal,
                    const.ARTICLE_FOUND: False,
                    const.SEARCH_URL: "",
                    const.RELATED: False,    
                    const.DISCOUNT_TYPE: "",
                    const.PROMOTION_TYPE_WEB: "",
                    const.PROMOTION_TEXT_WEB: "",
                    const.SAVE_AMOUNT: "", 
                    const.VISIBLE_PRICE: Decimal(0),
                    const.PRICE_INFO: "",
                    const.DEPARTMENT: "",
                    const.SALES_AREA: ""}
                
class spiderCampaignDict():
    def __init__(self):
        self.data =  {   
            const.SEARCH_URL: "",
            const.CAMPAIGN_ID: Decimal(0),
            const.CAMPAIGN_DESCRIPTION: "",
            const.ARTICLE_ID: "",
            const.ARTICLE_NAME: "",
            const.SALES_START: "",
            const.SALES_END: "",
            const.DEPARTMENT: "", 
            const.SALESGROUP: "",
            const.PROMOTION_DESC: "",
            const.PROMOTION_TEXT_WEB: "",
            const.COMPANY: "",
            const.DISCOUNT_TYPE: "",
            const.LIFE_CYCLE_STATUS: "",
            const.PROMOTION_TYPE: "",   
            const.PROMOTION_TYPE_WEB: "",
            const.ACTIVE_WEB: False,
            const.PRODUCT_COORDINATOR: "",
            const.CAMPAIGN_COORDINATOR: "",
            const.DATE: "",
            const.CAMPAIGN_PERIOD: "",
            const.ARTICLE_FOUND: False,
            const.RELATED: False,
            const.SAVE_AMOUNT: "",
            const.VISIBLE_PRICE: Decimal(0),
            const.PRICE_INFO: "",
                   }


