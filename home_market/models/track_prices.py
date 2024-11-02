from odoo import models, fields

class ProductTrackprices(models.Model):
    _name = 'product.track.prices'
    _description = 'Product Track prices'

    category_id = fields.Many2one('product.public.category', string='Category', required=True)
    tag_id = fields.Many2one('product.tag', string='Tag')
    product_id = fields.Many2one('product.template', string='Product')
    
    track_prices = fields.Float(string='Track Prices', required=True)
    track_compare_prices = fields.Float(string='Track Compare Price', required=True)
    track_discount = fields.Float(string='Track Discount', required=True)
    track_date = fields.Date(string='Track Date', required=True)
    updated_price = fields.Float(string='Updated Price')
    updated_compare_price = fields.Float(string='Updated Compare Price')
    updated_discount = fields.Float(string='Updated Discount')
    
    difference_price = fields.Float(string='Difference Price')
    difference_compare_price = fields.Float(string='Difference Compare Price')
    difference_discount = fields.Float(string='Difference Discount')
