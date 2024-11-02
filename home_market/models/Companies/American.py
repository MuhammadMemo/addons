


import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class American_Company:
    
    def American_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 10
        # Filter Products in HTML
        filter_Products = soup.find_all("div", class_='lakit-products__list_wrapper')
        # Loop to Get Product name and URL
        for i in filter_Products:
            for p in i.find_all("h3", class_='elementor-repeater-item-c8864c3 lakitp-zone-item product_item--title'):
                a_tag = p.find('a')
                if a_tag:
                    products.append(a_tag.text.strip())
                    urls.append(a_tag['href'])
                    company_list.append(company)
                    category_list.append(category)
                    category_ids.append(category_id)
                    tag_ids.append(tag_id)  
                    ribbon_id.append(ribbon)    
            # Extract prices within the same div
            for c in i.find_all("div", class_='elementor-repeater-item-97c83cc lakitp-zone-item product_item--price price'):
                # Extract compare list price and current price if both are present
                del_tag = c.find('del')
                ins_tag = c.find('ins')
                if del_tag and ins_tag:
                    bdi_del = del_tag.find('bdi')
                    bdi_ins = ins_tag.find('bdi')
                    if bdi_del and bdi_ins:
                        compare_list_price.append(bdi_del.text.strip())
                        price.append(bdi_ins.text.strip())
                    else:
                        compare_list_price.append(None)
                        price.append(None)
                else:
                    compare_list_price.append(None)
                    # Extract the current price if only one price is present
                    span_tag = c.find('span', class_='woocommerce-Price-amount amount')
                    if span_tag:
                        bdi = span_tag.find('bdi')
                        if bdi:
                            price.append(bdi.text.strip())
                        else:
                            price.append(None)
                    else:
                        price.append(None)     
                # Extract image URLs
            image_containers = i.find_all("div", class_='product_item--thumbnail-holder')
            for img_container in image_containers:
                a_tag = img_container.find('a')
                if a_tag:
                    img_tag = a_tag.find('img')
                    if img_tag and 'srcset' in img_tag.attrs:
                        image_url = img_tag['srcset'].split(', ')[-1].split(' ')[0]
                        images.append(image_url)
                    elif img_tag and 'src' in img_tag.attrs:
                        image_url = img_tag['src']
                        images.append(image_url)
                    else:
                        images.append(None)
                else:
                    images.append(None)
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
