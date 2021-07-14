# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.purchase.order'
    _description = 'Merge Purchase Order'

    merge_type = \
        fields.Selection([
            ('create_new',
             'New Create Merge !!'),
            ('create_new_order',
             '테스트 중인 문구입니다 선택하지마세요..')],
            default='create_new')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')
    default_code = fields.Char('Default Code')

    def merge_orders(self):
        purchase_orders = self.env['purchase.order'].browse(
            self._context.get('active_ids', []))

        if len(self._context.get('active_ids', [])) < 2:
            raise UserError(
                _('Please select atleast two purchase orders to perform '
                    'the Merge Operation.'))
        if any(order.state != 'draft' for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders which are in RFQ state '
                  'to perform the Merge Operation.'))


        if self.merge_type == 'create_new':
            group_order = []
            partner_ref = []
            currency_order = []


            for order in purchase_orders:
                check = 0
                partner_ref.append(order.name)
                partner_ref_line = ",".join(partner_ref)

                # partner_id와 currency_id가 같을때
                for gorder in group_order:
                    if gorder['partner_id'] == order.partner_id.id and \
                       gorder['currency_id'] == order.currency_id.id:
                        for line in order.order_line:
                            gorder['order_line'].append({
                                                         'name': line.name,
                                                         'product_id': line.product_id.id,
                                                         'product_qty': line.product_qty,
                                                         'price_unit': line.price_unit,
                                                         'taxes_id': line.taxes_id,
                                                         'currency_id': line.currency_id.id,
                                                        })
                            check = 1

                # group_order 생성하는 부분
                if check == 0:
                    aline = []
                    for line in order.order_line:
                        aline.append({'id': line.id,
                                      'name': line.name,
                                      'product_id': line.product_id.id,
                                      'product_qty': line.product_qty,
                                      'price_unit': line.price_unit,
                                      'taxes_id': line.taxes_id,
                                      'currency_id': line.currency_id.id})

                    group_order.append({'id': order.id,
                                        'partner_id': order.partner_id.id,
                                        'currency_id': order.currency_id.id,
                                        'order_line': aline,
                                        })

            for gorder in group_order:
                newline = []
                order_line = []
                for line in gorder['order_line']:
                    check = 0
                    for eline in newline:
                        if line['product_id'] == eline['product_id'] and line['price_unit'] == eline['price_unit']:
                            eline['product_qty'] = eline['product_qty'] + line['product_qty']
                            check = 2

                    if check == 0:
                        newline.append({
                                      'name': line['name'],
                                      'product_id': line['product_id'],
                                      'product_qty': line['product_qty'],
                                      'price_unit': line['price_unit'],
                                      'taxes_id': line['taxes_id'],
                                      'currency_id': line['currency_id'],
                                      })
                gorder['new_order_line'] = newline

            # # 데이터 확인하는 과정
            for gorder in group_order:
                _logger.debug('----------------  T e s t 1    ---------------- %s', gorder['partner_id'])
                for line in gorder['new_order_line']:
                    _logger.debug('----------------  T e s t 2    ---------------- %s', gorder)

            # # partner_id 와 화페 단위가 같으면 생성되는 부분
            if check == 2:
                for gorder in group_order:
                    po = self.env['purchase.order'].create({
                        'partner_id': gorder['partner_id'],
                        'partner_ref': partner_ref_line,
                        'currency_id': gorder['currency_id'],
                        'order_line': [(0, 0, {
                            'name': x['name'],
                            'currency_id': x['currency_id'],
                            'product_id': x['product_id'],
                            'product_qty': x['product_qty'],
                            'price_unit': x['price_unit'],
                        }) for x in gorder['new_order_line']],
                    })

        # Status 변경하는 부분
        for order in purchase_orders:
            order.button_cancel()



        # Merge 할때 order_id가 낮은 값을 기준으로 합치게 하는 부분
        if self.merge_type == 'create_new_order':
            group_order = []
            partner_ref = []
            for order in purchase_orders:
                check = 0
                partner_ref.append(order.name)
                partner_ref_line = ",".join(partner_ref)

                for gorder in group_order:
                    if gorder['partner_id'] == order.partner_id.id and \
                        gorder['currency_id'] == order.currency_id.id:
                        for line in order.order_line:
                            gorder['order_line'].append({
                                'name': line.name,
                                'product_id': line.product_id.id,
                                'product_qty': line.product_qty,
                                'price_unit': line.price_unit,
                                'taxes_id': line.taxes_id})
                            check = 1

                if check == 0:
                    aline = []
                    for line in order.order_line:
                        aline.append({'id': line.id,
                                        'name': line.name,
                                        'product_id': line.product_id.id,
                                        'product_qty': line.product_qty,
                                        'price_unit': line.price_unit,
                                        'taxes_id': line.taxes_id,
                                        'price_subtotal': line.price_subtotal})

                        group_order.append({'id': order.id,
                                            'name': order.name,
                                            'partner_id': order.partner_id.id,
                                            'currency_id': order.currency_id.id,
                                            'order_line': aline,
                                            })
                        _logger.debug('---------------- group_order   ---------------- %s', group_order)
            for gorder in group_order:
                newline = []
                for line in gorder['order_line']:
                    check = 0
                    for eline in newline:
                        if line['product_id'] == eline['product_id'] and line['price_unit'] == eline['price_unit']:
                            eline['product_qty'] = eline['product_qty'] + line['product_qty']
                            check = 2

                    if check == 0:
                        newline.append({
                            'id': line['id'],
                            'name': line['name'],
                            'product_id': line['product_id'],
                            'product_qty': line['product_qty'],
                            'price_unit': line['price_unit'],
                            'taxes_id': line['taxes_id'],
                        })
                gorder['new_order_line'] = newline


            for gorder in group_order:
                _logger.debug('---------------- Merge   ---------------- %s', gorder['name'])
            #
            # if check == 2:
            #     for gorder in group_order:
            #         po = self.env['purchase.order'].create({
            #             'name': gorder['name'],
            #             'partner_id': gorder['partner_id'],
            #             'partner_ref': partner_ref_line,
            #             'order_line': [(0, 0, {
            #                 'name': x['name'],
            #                 'product_id': x['product_id'],
            #                 'product_qty': x['product_qty'],
            #                 'price_unit': x['price_unit'],
            #             }) for x in gorder['new_order_line']],
            #         })

        # for order in purchase_orders:
        #     order.button_cancel()







