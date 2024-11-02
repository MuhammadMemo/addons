import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Carrefour_Company:
    
    def Carrefour_Formate(self, soup, company, category, category_id, tag_id):
        products = []
        # urls = []
        company_list = []
        category_list = []
        # price = []
        # compare_list_price = []
        category_ids = []
        tag_ids = []
        # images = []
        # ribbon_id = []
        # ribbon = 16
        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='css-14tfefh')
        # Loop to Get Product name and URL
        for i in filter_Products:
            for p in i.find_all("div", class_='css-tuzc44'):
                products.append(p.text.strip())
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)  
                # ribbon_id.append(ribbon)  
        _logger.info(products)