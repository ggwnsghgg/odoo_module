from odoo import models, fields, api

class Zooanimaltype(models.Model):
    _name = 'zoo.animal_type'
    _description = 'Animal type'

    name = fields.Char(string='이름', required=True)
    animal_year = fields.Date(string="동물원 입양일자")
    animal_type = fields.Char(string='동물의 타입')
    animal_sex = fields.Selection([
        ('man', '남'),
        ('woman', '여')], string="성별")
    animal_image = fields.Binary(string="동물 이미지")
    animal_tag = fields.Html(string="특이사항")

