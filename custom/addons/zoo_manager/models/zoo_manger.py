from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from openerp import tools

import logging
_logger = logging.getLogger(__name__)



# 동물 타입
class Zooanimalmanager(models.Model):
    _name = 'zoo.manger'
    _description = 'food manager'

    name = fields.Char(string='Animal Name')
    animal_image = fields.Binary("Animal Image")
    animal_type_id = fields.Many2one('zoo.animal_type', string="Animal Type")
    animal_age = fields.Integer('Animal Age', default=1)
    animal_year = fields.Date('Animal Adopt')
    food_ids = fields.One2many('zoo.food_quantity', 'manger_id', string='Food Name')
    zoo_food_table_id = fields.Many2one('zoo.food_table')
    partner_id = fields.Many2one('res.partner', string="Partner ID")
    time_for_food = fields.Datetime('Time For Food')


class ConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    food_quantity = fields.Many2many('zoo.food_quantity', string='Food type')





