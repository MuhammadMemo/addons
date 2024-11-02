import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Smart_Company:
    
    def Smart_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 12

        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='jet-listing-grid jet-listing')

        # Loop to Get Product name and URL
        for i in filter_Products:
            for p in i.find_all("p", class_='elementor-heading-title elementor-size-default'):
                # Only append product names and URLs, avoiding non-product text
                a_tag = p.find('a')
                if a_tag:
                    products.append(a_tag.text.strip())
                    urls.append(a_tag.get('href').strip())
                    company_list.append(company)
                    category_list.append(category)
                    category_ids.append(category_id)
                    tag_ids.append(tag_id)
                    ribbon_id.append(ribbon)

            # Get image URL, skipping .svg files
            for img_container in i.find_all("div", class_='elementor-widget-container'):
                image_tag = img_container.find("img")
                if image_tag:
                    image_url = image_tag.get('src', '')
                    # Skip images with .svg extension
                    if image_url.endswith('.svg'):
                        print(f'Skipping SVG image: {image_url}')
                        continue
                    images.append(image_url)

            # Extract prices and compare list prices
            for c in i.find_all(class_='elementor-widget-container'):
                ins_tag = c.find('ins')
                if ins_tag:
                    bdi = ins_tag.find('bdi')
                    if bdi:
                        price.append(bdi.text.strip())   
                del_tag = c.find('del')
                if del_tag:
                    bdi = del_tag.find('bdi')
                    if bdi:
                        compare_list_price.append(bdi.text.strip())

        # Ensure the length of products, images, price, and compare_list_price match
        min_length = min(len(products), len(images), len(price), len(compare_list_price))

        # Adjust all lists to the minimum length to ensure consistency
        products = products[:min_length]
        urls = urls[:min_length]
        images = images[:min_length]
        price = price[:min_length]
        compare_list_price = compare_list_price[:min_length]
        company_list = company_list[:min_length]
        category_list = category_list[:min_length]
        category_ids = category_ids[:min_length]
        tag_ids = tag_ids[:min_length]
        ribbon_id = ribbon_id[:min_length]
        
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

        df = pd.DataFrame(data)
        return df
