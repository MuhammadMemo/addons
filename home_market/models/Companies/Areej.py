
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Areej_Company:

    def Areej_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 15
        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='main-page-wrapper')
        # Loop to Get Product name and URL
        for i in filter_Products:
            for p in i.find_all("h3", class_='wd-entities-title'):
                products.append(p.text.strip())
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)  
                ribbon_id.append(ribbon)    

            for c in  i.find_all("div", class_='wrapp-product-price'):
                if c:
                    price_tag = c.find("ins")
                    if price_tag:
                        price_value = price_tag.find("bdi").text.strip()
                        price.append(price_value)
                    else:
                        price.append(None)
                    
                    
                    compare_list_price_tag = c.find("del")
                    if compare_list_price_tag:
                        compare_list_price_value = \
                            compare_list_price_tag.find("bdi")\
                            .text.strip()
                        compare_list_price.append(compare_list_price_value)
                    else:
                        compare_list_price.append(None)
            
                
            for m in  i.find_all("div", class_='product-element-top wd-quick-shop'):
                a_tag = m.find('a')
                if a_tag:
                    img_tag = a_tag.find('img')
                    image_url = img_tag['src']
                    images.append(image_url) 
                    
            for u in i.find_all("div", class_='product-element-top wd-quick-shop') :
                l_tag = u.find('a')
                if l_tag:
                    url = l_tag['href']
                    urls.append(url) 
            
        
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
    