
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Zahra_Company:
    
      def Zahra_Format(self, soup, company, category, category_id, tag_id):
        products = []
        urls = []
        company_list = []
        category_list = []
        price = []
        compare_list_price = []
        category_ids = []
        tag_ids = []
        images = []
        ribbon_id = []
        ribbon = 14
        
        # Filter the main product wrapper in HTML
        product_wrapper = soup.find("div", class_='o_wsale_products_grid_table_wrapper')
        
        # If wrapper exists, loop through each product inside it
        if product_wrapper:
            product_items = product_wrapper.find_all("td", class_='oe_product te_shop_grid')  # Adjust this based on the correct product container class
            
            # Loop to Get Product name and other details
            for i in product_items:
                # Get product name
                product_name_tag = i.find("h6", class_='o_wsale_products_item_title mb-1')
                if product_name_tag:
                    products.append(product_name_tag.text.strip())
                    company_list.append(company)
                    category_list.append(category)
                    category_ids.append(category_id)
                    tag_ids.append(tag_id)
                    ribbon_id.append(ribbon)
                else:
                    products.append('')  # Append empty string if product name not found

                # Get price
                price_tag = i.find("span", class_='te_p_sm')
                if price_tag:
                    price.append(price_tag.text.strip())
                else:
                    price.append('0')  # Append '0' if price not found

                # Get compare list price
                compare_price_tag = i.find("del", class_='text-danger mr-1 te_p_disc')
                if compare_price_tag:
                    compare_list_price.append(compare_price_tag.text.strip())
                else:
                    compare_list_price.append('0')  # Append '0' if compare price not found

                # Get image
                img_div = i.find("div", class_='card-body p-1 oe_product_image')
                if img_div:
                    a_tag = img_div.find('a')
                    if a_tag:
                        img_tag = a_tag.find('img')
                        if img_tag and 'data-src' in img_tag.attrs:
                            image_url = img_tag['data-src']
                            full_url_image = f"https://www.zahrafurnitureco.com{image_url}"
                            images.append(full_url_image)
                        else:
                            images.append('')  # Append empty string if no image found
                else:
                    images.append('')  # Append empty string if no image div found

                # Get URL
                if product_name_tag:
                    l_tag = product_name_tag.find('a')
                    if l_tag:
                        url = l_tag['href']
                        full_url = f"https://www.zahrafurnitureco.com{url}"
                        urls.append(full_url)
                    else:
                        urls.append('')  # Append empty string if no URL found
                else:
                    urls.append('')  # Append empty string if no product name tag found

        else:
            _logger.warning("No product wrapper found.")

        # Log lengths for debugging
        # _logger.info(f"len products: {len(products)}, urls: {len(urls)}, images: {len(images)}, price: {len(price)}, compare_list_price: {len(compare_list_price)}")           

        # Ensure all lists are the same length
        data = {
            'Company': company_list,
            'Category': category_list,
            'Products': products,
            'URL': urls,
            'Image': images,
            'Price': price,
            'CompareListPrice': compare_list_price,
            'CategoryID': category_ids,
            'TagID': tag_ids,
            'ribbon': ribbon_id
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        return df