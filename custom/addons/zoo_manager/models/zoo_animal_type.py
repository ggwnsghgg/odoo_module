from odoo import models, fields, api

class Zooanimaltype(models.Model):
    _name = 'zoo.animal_type'
    _description = 'Animal type'

    name = fields.Char('Animal Type', required=True)

