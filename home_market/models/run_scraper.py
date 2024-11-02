from odoo import models, fields, api
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

_logger = logging.getLogger(__name__)

class run_scraper(models.Model):
    
    def action_run_scraper(self):
        for record in self:
            self._run_scraper_for_record(record)

    def action_run_all_scraper(self):
        records = self.search([])
        for record in records:
            self._run_scraper_for_record(record)

    def _run_scraper_for_record(self, record):
        company = record.category_id.name if record.category_id else 'Unknown'
        category = record.tag_id.name if record.tag_id else 'Unknown'
        url = record.category_url
        category_id = record.category_id.id
        tag_id = record.tag_id.id

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')

            if category == 'Mffco Furniture':
                df = self.mffco_format(soup, company, category, category_id, tag_id)
                _logger.info(f'Dataframe before cleaning: {df.head()}')
                data_html = self.dataCleaning(df)
                _logger.info(data_html)

        except requests.exceptions.RequestException as e:
            _logger.error(f'Request failed for URL {url}: {e}')

    def mffco_format(self, soup, company, category, category_id, tag_id):
        products = []
        company_list = []
        category_list = []
        price = []
        compare_list_price = []
        category_ids = []
        tag_ids = []
        
        filter_products = soup.find_all("div", class_='product_container')
        for i in filter_products:
            for p in i.find_all("h3", class_='title'):
                products.append(p.text)
                company_list.append(company)
                category_list.append(category)
                category_ids.append(category_id)
                tag_ids.append(tag_id)
        for a in soup.select('ins'):
            price.append(a.find_next('bdi').text)
        for b in soup.select('del'):
            compare_list_price.append(b.find_next('bdi').text)

        data = {
            'Company': company_list,
            'Category': category_list,
            'Products': products,
            'Price': price,
            'CompareListPrice': compare_list_price,
            'CategoryID': category_ids,
            'TagID': tag_ids
        }
        df = pd.DataFrame(data)
        # Clean the price columns and convert them to numeric types
        for column in ['Price', 'CompareListPrice']:
            df[column] = df[column].str.replace(',', '').str.replace('٬', '').str.replace('ج.م.', '').str.extract('(\d+)', expand=False).astype(float)

        # Calculate the discount
        df['Discount'] = (df['CompareListPrice'] - df['Price']) / df['CompareListPrice'] * 100
        
        # Round the values to 2 decimal places
        df['Price'] = df['Price'].round(2)
        df['CompareListPrice'] = df['CompareListPrice'].round(2)
        df['Discount'] = df['Discount'].round(2)
        
        _logger.info(f'DataFrame before cleaning: {df.head()}')
        return df

    def dataCleaning(self, df):
        _logger.info(f'DataFrame columns before cleaning: {df.columns.tolist()}')
        _logger.info(f'DataFrame before cleaning: {df.head()}')

        df = df.drop_duplicates(subset=['Products', 'Price', 'CompareListPrice'], keep='first')
        
        removabl = [',', '٬', 'ج.م.']
        for char in removabl:
            df['Price'] = df['Price'].astype(str).str.replace(char, '', regex=True)
            df['CompareListPrice'] = df['CompareListPrice'].astype(str).str.replace(char, '', regex=True)
        
        df['Price'] = df['Price'].str.extract(pat='(\d+)', expand=False).astype(float)
        df['CompareListPrice'] = df['CompareListPrice'].str.extract(pat='(\d+)', expand=False).astype(float)
        
        df['Products'] = df['Products'].str.strip()
        
        delete = ['فوتيه مارفل', 'كرسى هزاز مودرن']
        for char in delete:
            df = df.loc[~((df['Products'] == char))]
        
        df.reset_index(inplace=True, drop=True)
        _logger.info(f'DataFrame after cleaning: {df.head()}')
        
        return df.to_html()
