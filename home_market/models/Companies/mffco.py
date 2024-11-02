
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Mffco_Company:
    
    # def __init__(self):
    #     self.ribbon = 5  # Define any default values or initial settings
    
    def Mffco_Format(self, soup, company, category, category_id, tag_id):
        products = []
        company_list = []
        category_list = []
        prices = []
        compare_list_prices = []
        category_ids = []
        tag_ids = []
        urls = []
        images = []
        ribbon_id = []
        ribbon = 5

        # Filter Products in HTML
        filter_products = soup.find_all("li", class_='product_widget')
        # Loop to Get Product Details
        for product in filter_products:
            product_link = product.find("a", class_='product_widget_box')

            product_url = product_link['href'] if product_link else None

            product_title = product.find("h3", class_='title').text.strip() \
                if product.find("h3", class_='title') else None
            product_image = product.find("img")['src'] \
                if product.find("img") else None

            # Add product details to lists
            if product_url and product_title:
                products.append(product_title)
                urls.append(product_url)
                images.append(product_image)
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)
                ribbon_id.append(ribbon)
                # Extract prices
                price_tag = product.find("ins")
                if price_tag:
                    price_value = price_tag.find("bdi").text.strip()
                    prices.append(price_value)
                else:
                    prices.append(None)
                compare_list_price_tag = product.find("del")
                if compare_list_price_tag:
                    compare_list_price_value = \
                        compare_list_price_tag.find("bdi")\
                        .text.strip()
                    compare_list_prices.append(compare_list_price_value)
                else:
                    compare_list_prices.append(None)
        data = {
            'Company': company_list,
            'Category': category_list,
            'Products': products,
            'Price': prices,
            'CompareListPrice': compare_list_prices,
            'CategoryID': category_ids,
            'TagID': tag_ids,
            'URL': urls,
            'Image': images,
            'ribbon': ribbon_id
        }
        df = pd.DataFrame(data)
        return df
    