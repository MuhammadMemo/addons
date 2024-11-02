import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class ElMalik_Company:
    
    def ElMalik_Format(self, soup, company, category, category_id, tag_id):
        products = []
        company_list = []
        category_list = []
        price = []
        compare_list_price = []
        category_ids = []
        tag_ids = []
        urls = []
        images = []
        filter_Products = soup.find_all("div", class_='products')
        for i in filter_Products:
            # Loop Get Product name
            for p in i.find_all("h3", class_='heading-title product-name'):
                products.append(p.text)
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)
            for c in i.find_all(class_='woocommerce-Price-amount amount'):
                compare_list_price.append(c.text)
                price.append(c.text)
            for m in i.find_all("div", class_="thumbnail-wrapper"):
                product_url = m.find("a")['href']
                urls.append(product_url)
            for u in i.find_all("figure", class_="no-back-image"):
                product_image = u.find("img")['data-lazy-src']
                images.append(product_image)
        data = {
            'Category': category_list,
            'Products': products,
            'Price': price,
            'CompareListPrice': compare_list_price,
            'CategoryID': category_ids,
            'TagID': tag_ids,
            'URL': urls,
            'Image' : images
        }
        df = pd.DataFrame(data)
        return df