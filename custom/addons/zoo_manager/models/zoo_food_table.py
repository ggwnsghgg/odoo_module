from odoo import models, fields, api
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


# 먹이 종류 와 이름
class Zoofoodtable(models.Model):
    _name = 'zoo.food_table'
    _description = 'food table'

    animal_type_id = fields.Many2one('zoo.animal_type', string = 'Animal type',required=True)
    food_type_id = fields.Many2one('zoo.food_type', string = 'Food Type',required=True)
    food_name_id = fields.Many2one('zoo.food_name', domain="[('food_type_id', '=', food_type_id)]")
    food_price_id = fields.Float(related='food_name_id.food_price')

    def name_get(self):
        res = []
        for record in self :
            if record.food_name_id :
               res.append((record.id, record.food_name_id.name))
        return res


