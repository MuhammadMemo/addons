
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Kabbani_Company:
    def Kabbani_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 6

        # Filter Products in HTML
        filter_products = soup.find_all("div", class_='grid-view-item')

        # Loop to Get Product Details
        for product in filter_products:
            product_link = product.find("a", class_='grid-view-item__link')
            product_url = "https://www.kabbanifurniture.com" +\
                product_link['href'] if product_link else None
            product_title = product.find("a", class_='grid-view-item__title')\
                .text.strip() \
                if product.find("a", class_='grid-view-item__title') else None

            # Extract prices
            price_tag = product.find("span", class_='product-price__sale')
            price_value = price_tag.text.strip() if price_tag else None

            compare_list_price_tag = \
                product.find("s", class_='product-price__price regular')
            compare_list_price_value = compare_list_price_tag.text.strip()\
                .strip() if compare_list_price_tag else None

            # Extract image URL from data-bgset
            image_url = None
            image_tag = product.find("div", class_='grid-view-item__image')
            if image_tag:
               
                if 'data-bgset' in image_tag.attrs:
                    bgset = image_tag['data-bgset']
                   
                    # Extract the highest resolution image URL
                    image_urls = [url.strip() for url in bgset.split(",")]
                    image_url = "https:" + image_urls[-1].split(" ")[0]

                else:
                    _logger.info('not found data-bgset attribute in image_tag')
            else:
                _logger.info('not found image_tag')

            # Add product details to lists
            if product_url and product_title:
                products.append(product_title)
                urls.append(product_url)
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)
                prices.append(price_value)
                compare_list_prices.append(compare_list_price_value)
                images.append(image_url)
                ribbon_id.append(ribbon)

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
            'ribbon':ribbon_id
        }

        df = pd.DataFrame(data)
        return df