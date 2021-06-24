from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrderItem(models.Model):
    _inherit = 'sale.order.line'

    tax_ids = fields.Many2many('sale.order.line.tax_id', string="단기/세금")
    add_text = fields.Html(string='Text')




