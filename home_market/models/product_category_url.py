from odoo import models, fields, api
import logging
from odoo import http
from odoo.http import request
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import base64
from odoo.tools import image_process
from io import BytesIO
from PIL import Image
import re
import sys

import random
from urllib.request import urlopen
import json
import itertools


from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from .Companies.mffco import Mffco_Company
from .Companies.kabbani import Kabbani_Company
from .Companies.Egypt import Egypt_Company
from .Companies.chic_homz import Chic_Homz_Company
from .Companies.American import American_Company
from .Companies.Carpiture import Carpiture_Company
from .Companies.Hub import Hub_Company
from .Companies.Zahra import Zahra_Company
from .Companies.Areej import Areej_Company
from .Companies.ArtHouse import ArtHouse_Company
from .Companies.Sofa import Sofa_Company

# 'sudo apt-get install libwebp-dev'
# 'pip install --upgrade pillow'
_logger = logging.getLogger(__name__)
class ProductCategoryUrl(models.Model):

    _name = 'product.category.url'
    _description = 'Product Category URL'
    category_id = fields.Many2one(
        'product.public.category',
        string='Category',
        required=True)
    tag_id = fields.Many2one('product.tag', string='Tag')
    category_url = fields.Char(string='Category URL', required=True)
    active = fields.Boolean(string='Active', default=True)
    df_list = []  # This is now a class-level attribute

    batch_schedule = fields.Integer(string='Batch Schedule', default=0)  # Define NoList as a field  
    serial_number = fields.Integer(string='Serial Number', default=1)
    page_number = fields.Integer(string='Page Number', default=1)

    valid_state = fields.Selection(
        [
            ('draft', 'Waiting'),
            ('Valid', 'Valid'),
            ('Invalid', 'Invalid'),
        ],
        string='Valid Status',
        readonly=True,
        copy=False,
        index=True,
        default='draft' )

    run_state = fields.Selection(
        [
            ('draft', 'Waiting'),
            ('Running', 'Running'),
            ('Done', 'Done'),
            ('Error', 'Error'),
        ],
        string='Run Status',
        readonly=True,
        copy=False,
        index=True,
        default='draft')
    
    def action_reset_to_waiting(self):
        for record in self:
            record.valid_state = 'draft'
            record.run_state = 'draft'

    def headers_agents(self):
       
        user_agents = [
            # Add your list of user agents here
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            ]
        user_agent = random.choice(user_agents)
        _logger.info(f'User-Agent ...: {user_agent}')

        headers = {'User-Agent': f'{user_agent}'}
        return headers
    
    def action_validate_url(self):
        for record in self:
            if self._validate_url(record.category_url):
                record.valid_state = 'Valid'
                _logger.info(f"URL validated for {record.category_url}")
            else:
                record.valid_state = 'Invalid'
                _logger.error(f"URL validation failed for {record.category_url}")

    def _validate_url(self, url):
        try:
            headers = self.headers_agents()
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            _logger.error(f"URL validation failed for {url}: {e}")
            return False

    def open_category_url(self):
        for record in self:
            return {
                'type': 'ir.actions.act_url',
                'url': record.category_url,
                'target': 'new',
            }

    def start_chromedriver(self):
        """Starts a ChromeDriver instance."""
        _logger.info("Initializing ChromeDriver")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Optional for headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Start ChromeDriver
        driver = webdriver.Remote(
            command_executor='http://localhost:9515',
            options=chrome_options,
        )
        _logger.info("ChromeDriver started successfully")
        return driver

    def dataCleaning(self, df):
        # Make a copy of the DataFrame to avoid SettingWithCopyWarning
        df = df.copy()

        # Remove duplicates
        df = df.drop_duplicates(subset=['Products', 'Price', 'CompareListPrice'], keep='first')

        # Convert Arabic numerals to English numerals
        arabic_to_english_numerals = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
        df['Price'] = df['Price'].astype(str).apply(lambda x: x.translate(arabic_to_english_numerals))
        df['CompareListPrice'] = df['CompareListPrice'].astype(str).apply(lambda x: x.translate(arabic_to_english_numerals))

        # Remove Arabic thousand separators
        df['Price'] = df['Price'].str.replace('٬', '', regex=False)
        df['CompareListPrice'] = df['CompareListPrice'].str.replace('٬', '', regex=False)

        # Replace Arabic decimal points with English decimal points
        df['Price'] = df['Price'].str.replace('٫', '.', regex=False)
        df['CompareListPrice'] = df['CompareListPrice'].str.replace('٫', '.', regex=False)

        # Remove commas, currency symbols, and any other unwanted characters
        removabl = [',', 'ج.م.', 'EGP', 'LE']
        for char in removabl:
            df['Price'] = df['Price'].str.replace(char, '', regex=True)
            df['CompareListPrice'] = df['CompareListPrice'].str.replace(char, '', regex=True)

        # Extract numeric values
        df['Price'] = df['Price'].str.extract(pat=r'(\d+\.\d+|\d+)', expand= False).astype(float)
        df['CompareListPrice'] = df['CompareListPrice'].str.extract(pat=r'(\d+\.\d+|\d+)', expand=False).astype(float)

        # # Remove specific unwanted product names
        # delete = ['فوتيه مارفل', 'كرسى هزاز مودرن']
        # df = df[~df['Products'].isin(delete)]
        # # Add a unique identifier to duplicate product names
        # df['ProductID'] = df.groupby('Products').cumcount() + 1
        # df['Products'] = df.apply(lambda x: f"{x['Products']} ({x['ProductID']})" if x['ProductID'] > 1 else x['Products'], axis=1)
        
        # Group by 'Products' and 'TagID' to handle duplicates within the same tag
        df['ProductID'] = df.groupby(['Products', 'TagID']).cumcount() + 1

        # Apply the unique identifier only if 'ProductID' is greater than 1
        df['Products'] = df.apply(lambda x: f"{x['Products']} ({x['ProductID']})" if x['ProductID'] > 1 else x['Products'], axis=1)


        # Drop the 'ProductID' column if not needed
        df.drop('ProductID', axis=1, inplace=True)

        # Clean up product names
        # df['Products'] = df['Products'].str.replace('رئيسية', '', regex=True).str.replace('وسط', '', regex=True).str.replace('جوزى', '', regex=True).str.strip()

        _logger.info('Data has been cleaned .....')

        return df

    def calc_Discount(self, df):
        # Convert price and compare list price to numeric, forcing errors to NaN
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['CompareListPrice'] = \
            pd.to_numeric(df['CompareListPrice'], errors='coerce')

        # Calculate the discount, handling NaN values
        df['Discount'] = (df['CompareListPrice'] - df['Price']) / \
            df['CompareListPrice'] * 100
            
        # Round the values to 2 decimal places
        df['Price'] = df['Price'].round(2)
        df['CompareListPrice'] = df['CompareListPrice'].round(2)
        df['Discount'] = df['Discount'].round(2)
        
        # Log the dataframe for debugging
        _logger.info('Calculated Discount .....')
        
        return df
    
    def action_run_scraper(self):
        # records = self.search([], order="category_id asc")
       
        for record in self:
            self._run_scraper_for_record(record)
            
        if not self.df_list:
            _logger.warning("No DataFrames available to process")
        else:
            # self.reset_serial_number()
            self.process_dataframes()
         
     # Define a class-level variable for the serial number
   
    def reset_serial_number(self):
        for record in self:
            record.serial_number = 1
        _logger.info("Serial numbers have been reset to 1.")


    def _run_scraper_for_record(self, record):
        # Extract relevant record details
        category = record.category_id.name if record.category_id else 'Unknown'
        company = record.tag_id.name if record.tag_id else 'Unknown'
        url = record.category_url
        category_id = record.category_id.id if record.category_id else None
        tag_id = record.tag_id.id if record.tag_id else None

        _logger.info(f"Starting scraper for Company: {company}, Category: {category}, URL: {url}")

        # Validate URL and set error state if invalid
        if not self._validate_url(url):
            record.valid_state, record.run_state = 'Invalid', 'Error'
            _logger.error(f"Invalid URL: {url}")
            return

        # Define company-specific formatters
        company_formatters = {
            'Mffco Furniture': Mffco_Company().Mffco_Format,
            'kabbani Furniture': Kabbani_Company().Kabbani_Format,
            'Furniture Of Egypt': Egypt_Company().Egypt_Format,
            'Chic Homz Furniture': Chic_Homz_Company().Chic_Homz_Format,
            'American Furniture': American_Company().American_Format,
            'Carpiture Furniture': Carpiture_Company().Carpiture_Format,
            'Hub Furniture': Hub_Company().Hub_Format,
            'Zahra Furniture': Zahra_Company().Zahra_Format,
            'Areej Furniture': Areej_Company().Areej_Format,
            'Art House Furniture': ArtHouse_Company().ArtHouse_Format,
            # Ensure all arguments are passed correctly
            'Sofa Zone Furniture': lambda soup, company, category, category_id, tag_id: Sofa_Company().Sofa_Format(
             self.start_chromedriver(), url, company, category, category_id, tag_id),
        }

        # Set initial record state
        record.valid_state, record.run_state = 'draft', 'draft'

        try:
            # Request the URL content

            # session = requests.Session()
            # retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            # session.mount('https://', HTTPAdapter(max_retries=retries))

            # response = session.get(url, headers=self.headers_agents(), timeout=10)
            
            response = requests.get(url, headers=self.headers_agents(), timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Retrieve and execute the formatter
            formatter = company_formatters.get(company)
            if not formatter:
                _logger.warning(f"No formatter found for company: {company}")
                record.run_state = 'Error'
                return

            df = formatter(soup, company, category, category_id, tag_id)

            # Check for empty or None DataFrame and update state accordingly
            if df is None or df.empty:
                _logger.warning(f"DataFrame is empty for company: {company}")
                record.run_state = 'Error'
            else:
                df['GroupUrl'] = url
                self.df_list.append(df)
                record.run_state = 'Done'

        except requests.HTTPError as http_err:
            _logger.error(f"HTTP error for {url}: {http_err}")
            record.valid_state, record.run_state = 'Invalid', 'Error'
        except Exception as err:
            _logger.warning(f"Unexpected error for {url}: {err}")
            record.valid_state, record.run_state = 'Invalid', 'Error'

    def process_dataframes(self):
        # Concatenate all the DataFrames stored in df_list
        if self.df_list:
            df = pd.concat(self.df_list, ignore_index=True)
            # Process final_df as needed
            data_cleaned = self.dataCleaning(df)
            data_discounted = self.calc_Discount(data_cleaned)
            final_df = data_discounted
            
            self.add_new_products(final_df)
            self.Product_track_prices(final_df)
            self.update_image(final_df)
            # self.product_sort()
            self.add_variant(final_df)
            self.compare_and_update_publication(final_df)
            self.related_products(final_df)
            self.df_list.clear()  # Clears df_list after processing

        else:
            _logger.warning("No DataFrames available to process")
            # _logger.info(f"Processing the concatenated DataFrame: {final_df}")  # Add detailed logging here
            
    def add_new_products(self, df):
        
        # Process each row in the DataFrame
        for _, row in df.iterrows():

            product_name = row['Products']
            price = row['Price']
            compare_price = row['CompareListPrice']
            discount = row['Discount']
            category_id = row['CategoryID']
            tag_id = row['TagID']
            url = row['URL']
            image_url = row['Image']
            ribbon = row['ribbon']
            GroupUrl = row['GroupUrl']

            # Ensure that NaN values are handled
            if pd.isna(price):
                price = 0.0
            if pd.isna(compare_price):
                compare_price = 0.0
            if pd.isna(discount) or discount < 0:
                discount = 0.0

            # Exclude the row if any of the important fields are null
            if pd.isna(product_name) or pd.isna(price) or pd.isna(category_id):
                continue  # Skip this iteration and move to the next row

            # search existing product
            existing_product = self.env['product.template'].search([
                ('name', '=', product_name),
                ('public_categ_ids', 'in', [category_id]),
                ('product_tag_ids', 'in', tag_id),
            ],  limit=1) 
            order = 'product_tag_ids asc',
            
            if not existing_product:
                
                # Download the image and convert it to binary
                image_data = self.download_image(image_url)

                self.env['product.template'].create({
                    'name': product_name,
                    'public_categ_ids': [(4, category_id)],  # Add category to Many2many field
                    'product_tag_ids': [(4, tag_id)],  # Add tag to Many2many field
                    'list_price': price,
                    'compare_list_price': compare_price,
                    'Discount': discount,
                    'ProductUrl': url,
                    'image_1920': image_data,
                    'is_published': True,
                    'website_ribbon_id': ribbon,
                    'taxes_id': [(5, 0, 0)],
                    'allow_out_of_stock_order': False,
                    'detailed_type': 'product',
                    'GroupUrl': GroupUrl,
                    'out_of_stock_message': '.',
                })
                _logger.info(f'New product created in Product:\
                    {product_name}, {price}, {compare_price}, {discount}')
                
        _logger.info(f'End add New product')
                           
    def Product_track_prices(self, df):
        
        # Process each row in the DataFrame
        for _, row in df.iterrows():

            product_name = row['Products']
            price = row['Price']
            compare_price = row['CompareListPrice']
            discount = row['Discount']
            category_id = row['CategoryID']
            tag_id = row['TagID']
            url = row['URL']
            image_url = row['Image']
            ribbon = row['ribbon']
            GroupUrl = row['GroupUrl']

            # Ensure that NaN values are handled
            if pd.isna(price):
                price = 0.0
            if pd.isna(compare_price):
                compare_price = 0.0
            if pd.isna(discount) or discount < 0:
                discount = 0.0
                
            # Exclude the row if any of the important fields are null
            if pd.isna(product_name) or pd.isna(price) or pd.isna(category_id):
                continue  # Skip this iteration and move to the next row

            # search existing product
            existing_product = self.env['product.template'].search([
                ('name', '=', product_name),
                ('public_categ_ids', 'in', [category_id]),
                ('product_tag_ids', 'in', tag_id),
            ],  limit=1) 
            order = 'product_tag_ids asc',
            
            if existing_product:
                             
                # Check if the price, compare price or discount has changed
                if (existing_product.list_price != price or
                        existing_product.compare_list_price != compare_price 
                        or existing_product.Discount != discount):

                    # Insert the old data into product.track.prices
                    self.env['product.track.prices'].create({
                        'category_id': category_id,
                        'tag_id': tag_id,
                        'product_id': existing_product.id,
                        'track_prices': existing_product.list_price,
                        'track_compare_prices': existing_product.compare_list_price,
                        'track_discount': existing_product.Discount,
                        'track_date': fields.Date.today(),
                        'updated_price': price,
                        'updated_compare_price': compare_price,
                        'updated_discount': discount,
                        'difference_price': price - existing_product.list_price,
                        'difference_compare_price': compare_price - existing_product.compare_list_price,
                        'difference_discount': discount - existing_product.Discount,

                    })
                    # Update the product.template with new data
                    existing_product.write({
                        'list_price': price,
                        'compare_list_price': compare_price,
                        'Discount': discount,
                    })
                    _logger.info(f'Updated in Product and track prices:\
                        {product_name}, {price}, {compare_price}, {discount},{category_id},{tag_id}')
                else:
                    _logger.info(f'No Any Action for Product_track_prices :\
                        {product_name}, {price}, {compare_price}, {discount}, {category_id}, {tag_id}')
                    
        _logger.info("End Updated Product track prices")
                
    def compare_and_update_publication(self, df):
        # Get unique values of GroupUrl from the DataFrame
        GroupUrl = df['GroupUrl'].unique()

        for u in GroupUrl:
            # Filter rows where 'GroupUrl' matches 'u'
            productGroup = df[df['GroupUrl'] == u]
            df_products = productGroup['Products'].tolist()

            # Normalize DataFrame product names for comparison (convert to lowercase and strip spaces)
            normalized_df_products = [name.strip().lower() for name in df_products]


            url_products = self.env['product.template'].search([
                                                            ('GroupUrl', '=', u)])  # Fetch all matching products
                                                       
                                                       
            for product in url_products:
                product_name = product.name.strip().lower()  # Normalize product name from Odoo

                # Check if the normalized product name exists in the DataFrame
                if product_name not in normalized_df_products:
                    # If the product is not in the DataFrame, update 'is_published' to False
                    product.write({
                        'is_published': False,
                    })
                    _logger.info(f"Unpublished: Product '{product.name}' does not exist in DataFrame.")
                else:
                    product.write({
                        'is_published': True,
                    })
                    
                    _logger.info(f"Exists: Product '{product.name}' found in DataFrame. No action needed.")
                    
            _logger.info(f"Publication is End.")

    def add_variant(self, df):

        for _, row in df.iterrows():

            product_name = row['Products']
            category_id = row['CategoryID']
            tag_id = row['TagID']

            # Step 1: Check if the Tag exists
            tag = self.env['product.tag'].search([('id', '=', tag_id)], limit=1)

            if tag:  # attribute
                # Get the Arabic and English translations directly
                tag_name_ar = tag.with_context(lang='ar_001').name  # Arabic translation
                tag_name_en = tag.with_context(lang='en_US').name  # English translation

                # Step 2: Check if the attribute exists (based on the English translation)
                attribute = self.env['product.attribute'].search([('name', '=', tag_name_en)], limit=1)

                if not attribute:
                    # Step 3: Create the attribute with the English name first
                    attribute = self.env['product.attribute'].create({
                        'name': tag_name_en,  # Set initially with the English name
                        'visibility': 'hidden',
                        'display_type': 'radio',
                        'sequence' : 0,
                    })

                    # Step 4: Update the Arabic translation
                    attribute.with_context(lang='ar_001').write({
                        'name': tag_name_ar  # Set Arabic name translation
                    })
                else:
                    # Step 5: If the attribute exists, update both translations
                    attribute.with_context(lang='en_US').write({
                        'name': tag_name_en  # Update the English name
                    })
                    attribute.with_context(lang='ar_001').write({
                        'name': tag_name_ar  # Update the Arabic name
                    })

            # Step 6: Check if the Category exists
            category = self.env['product.public.category'].search([('id', '=', category_id)], limit=1)

            if category:  # value
                # Get the Arabic and English translations directly
                category_name_ar = category.with_context(lang='ar_001').name  # Arabic translation
                category_name_en = category.with_context(lang='en_US').name  # English translation

                # Step 7: Check if the attribute value exists
                attribute_value = self.env['product.attribute.value'].search([
                        ('name', '=', category_name_en),
                        ('attribute_id', '=', attribute.id)  # Ensure the attribute value belongs to the attribute
                    ], limit=1)


                if not attribute_value:
                    # Step 8: Create the attribute value with the English name first
                    attribute_value = self.env['product.attribute.value'].create({
                        'name': category_name_en,  # Set initially with the English name
                        'attribute_id': attribute.id,  # Link the value to the attribute
                        'color': 2,
                        'is_custom' : False,
                        'sequence' : 0,
                        'default_extra_price' : 0,
                    })

                    # Step 9: Update the Arabic translation
                    attribute_value.with_context(lang='ar_001').write({
                        'name': category_name_ar  # Set Arabic name translation
                    })
                else:
                    # Step 10: If the attribute value exists, update both translations
                    attribute_value.with_context(lang='en_US').write({
                        'name': category_name_en  # Update the English name
                    })
                    attribute_value.with_context(lang='ar_001').write({
                        'name': category_name_ar  # Update the Arabic name
                    })

            # Step 11: Search for the existing product
            existing_product = self.env['product.template'].search([
                ('name', '=', product_name),
                ('public_categ_ids', 'in', [category_id]),
                ('product_tag_ids', 'in', tag_id),
            ], limit=1)

            if existing_product:
                # Step 12: Check if the attribute line already exists for the product
                existing_attribute_line = self.env['product.template.attribute.line'].search([
                    ('product_tmpl_id', '=', existing_product.id),
                    ('attribute_id', '=', attribute.id),
                ], limit=1)

                if not existing_attribute_line:
                    # Step 13: Create a new attribute line with at least one value
                    attribute_line = self.env['product.template.attribute.line'].create({
                        'product_tmpl_id': existing_product.id,
                        'attribute_id': attribute.id,
                        'value_ids': [(6, 0, [attribute_value.id])]  # Link the attribute value
                    })
                    _logger.info(f"Created attribute line for {attribute.name} with value {attribute_value.name} for product {product_name}")
                else:
                    _logger.info(f"no action needed , Attribute line already exists for product {product_name}")

    def update_image(self, df):
        # Check if 'image_1920' field is empty (no image present)
        
        for _, row in df.iterrows():

            product_name = row['Products']
            # price = row['Price']
            # compare_price = row['CompareListPrice']
            # discount = row['Discount']
            category_id = row['CategoryID']
            tag_id = row['TagID']
            # url = row['URL']
            image_url = row['Image']
            # ribbon = row['ribbon']
            # GroupUrl = row['GroupUrl'] 
             # search existing product
            existing_product = self.env['product.template'].search([
                ('name', '=', product_name),
                ('public_categ_ids', 'in', [category_id]),
                ('product_tag_ids', 'in', tag_id),
            ],  limit=1) 
            order = 'product_tag_ids asc',
            
            if not existing_product.image_1920:
                image_data = self.download_image(image_url)
                
                # Update the product with the downloaded image
                existing_product.write({
                    'image_1920': image_data
                })
                _logger.info(f"update Product image for: {image_url}")

        _logger.info(f"End update Product image")
            
    def download_image(self, image_url):
        # Download the image and convert it to binary
        time.sleep(random.uniform(5, 8))  # Random delay between 5 to 8 seconds
        image_data = None
        if image_url:
            _logger.info(f'Attempting to download image from URL: {image_url}')
            
            # Check if the image_url is a data URL
            if image_url.startswith('data:'):
                try:
                    # Extract the base64 part from the data URL
                    header, data = image_url.split(',', 1)
                    
                    # Fix any missing base64 padding
                    missing_padding = len(data) % 4
                    if missing_padding:
                        data += '=' * (4 - missing_padding)
                    
                    image_data = base64.b64decode(data)
                    _logger.info(f'Processing image from data URL, size: {len(image_data)} bytes')
                except Exception as e:
                    _logger.error(f"Error processing data URL: {e}")
                    return None
            else:
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()  # Raise an error for bad responses
                    _logger.info(f'Downloading image from: {image_url}')
                    # or image_url.lower().endswith('.png')
                    # If the image is in .webp format, save it directly without resizing
                    if image_url.lower().endswith('.oooo') :
                        _logger.info(f'Skipping resize for WebP image: {image_url}')
                        image_data = base64.b64encode(response.content).decode('utf-8')
                    else:
                        # For other formats, resize the image
                        resized_image_data = self.resize_image(response.content)
                        
                        # Only process if resizing was successful
                        if resized_image_data:
                            image_data = base64.b64encode(resized_image_data).decode('utf-8')
                            _logger.info(f'Image data size after resizing: {len(resized_image_data)} bytes')
                            _logger.info(f'Completed downloading image from URL: {image_url}')
                        else:
                            _logger.error(f'Failed to process the image from: {image_url}')
                except requests.HTTPError as e:
                    _logger.error(f'HTTP error occurred while downloading image: {e}')
                except requests.RequestException as e:
                    _logger.error(f'Error downloading image: {e}')
                except Exception as e:
                    _logger.error(f'Unexpected error occurred: {e}')
        _logger.info(f'Completed downloading image')
        return image_data

    def resize_image(self, image_data, max_width=1920):
        try:
            # Try to open the image from binary data
            image = Image.open(BytesIO(image_data))
            
            # Convert the image to RGB if it is not already in that mode
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            # Check if resizing is necessary
            if image.width > max_width:
                aspect_ratio = image.height / image.width
                new_height = int(max_width * aspect_ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            # Save the image as JPEG, PNG, or WEBP
            image_format = 'JPEG'
            if image.format == 'PNG':
                image_format = 'PNG'
            elif image.format == 'WEBP':
                image_format = 'WEBP'
                
            image.save(output, format=image_format)
            return output.getvalue()
        
        except IOError as e:
            # Log error for image processing issues (including unrecognized formats)
            _logger.error(f"IOError: Failed to process image - {e}")
            return None
        except ValueError as e:
            # Log error for unsupported file extensions
            _logger.error(f"Error: {e}")
            return None
        except Exception as e:
            # Log any other errors
            _logger.error(f"Error processing image: {e}")
            return None

    def product_sort(self):
        sequence_increment = 1  # Increment by 1 for each product
        products_per_batch = 4  # Number of products before switching to the next company

        # Define category-based starting sequences
        category_sequence_map = {
            (1, 7, 8): 1000,   # Bedrooms
            (9, 10, 11): 3000,  # Living Room
            (16, 17, 18, 19): 5000,  # Office Furniture
            (14, 20, 21, 22): 7000  # Tables
        }
        default_sequence_start = 9000  # Default for uncategorized products

        # Keep track of the current sequence for each category
        category_current_sequence = {}

        # Fetch all active products
        products = self.env['product.template'].search([('active', '=', True)])   
        _logger.info(f"Found {len(products)} active products.")  # Debugging line

        # Sort products based on public_categ_ids and product_tag_ids
        products = sorted(products, key=lambda p: (
            p.public_categ_ids.ids[0] if p.public_categ_ids else float('inf'),  # Sort by the first category ID
            p.product_tag_ids.ids[0] if p.product_tag_ids else float('inf')   # Sort by the first tag ID
        ))

        # Create a dictionary to group products by their company tags
        company_products = {}

        # Group products by their associated company tags
        for product in products:
            company_tags = product.product_tag_ids
            if company_tags:
                # Use the first company tag (assuming each product has one relevant company tag)
                current_company = company_tags[0]
                if current_company not in company_products:
                    company_products[current_company] = []
                company_products[current_company].append(product)

        # List of companies to loop through
        company_list = list(company_products.keys())

        # Assign sequences to products, rotating through companies
        company_index = 0  # Start with the first company

        while any(company_products.values()):  # Continue until all companies' products are assigned
            # Get the current company's products
            current_company = company_list[company_index]
            products_for_company = company_products[current_company]

            # Assign sequences to up to 4 products for the current company
            for i in range(products_per_batch):
                if not products_for_company:
                    break  # No more products for this company

                product = products_for_company.pop(0)

                # Determine the starting sequence based on the product's public_categ_ids
                if product.public_categ_ids:
                    category_id = product.public_categ_ids[0].id  # Assuming the first category is the relevant one

                    # Find the appropriate starting sequence range for the category
                    for category_range, start_sequence in category_sequence_map.items():
                        if category_id in category_range:
                            if category_id not in category_current_sequence:
                                category_current_sequence[category_id] = start_sequence  # Start with the initial sequence
                            break
                    else:
                        if category_id not in category_current_sequence:
                            category_current_sequence[category_id] = default_sequence_start  # Use default for uncategorized products

                    # Get the current sequence for the category and increment it
                    current_sequence = category_current_sequence[category_id]
                    category_current_sequence[category_id] += sequence_increment  # Update the sequence for the next product
                else:
                    current_sequence = default_sequence_start  # Default for products without category

                # Write the sequence for the product
                product.write({'website_sequence': current_sequence})

                # Log the assignment
                _logger.info(f"Assigned sequence {current_sequence} to product {product.name} for company {current_company.name}")
                _logger.info(f"category_id {category_id}")

            # Move to the next company
            company_index = (company_index + 1) % len(company_list)

        _logger.info("Product sorting completed.")
    
    def related_products(self, df):
        # Ensure 'id' column exists to store product IDs
        df['id'] = None

        # Update DataFrame with product ID if product is found
        for index, row in df.iterrows():
            product_name = row['Products']
            category_id = row['CategoryID']
            tag_id = row['TagID']

            # Search for existing product in Odoo
            existing_product = self.env['product.template'].search([
                ('name', '=', product_name),
                ('public_categ_ids', 'in', [category_id]),
                ('product_tag_ids', 'in', [tag_id]),
            ],limit=1)

            # Update DataFrame if product is found
            if existing_product:
                df.at[index, 'id'] = existing_product.id

        # Convert DataFrame to log output for debugging
        # _logger.info(f'dfData : {df}')

        # Group products by 'GroupUrl' and generate product pairs
        link_groups = {}
        for i, row in df.iterrows():
            group_url = row['GroupUrl']
            if group_url not in link_groups:
                link_groups[group_url] = []
            link_groups[group_url].append({'name': row['Products'], 'id': row['id']})

        # Generate pairs for each link group
        for group, products in link_groups.items():
            product_names = [p['name'] for p in products]
            product_ids = [p['id'] for p in products]
            
            # Creating linked products with up to 16 entries per product
            linked_products = {src: [] for src in product_names}
            for src, dest in itertools.permutations(product_names, 2):
                if len(linked_products[src]) < 16:
                    linked_products[src].append(dest)

            # Update related products in Odoo
            for src in linked_products:
                src_id = df[df['Products'] == src]['id'].values[0]
                for dest in linked_products[src]:
                    dest_id = df[df['Products'] == dest]['id'].values[0]
                    
                   # Insert relationship in the 'product_alternative_rel' table
                    self.env.cr.execute("""
                        INSERT INTO product_alternative_rel (src_id, dest_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """, (src_id, dest_id))
                    
        _logger.info("Related products have been updated successfully.")

        # _logger.info(f'src_id :{src_id}, dest_id :{dest_id}')

    def run_batch_schedule_one(self):
        # Fetch all records ordered by category_id
        records = self.search([('batch_schedule', '=', 1)], order="category_id asc, tag_id asc")

        for record in records:
            self._run_scraper_for_record(record)
            
        if not self.df_list:
            _logger.warning("No DataFrames available to process")
        else:
            self.process_dataframes()
    
    def run_batch_schedule_two(self):
        # Fetch all records ordered by category_id
        records = self.search([('batch_schedule', '=', 2)], order="category_id asc, tag_id asc")

        for record in records:
            self._run_scraper_for_record(record)
            
        if not self.df_list:
            _logger.warning("No DataFrames available to process")
        else:
            self.process_dataframes()
            
    def run_batch_schedule_three(self):
        # Fetch all records ordered by category_id
        records = self.search([('batch_schedule', '=', 3)], order="category_id asc, tag_id asc")

        for record in records:
            self._run_scraper_for_record(record)
            
        if not self.df_list:
            _logger.warning("No DataFrames available to process")
        else:
            self.process_dataframes()
            
    def update_any_field(self, df):
        
         # Process each row in the DataFrame
        for _, row in df.iterrows():

            product_name = row['Products']
            price = row['Price']
            compare_price = row['CompareListPrice']
            discount = row['Discount']
            category_id = row['CategoryID']
            tag_id = row['TagID']
            url = row['URL']
            image_url = row['Image']
            ribbon = row['ribbon']
            GroupUrl = row['GroupUrl']
            
            # search existing product
            existing_product = self.env['product.template'].search([
                ('name', '=', product_name),
                ('public_categ_ids', 'in', [category_id]),
                ('product_tag_ids', 'in', tag_id),
            ],  limit=1) 
            order = 'product_tag_ids asc',
            
            if not existing_product:
            
                name_en = '.'
                existing_product.write({
                    'ProductUrl': url,
                    'GroupUrl': GroupUrl,
                    'allow_out_of_stock_order': False,
                    'out_of_stock_message': name_en,
                    })        