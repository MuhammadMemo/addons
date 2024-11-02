

from odoo import models

class ProductCategory(models.Model):
    _inherit = 'product.public.category'

    def get_categories(self):
        categories = self.search([])
        data = [{
            'id': category.id,
            'name': category.name,
            'image': category.image_1920 and f'/web/image/product.public.category/{category.id}/image_1920',
        } for category in categories]
        return data
