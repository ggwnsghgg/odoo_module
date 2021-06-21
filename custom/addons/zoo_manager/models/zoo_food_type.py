from odoo import models, fields, api

class Zoofoodtype(models.Model):
    _name = 'zoo.food_type'
    _description = 'food type'

    name = fields.Char('Food Type', required=True)
    sequence = fields.Float('Sequence')

