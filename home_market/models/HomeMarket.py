from odoo import models, fields, api
from . import product_category_url 
import requests
import logging
import urllib3
from urllib.parse import urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import random
_logger = logging.getLogger(__name__)

class HomeMarketProduct(models.Model):
    _inherit = 'product.template'

    ProductUrl = fields.Char(string='Product Url', store=True)
    # list_price = fields.Float(string='Price')
    Discount = fields.Float(string= 'Discount', compute='_compute_discount', store=True)
    GroupUrl = fields.Char(string='Group Url', store=True)
    # public_categ_ids = fields.many2many(string='Catogry', store=True)
    # is_published = fields.Boolean(string='Published', store=True)
    ProductUrlShort = fields.Char(string="Short URL", compute='_compute_product_url_short')
    product_track_ids = fields.One2many('product.track.prices', 'product_id', string='Price Tracks')

    def _compute_product_url_short(self):
        for product in self:
            if product.ProductUrl:
                parsed_url = urlparse(product.ProductUrl)
                product.ProductUrlShort = parsed_url.netloc  # This will return the domain name
            else:
                product.ProductUrlShort = ''

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
    
    valid_state = fields.Selection(
        [
            ('draft', 'Waiting'),
            ('Valid', 'Valid URL'),
            ('Invalid', 'Invalid URL'),
        ],
        string='Valid Status',
        readonly=True,
        copy=False,
        index=True,
        default='draft'
    )
    
    def action_reset_to_waiting(self):
        for record in self:
            record.valid_state = 'draft'
            record.run_state = 'draft'

    @api.depends('list_price', 'compare_list_price')
    def _compute_discount(self):
        for record in self:
            if record.compare_list_price:
                discount_value = ((record.compare_list_price - record.list_price) / record.compare_list_price) * 100
                record.Discount = round(discount_value, 2)  # Rounding to 2 decimal places
            else:
                record.Discount = 0

    def action_validate_template_url_All(self):
        for record in self:
            if self._validate_template_url(record.ProductUrl):
                record.valid_state = 'Valid'
            else:
                record.valid_state = 'Invalid'

    def _validate_template_url(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Suppressing SSL warnings
            response = requests.get(url, headers=headers, allow_redirects=True, verify=False)
            
            if response.status_code in [200, 301, 302, 204]:
                _logger.info(f"URL validated for {url} with status code {response.status_code}")
                return True
            else:
                _logger.error(f"URL validation failed for {url} with status code {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
                _logger.error(f"URL validation failed for {url}: {e}")
                return False

        
    def open_url(self):
        for record in self:
            return {
                'type': 'ir.actions.act_url',
                'url': record.ProductUrl,
                'target': 'new',
            }
    
    def sort_products(self):
        # records = self.search([])
        # records.write({'website_sequence': 10000})
        
        for record in self:  # Loop through the records
            # Check if the product has any public categories
            if record.public_categ_ids:
                # Get the category_id of the first public category
                category_id = record.public_categ_ids[0].id  
                
                # random.sample(range(100), 10)
                
                # Assign sequence based on the category
                if category_id == 1:  # Bedrooms
                    sequence = random.randint(1000, 2000)
                elif category_id == 7:  # Living Room
                    sequence = random.randint(2001, 3000)
                elif category_id == 8:  # Office Furniture
                    sequence = random.randint(3001, 4000)
                else:
                    sequence = random.randint(9000, 10000)  # Default sequence for other categories

                # Log the product and its sequence
                _logger.info(f"sort_products for {record.id}: {record.name}, {sequence}")
                
                # Update the product's website sequence
                record.website_sequence = sequence
            else:
                _logger.warning(f"does not have any public category assigned. Product {record.id} ({record.name}) ")


    def regenerate_image(self):
        for record in self:  # Loop through the records
            record.image_1920 = record.image_1920  # Re-assign to regenerate thumbnails
            
        _logger.info(f"product images processed.")