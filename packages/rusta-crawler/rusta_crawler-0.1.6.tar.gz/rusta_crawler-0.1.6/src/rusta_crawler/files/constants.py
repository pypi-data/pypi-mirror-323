

SQL_CAMPAIGN_OF_THE_WEEK = "campaign_of_the_week.sql"
SQL_ROLLING_CAMPAIGNS = "rolling_campaigns.sql"


SE_SQL = "all_active_articles_se.sql"
DE_SQL =  "all_active_articles_de.sql"
FI_SQL =  "all_active_articles_fi.sql"
NO_SQL = "all_active_articles_no.sql"

COMP_VALUE = "COMP_VALUE"
RETAIL_PRICE = "RETAIL_PRICE"
ACTUAL_PRICE = "ACTUAL_PRICE"
SQL_PAKET_PRICE = "paket_price"
URL = "url"
ACTIVE_WEB_SE = 'ACTIVE_WEB_SE'
ACTIVE_SE = 'ACTIVE_SE'
ACTIVE_WEB_NO = 'ACTIVE_WEB_NO'
ACTIVE_NO = 'ACTIVE_NO'
ACTIVE_WEB_FI = 'ACTIVE_WEB_FI'
ACTIVE_FI = 'ACTIVE_FI'
ACTIVE_DE = 'ACTIVE_DE'
ARTICLE_ID = 'ARTICLE_ID'
ITEM_NAME = 'ITEM_NAME'
LIFE_CYCLE_STATUS = 'LIFE_CYCLE_STATUS'
PROMOTION_TYPE = 'PROMOTION_TYPE'
PROMOTION_TYPE_WEB = 'PROMOTION_TYPE_WEB'
PROMOTION_TEXT_WEB = 'PROMOTION_TEXT_WEB'
PROMOTION_TEXT = 'PROMOTION_TEXT'
SAVE_AMOUNT = 'SAVE_AMOUNT'
VISIBLE_PRICE = 'VISIBLE_PRICE'
PRICE_INFO = 'PRICE_INFO'
ASSORTMENT_TYPE = 'ASSORTMENT_TYPE'
DISCOUNT_TYPE = 'DISCOUNT_TYPE'
ARTICLE_FOUND = 'ARTICLE_FOUND'
CAMPAIGN_ID = 'CAMPAIGN_ID'
CAMPAIGN_DESCRIPTION = 'CAMPAIGN_DESCRIPTION'
PROMOTION_DESC = "PROMOTION_DESC"
SALES_START = "SALES_START"
SALES_END = "SALES_END"
ACTIVE_WEB = 'ACTIVE_WEB'
ACTIVE_WEB_SE = "ACTIVE_WEB_SE"
ACTIVE_WEB_DE = "ACTIVE_WEB_DE"
COMPANY = "COMPANY"
COMPANY_NAME = "COMPANY_NAME"
START_URL = "START_URL"
SEARCH_URL = "SEARCH_URL"
ARTICLE_NAME = "ARTICLE_NAME"
RELEATED_ARTICLE = "RELEATED_ARTICLE"
PRODUCT_COORDINATOR = "PRODUCT_COORDINATOR"
CAMPAIGN_COORDINATOR = "CAMPAIGN_COORDINATOR"
DEPARTMENT = "DEPARTMENT"
SALESGROUP = "SALESGROUP"
SALES_AREA = "SALES_AREA"
FOUND_IN_EPI = "found_in_epi"
LONG_TEXT = "long_text"
VALID_PUB_CODE = "valid_pub_code"
PRODUCT_TYPE = "product_type"
VALID_CATALOG = "valid_catalog"
IMAGES = "images"
EPI_VISIBLE_ON_WEB = "visible_on_web"
VALID_IMAGE_TYPE = "valid_image_type"
PROMOTION_NOT_FOUND = "Promotion not found"
DIV_JS_MAIN_RESULT = "div.js-main-result"
DIV_PRICE_BADGE_PROMOTIONPRICE_MULTIPRICE = "div.price-badge.promotionprice.multiprice" 
DIV_PRICE_BADGE_PROMOTIONPRICE_COMBO = "div.price-badge.promotionprice.comboprice"
DIV_PRICE_BADGE_PROMOTIONPRICE_DISCOUNT = "div.price-badge.promotionprice.discount"
DIV_PRICE_BADGE_PACKAGE = "div.price-badge.promotionprice.packageprice"
DIV_PRICE_SALE = "div.price.sale"
MULTI = "Multi"
COMBO = "Combo"
DISCOUNT = "Discount"
SALE_PRICE = "Sale Price"
PACKAGE = "Package"
PACKAGE_FOUND = "PACKAGE_FOUND"
PROMOTION_NOT_FOUND = "Promotion not found"
TRUE = "True"
FALSE = "False"
YES = "Yes"
DATE = "SCRAPE_DATE"
PRICE_CORRECT = "PRICE_CORRECT"
RELATED = "RELATED"
COMPANY_URLS = {
    10: 'https://www.rusta.com/se/sv/sok/?q=',
    23: 'https://www.rusta.com/fi/fi/Etsi/?q=',
    20: 'https://www.rusta.com/no/no/sok/?q=',
    22: 'https://www.rusta.com/de/de/suche/?q=',  
    }

COMPANY_URLS_NEW_SITE = {
    10: "https://rusta.com/sv-se/sok?q=",
    20: "https://rusta.com/nb-no/sok?q=",
    23: "https://rusta.com/fi-fi/etsi?q=",
    22: "https://rusta.com/de-de/suche?q="  
    }


PIN_SITE_URL = { 'SE' : "https://prod.rusta.com/sv-se"
                , 'FI' : "https://prod.rusta.com/fi-fi"
                , 'NO' : "https://prod.rusta.com/no-no"
                , 'DE' : "https://prod.rusta.com/de-de"}

DATA_FIELDS = {
    1: "url",
    2: "ARTICLE_ID",
    3: "ARTICLE_NAME",
    4: "COMPANY",
    5: "ACTIVE",
    6: "ACTIVE_WEB",
    7: "PRODUCT_COORDINATOR",
    8: "LIFE_CYCLE_STATUS",
    9: "ARTICLE_FOUND"
}
QUERY_SQL = {
    "rolling_campaign": "rolling_campaigns.sql",
    "campaign_of_the_week": "campaign_of_the_week.sql",
    "all_articles_se": "all_active_articles_se.sql",
    "all_articles_de": "all_active_articles_de.sql",
    "all_articles_fi": "all_active_articles_fi.sql",
    "all_articles_no": "all_active_articles_no.sql",
    "package_price": "package_price.sql"
}

CAMPAIGN_OF_THE_WEEK = "campaign_of_the_week"
ROLLING_CAMPAIGNS = "rolling_campaign"
ACTIVE_ARTICLES = "active_articles"
PACKAGE_PRICE = "package_price"

WEEK = "week"
ROLLING = "rolling"
ACTIVE = "active"


CAMPAIGN_DATA_TO_LOAD = {WEEK: "campaign_of_the_week.sql", ROLLING: "rolling_campaigns.sql"}

XL_CAMPAIGN_HEADER =["URL", "CAMPAIGN_ID", "CAMPAIGN_DESCRIPTION", 
                            "PROMOTION_DESC", "ARTICLE_ID", "ITEM_NAME", "SALES_START", "SALES_END", 
                "PROMOTION_TYPE", "PROMOTION_TYPE_WEB", "DISCOUNT_TYPE", "ARTICLE_FOUND", "COMPANY", "CAMPAIGN_COORDINATOR"]

COMPANY_DICT = {"23":"FI-23", "10":"SE-10", "20":"NO-20", "22":"DE-22"}
COMPANY_NAME_TO_ID = {"SE":"10","FI":"23", "DE":"22", "NO":"20"}


XL_HEADER = ["URL",
    "ARTICLE_ID",
    "ARTICLE_NAME",
    "COMPANY",
    "ACTIVE",
    "ACTIVE_WEB",
    "PRODUCT_COORDINATOR",
    "LIFE_CYCLE_STATUS",
    "ARTICLE_FOUND",
    "found_in_epi",
    "long_text",
    "valid_pub_code",
    "product_type",
    "valid_catalog",
    "images",
    "valid_image_type"]
XL_HEADER_2 = ["URL",
    "ARTICLE_ID",
    "ARTICLE_NAME",
    "COMPANY",
    "ACTIVE",
    "ACTIVE_WEB",
    "PRODUCT_COORDINATOR",
    "LIFE_CYCLE_STATUS",
    "ARTICLE_FOUND"]

TBL_WEEK_RESULT = "week_result"
TBL_ROLLING_RESULT = "rolling_result"
TBL_ACTIVE_RESULT = "active_result"
TBL_ACTIVE_SCRAPE_RESULT = "ACTIVE_SCRAPE_RESULT"
TBL_PACKAGE_RESULT = "package_result"
TBL_CAMPAIGN_DATA = "new_site_campaign_data"
TBL_CAMPAIGN_DATA_PACKAGE = "campaign_data_package"
TBL_ACTIVE_SCRAPE_DATA = "ACTIVE_SCRAPE_DATA"
TBL_ACTIVE_SCRAPE_RESULT_TEMP = "ACTIVE_SCRAPE_RESULT_TEMP"
TBL_EPI_ARTICLE_STATUS = "epi_article_status"
TBL_CAMPAIGN_SCRAPE_RESULT = "CAMPAIGN_SCRAPE_RESULT"
TBL_CAMPAIGN_SCRAPE_ARTICLES = "CAMPAIGN_SCRAPE_ARTICLES"

TBL_NEW_SITE_CAMPAIGN_DATA = {WEEK: "new_site_campaign_data_week", ROLLING: "new_site_campaign_data_rolling"}
CAMPAIGN_PERIOD = "CAMPAIGN_PERIOD"

ITEM_LONG_COPY = 'ITEM_LONG_COPY'
ITEM_LONG_COPY_SE = 'ITEM_LONG_COPY_SE'
ITEM_LONG_COPY_NO = 'ITEM_LONG_COPY_NO'
ITEM_LONG_COPY_FI = 'ITEM_LONG_COPY_FI'
ITEM_LONG_COPY_DE = 'ITEM_LONG_COPY_DE'
ITEM_ACTIVE_WEB_SE = 'ITEM_ACTIVE_WEB_SE'
ITEM_ACTIVE_WEB_NO = 'ITEM_ACTIVE_WEB_NO'
ITEM_ACTIVE_WEB_FI = 'ITEM_ACTIVE_WEB_FI'
ITEM_ACTIVE_WEB_DE = 'ITEM_ACTIVE_WEB_DE'
ITEM_ECOM_STATUS_SE = 'ITEM_ECOM_STATUS_SE'
ITEM_ECOM_STATUS_NO = 'ITEM_ECOM_STATUS_NO'
ITEM_ECOM_STATUS_FI = 'ITEM_ECOM_STATUS_FI'
ITEM_ECOM_STATUS_DE = 'ITEM_ECOM_STATUS_DE'
ITEM_ENABLE_ECOM_SE = 'ITEM_ENABLE_ECOM_SE'
ITEM_ENABLE_ECOM_NO = 'ITEM_ENABLE_ECOM_NO'
ITEM_ENABLE_ECOM_FI = 'ITEM_ENABLE_ECOM_FI'
ITEM_ENABLE_ECOM_DE = 'ITEM_ENABLE_ECOM_DE'
OPTION_LONG_COPY_SE = 'OPTION_LONG_COPY_SE'
OPTION_LONG_COPY_NO = 'OPTION_LONG_COPY_NO'
OPTION_LONG_COPY_FI = 'OPTION_LONG_COPY_FI'
OPTION_LONG_COPY_DE = 'OPTION_LONG_COPY_DE'
ITEM_ACTIVE_WEB = 'ITEM_ACTIVE_WEB'
ITEM_ECOM_STATUS = 'ITEM_ECOM_STATUS'
ITEM_ENABLE_ECOM = 'ITEM_ENABLE_ECOM'
ITEM_CHANNEL = 'ITEM_CHANNEL'
OPTION_LONG_COPY = 'OPTION_LONG_COPY'
OPTION_CHANNEL = 'OPTION_CHANNEL'
PRODUCT_TYPE = 'PRODUCT_TYPE'
PRODUCT_CATEGORY = 'PRODUCT_CATEGORY'
PRODUCT_CHANNEL = 'PRODUCT_CHANNEL'
ITEM_ENTITY_ID = 'ITEM_ENTITY_ID'
OPTION_ENTITY_ID = 'OPTION_ENTITY_ID'
PRODUCT_ENTITY_ID = 'PRODUCT_ENTITY_ID'
ITEM_IMAGE_FILE_NAME = 'ITEM_IMAGE_FILE_NAME'
ITEM_IMAGE_RESC_TYPE    = 'ITEM_IMAGE_RESC_TYPE'

INP_CAMPAIGN_OF_THE_WEEK = "week"
INP_ROLLING_CAMPAIGNS = "rolling"
INP_PACKAGE_PRICE = "package"
CAMPAIGN_TO_CHECK = "campaign_to_check"
RETEST_ACTIVE_ARTICLES = "retest_active_articles"
DOWNLOAD_TIMEOUT = "download_timeout"
DOWNLOAD_SLOT = "download_slot"
DOWNLOAD_LATENCY = "download_latency"
DEPTH = "depth"
COUNTRIES = ["SE", "FI", "NO", "DE"]
SE = "SE"
FI = "FI"
NO = "NO"
DE = "DE"
COUNTRY = "COUNTRY"
SE_COMPANY_ID = "10"
FI_COMPANY_ID = "23"
NO_COMPANY_ID = "20"
DE_COMPANY_ID = "22"
ACTIVE_CTR = "ACTIVE"


CAMPAIGN_SQL = {WEEK : "campaign_of_the_week",
                ROLLING : "rolling_campaign"}