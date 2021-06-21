from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Zoofoodname(models.Model):
    _name = 'zoo.food_name'
    _description = 'food name'

    name = fields.Char('Zoo Food Name', required=True)
    food_type_id = fields.Many2one('zoo.food_type', string='Food Type')
    food_price = fields.Float(string='Food Price')


