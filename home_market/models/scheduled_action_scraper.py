from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ScheduledActionScraper(models.Model):
    _inherit = 'ir.cron'
    _inherit = 'product.category.url'

    @api.model
    def action_run_all_scraper(self):
        _logger.info("Starting the scraper...")
        # Fetch records based on your criteria
        records = self.env['product.category.url'].search([], order="category_id asc")
        
        for record in records:
            self._run_scraper_for_record(record)
        _logger.info("Scraper completed successfully.")
