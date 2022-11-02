# Part of Odoo. See LICENSE file for full copyright and licensing details.

from hashlib import new as hashnew
import hashlib
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare, float_repr, float_round



class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('inicis', "Inicis")], ondelete={'inicis': 'set default'}
    )
    inicis_merchant_id = fields.Char(string="Merchant ID", required_if_provider='inicis', groups='base.group_user')
    # inicis_merchant_key = fields.Char(string="Merchant Hash Key", required_if_provider='inicis', groups='base.group_user')
    # inicis_merchant_iv = fields.Char(string="Merchant ID IV", required_if_provider='inicis', groups='base.group_user')
    inicis_sign_key= fields.Char(string="Sign Key", required_if_provider='inicis', groups='base.group_user')

    def _get_signature(self, oid, price, timestamp):
        sig_data = {
            'oid': oid,
            'price': price,
            'timestamp': timestamp,
        }
        sig_data_string = '&'.join(['{}={}'.format(k, v) for k, v in sig_data.items()])
        return hashlib.sha256(sig_data_string.encode('utf-8')).hexdigest()

    def _get_mKey(self):
        return hashlib.sha256(self.inicis_sign_key.encode('utf-8')).hexdigest()

    def inicis_get_form_action_url(self):
        return 'https://stdpay.inicis.com/stdjs/INIStdPay.js'

    def inicis_form_generate_values(self, values):
        base_url = self.get_base_url()
        tx = self.env['payment.transaction'].search([('reference', '=', values.get('reference'))])
        so = self.env['sale.order'].browse(tx.sale_order_ids[0].id)
        oid = values.get('reference')
        timestamp = tx._get_timestamp()
        currency = 'WON' if values.get('currency').name == 'KRW' else values.get('currency').name
        price = float_repr(float_round(values.get('amount'), 2) * 100, 0) if values.get(
            'currency').name == 'USD' else float_repr(values.get('amount'), 0)
        inicis_values = dict(
            version='1.0',
            mid=self.inicis_mid,
            oid=oid,
            goodname=so.order_line[0].display_name if so and so.order_line else '',
            quantity=len(so.order_line),
            price=price,
            tax='0',
            taxfree='0',
            currency=currency,
            buyername=values.get('partner_name'),
            buyertel=values.get('partner_phone'),
            buyeremail=values.get('partner_email'),
            timestamp=timestamp,
            signature=self._get_signature(oid, price, timestamp),
            returnUrl=urls.url_join(base_url, '/payment/inipay/return'),
            mKey=self._get_mKey(),
            closeUrl=urls.url_join(base_url, '/payment/inipay/close'),
            popupUrl=urls.url_join(base_url, '/payment/inipay/popup'),
        )
        return inicis_values
