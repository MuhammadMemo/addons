
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Chic_Homz_Company:
    
    def Chic_Homz_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 13
        # Filter Products in HTML

        filter_Products = soup.find_all("div", class_='collection page-width')

        # Loop to Get Product name and URL
        for product_section in filter_Products:
            for p in product_section.find_all("h3", class_="card__heading h5"):
                # pro = p.find("h3")
                # products.append(pro.text.strip())
                products.append(p.text.strip())
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)
                ribbon_id.append(ribbon)
                # Extract the product URL from the <a> tag
                a_tag = p.find("a", class_="full-unstyled-link")
                if a_tag:
                    product_url = a_tag.get('href')
                    # Construct the full URL if needed (assuming the site is relative)
                    full_url = f"https://chichomz.com{product_url}"  # Replace with the actual domain
                    urls.append(full_url)
                
            # Extract prices and compare list prices
            for c in product_section.find_all("div", class_='price__container'):
                # Extract the current price
                current_price_tag = c.find("span", class_="price-item price-item--sale price-item--last")
                if current_price_tag:
                    price.append(current_price_tag.text.strip())

                # Extract the compare list price (strikethrough price)
                compare_price_tag = c.find("s", class_="price-item price-item--regular")
                if compare_price_tag:
                    compare_list_price.append(compare_price_tag.text.strip()) 
                    
                
            for image_section in product_section.find_all("div", class_="media media--transparent media--hover-effect"):
                # Find the <img> tag within this section
                image_tag = image_section.find("img")
                if image_tag:
                    image_url = image_tag.get('src')
                    if image_url:
                        # Construct the full image URL if needed (assuming the site uses a relative path)
                        full_img_url = f"https:{image_url}"  # Assuming the 'src' is missing the protocol
                        # print(f"Image URL: {full_img_url}")
                        images.append(full_img_url)

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