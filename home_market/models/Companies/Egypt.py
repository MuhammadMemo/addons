
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Egypt_Company:
    
    def Egypt_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 7

        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='product-item')


        # Loop through each product
        for product in filter_Products:
            # Get product name
            product_name_tag = product.find("a", class_='product-title')
            if product_name_tag:
                product_name = product_name_tag.text.strip()
            else:
                product_name = "N/A"

            products.append(product_name)
            company_list.append(company)
            category_list.append(category)
            category_ids.append(category_id)
            tag_ids.append(tag_id)
            ribbon_id.append(ribbon)

            # Get product URL
            product_url = "https://www.furnitureofegypt.com" + product_name_tag['href'] if product_name_tag else None
            urls.append(product_url)

            # Get image URL
            image_tag = product.find("a", class_='product-img').find("img")
            if image_tag:
                image_url = image_tag['src']
            else:
                image_url = None
            images.append(image_url)

            # Get product price and compare price
            product_price_tag = product.find("p", class_='font-semibold')
            compare_price_tag = product.find("del", class_='text-red-500')

            if product_price_tag:
                price_text = product_price_tag.text.strip().replace(",", "").split()[0]  # Extract the numeric part of price
                price = float(price_text) if price_text.isdigit() else "N/A"
            else:
                price = "N/A"

            if compare_price_tag:
                compare_price_text = compare_price_tag.text.strip().replace(",", "").split()[0]  # Extract compare price
                compare_price = float(compare_price_text) if compare_price_text.isdigit() else price  # If compare price is not valid, use normal price
            else:
                compare_price = price  # Fallback to price if no compare price is available

            prices.append(price)
            compare_list_prices.append(compare_price)
                
        # # Ensure all lists are of the same length
        # lengths = [len(lst) for lst in [products, company_list, category_list, prices, compare_list_prices, category_ids, tag_ids, urls, images]]
        # if len(set(lengths)) != 1:
        #     raise ValueError("Mismatch in lengths of lists: {}".format(lengths))

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
    

    # def Egypt_Format(self, url, company, category, category_id, tag_id):
    #     products = []
    #     company_list = []
    #     category_list = []
    #     prices = []
    #     compare_list_prices = []
    #     category_ids = []
    #     tag_ids = []
    #     urls = []
    #     images = []
    #     ribbon_id = []
    #     ribbon = 7

    #     driver = self.start_chromedriver()
    #     _logger.info("ChromeDriver started successfully")
        
    #     driver.get(url)
    #     _logger.info("Driver successfully initialized.")
        
    #     previous_products_count = 0  # Track products count to detect changes
    #     while True:
    #         # Parse the page source with BeautifulSoup
    #         soup = BeautifulSoup(driver.page_source, 'html.parser')

    #         # Filter products in HTML
    #         filter_Products = soup.find_all("div", class_='product-item')

    #         # Loop through each product
    #         for product in filter_Products:
    #             # Get product name
    #             product_name_tag = product.find("a", class_='product-title')
    #             product_name = product_name_tag.text.strip() if product_name_tag else "N/A"

    #             products.append(product_name)
    #             company_list.append(company)
    #             category_list.append(category)
    #             category_ids.append(category_id)
    #             tag_ids.append(tag_id)
    #             ribbon_id.append(ribbon)

    #             # Get product URL
    #             product_url = "https://www.furnitureofegypt.com" + product_name_tag['href'] if product_name_tag else None
    #             urls.append(product_url)

    #             # Get image URL
    #             image_tag = product.find("a", class_='product-img').find("img")
    #             image_url = image_tag['src'] if image_tag else None
    #             images.append(image_url)

    #             # Get product price and compare price
    #             product_price_tag = product.find("p", class_='font-semibold')
    #             compare_price_tag = product.find("del", class_='text-red-500')

    #             if product_price_tag:
    #                 price_text = product_price_tag.text.strip().replace(",", "").split()[0]  # Extract the numeric part of price
    #                 price = float(price_text) if price_text.isdigit() else "N/A"
    #             else:
    #                 price = "N/A"

    #             compare_price = (
    #                 float(compare_price_tag.text.strip().replace(",", "").split()[0])
    #                 if compare_price_tag and compare_price_tag.text.strip().replace(",", "").split()[0].isdigit()
    #                 else price  # If no valid compare price, use normal price
    #             )

    #             prices.append(price)
    #             compare_list_prices.append(compare_price)

    #         _logger.info(f"List lengths: Products={len(products)}, Company={len(company_list)},Category={len(category_list)}, Ribbon={len(ribbon_id)}")
            
    #         # Check if the product count has increased
    #         if len(products) == previous_products_count:
    #             _logger.info("No new products loaded. Ending pagination.")
    #             break
    #         else:
    #             previous_products_count = len(products)
            
    #         # Attempt to click the 'Next' button
    #         try:
    #             next_button = driver.find_element_by_class_name("p-paginator-next")
    #             if "p-disabled" not in next_button.get_attribute("class"):
    #                 next_button.click()
    #                 _logger.info("Clicked 'Next' button.")
    #                 time.sleep(3)  # Wait for the page to load
    #             else:
    #                 _logger.info("Next button is disabled. Ending pagination.")
    #                 break
    #         except Exception as e:
    #             _logger.error(f"Error clicking 'Next' button: {e}")
    #             break

    #     # Compile the scraped data into a DataFrame
    #     try:
    #         data = {
    #             'Company': company_list,
    #             'Category': category_list,
    #             'Products': products,
    #             'Price': prices,
    #             'CompareListPrice': compare_list_prices,
    #             'CategoryID': category_ids,
    #             'TagID': tag_ids,
    #             'URL': urls,
    #             'Image': images,
    #             'ribbon': ribbon_id
    #         }
    #         df = pd.DataFrame(data)
    #     except ValueError as e:
    #         _logger.error(f"DataFrame creation error: {e}")
    #         _logger.info(f"List lengths: Products={len(products)}, Company={len(company_list)}, "
    #                     f"Category={len(category_list)}, Ribbon={len(ribbon_id)}")
    #         return None
    #     driver.quit()
    #     return df