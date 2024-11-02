
import pandas as pd
import logging

# Initialize a logger for this module
_logger = logging.getLogger(__name__)

class Hub_Company:
    
    def Hub_Format(self, soup, company, category, category_id, tag_id):
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
        ribbon = 8
        # Filter Products in HTML
        filter_products = soup.find_all(
            "div", class_='products wrapper grid products-grid')

        for product_wrapper in filter_products:
            product_divs = product_wrapper.find_all(
                "div", class_="product-top")

            for product_div in product_divs:
                product_url = product_div.find("a")['href']
                img_tags = product_div.find("img")['src']
                urls.append(product_url)
                images.append(img_tags)
                ribbon_id.append(ribbon)

            product_name_tag = product_wrapper.find_all(
                                    "a", class_='product-item-link')

            for i in product_name_tag:
                product_name = i.text.strip()
                products.append(product_name)
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)

            # Extract current price
            price_tag = product_wrapper.find_all(
                "span", class_="special-price")

            for p in price_tag:
                if p:
                    current_price = p.find("span", class_="price")
                    if current_price:
                        prices.append(current_price.text.strip())
                    else:
                        prices.append(None)
                else:
                    prices.append(None)

                # Extract compare list price
            compare_list_price_tag = product_wrapper.\
                find_all("span", class_="old-price")
            for c in compare_list_price_tag:
                if c:
                    compare_price = c.find("span", class_="price")
                    if compare_price:
                        compare_list_prices.append(compare_price.text.strip())
                    else:
                        compare_list_prices.append(None)
                else:
                    compare_list_prices.append(None)
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