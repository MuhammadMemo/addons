

import pandas as pd
import logging
from odoo.http import request
from bs4 import BeautifulSoup
import time

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Sofa_Company:
   
    def Sofa_Format(self, driver, url, company, category, category_id, tag_id):

        driver.get(url)
        _logger.info(f"Driver successfully initialized.")
        
        products = []
        urls = []
        company_list = []
        category_list = []
        prices = []
        compare_list_prices = []
        category_ids = []
        tag_ids = []
        images = []
        ribbon_id = []
        ribbon = 19

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_wrapper = soup.find("div", class_='wd-products-element')

            if product_wrapper:
                product_items = product_wrapper.find_all("div", class_='product-grid-item')
                _logger.info(f"Found {len(product_items)} products.")
                
                for item in product_items:
                    # Initialize default values for each product
                    product_name = ''
                    product_url = ''
                    product_image = ''
                    product_price = ''
                    product_compare_price = ''

                    # Extract product name
                    product_name_tag = item.find("h3", class_='wd-entities-title')
                    if product_name_tag:
                        product_name = product_name_tag.text.strip()
                    
                    # Extract product URL
                    url_tag = item.find("a", class_='product-image-link')
                    if url_tag and url_tag.get('href'):
                        product_url = url_tag['href']

                    # Extract product image
                    image_tag = item.find("img")
                    if image_tag:
                        product_image = self.extract_image_url_Sofa_Furniture(image_tag)

                    # Extract price and compare list price
                    price_wrapper = item.find("div", class_="wrap-price")
                    if price_wrapper:
                        price_range = price_wrapper.find_all("span", class_='woocommerce-Price-amount')

                        # Case 1: Price range
                        if len(price_range) == 2 and not price_wrapper.find("del") and not price_wrapper.find("ins"):
                            product_price = price_range[0].text.strip()
                            product_compare_price = price_range[1].text.strip()

                        # Case 2: Discounted price
                        elif price_wrapper.find("del") and price_wrapper.find("ins"):
                            del_price = price_wrapper.find("del").find("span", class_='woocommerce-Price-amount')
                            ins_price = price_wrapper.find("ins").find("span", class_='woocommerce-Price-amount')
                            
                            product_compare_price = del_price.text.strip()  # Compare price
                            product_price = ins_price.text.strip()          # Current price

                        # Case 3: Single price
                        elif len(price_range) == 1:
                            product_price = price_range[0].text.strip()
                    
                    # Append extracted data to the lists
                    products.append(product_name)
                    urls.append(product_url)
                    images.append(product_image)
                    prices.append(product_price)
                    compare_list_prices.append(product_compare_price)
                    company_list.append(company)
                    category_list.append(category)
                    category_ids.append(category_id)
                    tag_ids.append(tag_id)
                    ribbon_id.append(ribbon)

            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Log information
        _logger.info(f"URL image test line: {products} : {images}")

        # Create DataFrame with all product data
        data = {
            'Company': company_list,
            'Category': category_list,
            'Products': products,
            'URL': urls,
            'Image': images,
            'Price': prices,
            'CompareListPrice': compare_list_prices,
            'CategoryID': category_ids,
            'TagID': tag_ids,
            'ribbon': ribbon_id
        }
        driver.quit()  # Ensures the ChromeDriver process is terminated

        if all(len(lst) == len(products) for lst in [urls, images, prices, compare_list_prices, company_list]):
            df = pd.DataFrame(data)
            return df
        else:
            _logger.warning("Inconsistent data lengths, unable to create DataFrame.")
            return None
        
    def extract_image_url_Sofa_Furniture(self, img_tag):
        """
        This function extracts the most relevant image URL from an img tag.
        It prioritizes srcset, then data-src, and finally src.
        """
        # 1. Try extracting from `srcset`
        if 'srcset' in img_tag.attrs:
            # srcset contains multiple resolutions, so typically we want the largest one
            srcset_value = img_tag['srcset']
            # Split srcset and get the last (largest resolution)
            largest_image = max(srcset_value.split(','), key=lambda x: int(x.split()[-1].replace('w', '')))
            # Extract the URL from the largest image entry
            return largest_image.split()[0]
        
        # 2. If no `srcset`, try extracting from `data-src`
        if 'data-src' in img_tag.attrs:
            return img_tag['data-src']
        
        # 3. Finally, fallback to `src`
        if 'src' in img_tag.attrs:
            return img_tag['src']
        
        # Return None if no valid image URL is found
        return None