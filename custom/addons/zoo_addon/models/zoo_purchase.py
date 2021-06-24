from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)






class ZooBooleanCreate(models.Model):
    _inherit = 'purchase.order'

    # sale_move_id = fields.Many2one('sale.order', string="Sale Move")
    # sale_product_id = fields.Many2one('product.product', string="Product")
    #
    zoo_boolean = fields.Boolean(default=False, string='Zoo')
    zoo_manger_id = fields.Many2one('zoo.manger', string="Zoo Manger")
    zoo_food_table_id = fields.Many2one('zoo.food_table', string="Zoo Food Table")
    zoo_food_ids_id = fields.Many2one('zoo.food_ids', string="Zoo Food Ids")
    zoo_food_name_id = fields.Many2one('zoo.food_name', stirng="Zoo Food Name")



    # purchase.order에서 선택된 음식 이름을 기반으로 food_table로 이동
    # def call_zoo_manger(self):
    #     view_id = self.env.ref('zoo_manager.zoo_manger_food_quantity_view_tree').id
    #     _logger.debug('----------- food name ---------- %s', self.zoo_manger_id.food_ids)
    #     line = [self.zoo_manger_id.food_ids.ids]
    #
    #     _logger.debug('----------- food name ---------- %s', line)
    #
    #     return {
    #             'name': 'Zoo Food Table',
    #             'view_type': 'list',
    #             'view_mode': 'list, tree',
    #             'views': [(view_id, 'list')],
    #             'res_model': 'zoo.food_quantity',
    #             'domain': [('id', 'in', self.zoo_manger_id.food_ids.ids)],
    #             'view_id': view_id,
    #             'type': 'ir.actions.act_window',
    #
    #             }


    # manger로 이동
        # view_id = self.env.ref('zoo_manager.zoo_manger_view_form').id
        #
        # return {
        #     'name': 'Zoo Manger',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'views': [(view_id, 'form')],
        #     'res_model': 'zoo.manger',
        #     'view_id': view_id,
        #     'type': 'ir.actions.act_window',
        #     'res_id': self.zoo_manger_id.id,
        # }

#
# class ZooBooleanCreateTaxid(models.Model):
#     _inherit = 'purchase.order.line'
#
#     zoo_test = fields.Boolean(default=False, string='Zoo')
#     zoo_boolean = fields.Boolean(default=False, string='Zoo')
#



# # _inherit 을 남발하다가 필드를 생성해버려서 지워버리면 오류가 뜨기에 일단 보류
# class ZooBooleanCreateTaxid(models.Model):
#     _inherit = 'stock.picking'
#
#     zoo_boolean = fields.Boolean(default=False, string='Zoo')



# class ZooBooleanCreateTaxid(models.Model):
#     _inherit = 'stock.move'
#
#     zoo_boolean = fields.Boolean(default=False, string='Zoo')





 # sales에 manger 상속받아서 버튼에 기능을 넣어 sales로 데이터 전송할 수 있게 제작
class Zooanimalmanager(models.Model):

    _inherit = 'zoo.manger'
    purchase_move = fields.Boolean(default=True)
    purchase_move_id = fields.Many2one('purchase.order', string="Purchase Order")
    zoo_food_table_id = fields.Many2one('zoo.food_table')



    def purchase_create(self):

        order_line_vals = []
        partner_ids = self.partner_id


        for food in self.food_ids:
            food_name = food.food_table_id.food_name_id.name
            food_weight = food.food_weight
            food_price_ids = food.food_price_ids


            product = self.env['product.product'].search([('name','=',food_name)],limit = 1)
            if not product :
                product = self.env['product.product'].create({'name': food_name, })

            order_line_vals.append([0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': food.food_weight,
                'price_unit': food.food_price_ids,

            }])

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'order_line': order_line_vals,
            'zoo_manger_id': self.id
        })
        _logger.debug(' -------------------------------------------------------- %s', self.partner_id)
        self.update({
                    'purchase_move': True,
                    'purchase_move': purchase_order.id
                    })

    def call_sale_order(self):
        _logger.debug('---------- sale_product_id -------- ')
        view_id = self.env.ref('purchase.purchase_order_form').id

        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'purchase.order',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.purchase_move_id.id,
        }











