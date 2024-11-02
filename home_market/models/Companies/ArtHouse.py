

import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class ArtHouse_Company:
    
    def ArtHouse_Format(self, soup, company, category, category_id, tag_id):
        products = []
        company_list = []
        category_list = []
        price = []
        compare_list_price = []
        category_ids = []
        tag_ids = []
        urls = []
        images = []
        ribbon_id = []
        ribbon = 11
        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='column main')
        # Loop to Get Product name and URL
        for i in filter_Products:
            product_items = i.find_all("div", class_='product details product-item-details')
            for item in product_items:
                # Extract product name and URL
                product_name_tag = item.find("strong", class_="product name product-item-name")
                if product_name_tag:
                    products_tag = product_name_tag.find("a").text.strip()
                    products.append(products_tag)
                    product_url = product_name_tag.find("a")['href']
                    urls.append(product_url)
                else:
                    products.append(None)
                    urls.append(None)

                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)
                ribbon_id.append(ribbon)

                # Extract current price
                current_price_tag = item.find("span", class_="special-price")
                if current_price_tag:
                    current_price = current_price_tag.find("span", class_="price").text.strip()
                    price.append(current_price)
                else:
                    price.append(None)

                # Extract compare list price
                compare_list_price_tag = item.find("span", class_="old-price")
                if compare_list_price_tag:
                    compare_list_price_value = compare_list_price_tag.find("span", class_="price").text.strip()
                    compare_list_price.append(compare_list_price_value)
                else:
                    compare_list_price.append(None)
                
            # Extract image URLs separately from product-image-container
            img_tags = i.find_all("img", class_="product-image-photo main-img")
            for m in img_tags:
                images.append(m.get('data-lazysrc'))

        data = {
            'Company': company_list,
            'Category': category_list,
            'Products': products,
            'Price': price,
            'CompareListPrice': compare_list_price,
            'CategoryID': category_ids,
            'TagID': tag_ids,
            'URL': urls,
            'Image': images,
            'ribbon':ribbon_id
        }

        df = pd.DataFrame(data)
        return df