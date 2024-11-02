from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class product_public_category(models.Model):
    _inherit = 'product.public.category'
    is_publish = fields.Boolean(string='is Publish', store=True ,default=True)
    description = fields.Char(string='Description', store=True )
