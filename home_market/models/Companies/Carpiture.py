

import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Carpiture_Company:
    
    def Carpiture_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 9
        
        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='product-collection')
        
        # Loop to Get Product Details
        for product in filter_Products:
            # Extract product name
            product_title_tag = product.find("div", class_='product-collection__title')
            if product_title_tag:
                h2_tag = product_title_tag.find('h2')
                if h2_tag:
                    a_tag = h2_tag.find('a')
                    if a_tag:
                        products.append(a_tag.text.strip())
                        company_list.append(company)
                        category_list.append(category)
                        category_ids.append(category_id)
                        tag_ids.append(tag_id)
                        urls.append('https://carpiturefurniture.com' + a_tag['href'])
                        ribbon_id.append(ribbon)
                    else:
                        products.append(None)  # Ensures length consistency
                        company_list.append(company)
                        category_list.append(category)
                        category_ids.append(category_id)
                        tag_ids.append(tag_id)
                        urls.append(None)
            
           # Extract prices within the same div
            price_container = product.find("div", class_='frm-price-color')
            if price_container:
                price_span = price_container.find('span', class_='price')
                
                if price_span:
                    # Case with 'current' and 'compare' prices
                    current_price_tag = price_span.find('span', class_='current')
                    compare_price_tag = price_span.find('span', class_='compare')
                    
                    if current_price_tag:
                        price.append(current_price_tag.text.strip())
                    else:
                        # Handle case where only one price is available without 'current'
                        single_price_tag = price_span.find('span')
                        price.append(single_price_tag.text.strip() if single_price_tag else None)
                    
                    compare_list_price.append(compare_price_tag.text.strip() if compare_price_tag else None)
                else:
                    price.append(None)
                    compare_list_price.append(None)
            else:
                price.append(None)
                compare_list_price.append(None)

          # Extract image URL
            image_container = product.find("div", class_='media secondary_image_hover')

            if image_container:
                image_tag = image_container.find_all('img')
                
                if image_tag:
                    # Loop through all image tags and extract the correct image URL
                    for img in image_tag:
                        if 'src' in img.attrs:
                            image_url = "https:" + img['src'].split('?')[0]  # Extract the base URL
                            images.append(image_url)
                            break  # Stop after finding the first valid image
                        else:
                            images.append(None)
                else:
                    images.append(None)
            else:
                images.append(None)

        
        # Create the DataFrame only if all lists are of equal length
        # if len(set(map(len, [company_list, category_list, products, price, compare_list_price, category_ids, tag_ids, urls, images]))) == 1:
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
        # else:
        #     _logger.error("Error: Lists are not of equal length!")
        #     return None