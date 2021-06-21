from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)



class foodquantity(models.Model):
    _name = 'zoo.food_quantity'
    _description = 'food quantity'

    manger_id = fields.Many2one('zoo.manger')

    animal_type_id = fields.Many2one('zoo.animal_type',
                                     string="Animal Type",
                                     related="manger_id.animal_type_id",
                                     store=False)

    food_table_id = fields.Many2one('zoo.food_table',
                                    string ="Food",
                                    domain="[('animal_type_id', '=', animal_type_id)]")

    food_price_ids = fields.Float(related='food_table_id.food_price_id')
    food_weight = fields.Float(string='Food Weight')
    currency_id = fields.Many2one("res.currency", string="Currency")
    food_subtotal = fields.Monetary(string="Food Subtotal", compute='_compute_total')
    # food_subtotal = fields.Float(string="Food Subtotal", compute='_compute_total')

    @api.depends('food_subtotal')
    def _compute_total(self):
        for move in self:
            total = 0.0
            total += move.food_subtotal + move.food_price_ids * move.food_weight  # why is there a discount in a field named amount_undiscounted ??
            move.food_subtotal = total



