# -*- coding: utf-8 -*-

import logging
import pprint
import time
import datetime
import hashlib
import requests
import socket
import urllib
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_repr, float_round
from odoo.addons.payment.models.payment_acquirer import ValidationError


_logger = logging.getLogger(__name__)


class PaymentAcquirerINIpay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('inipay', 'INIpay')])
    inipay_mid = fields.Char(string="Merchant ID", required_if_provider='inipay', groups='base.group_user')
    inipay_mid_key = fields.Char(string="Merchant ID Key", required_if_provider='inipay', groups='base.group_user')
    inipay_mid_iv = fields.Char(string="Merchant ID IV", required_if_provider='inipay', groups='base.group_user')
    inipay_sign_key = fields.Char(string="Sign Key", required_if_provider='inipay', groups='base.group_user')

    def _get_signature(self, oid, price, timestamp):
        sig_data = {
            'oid': oid,
            'price': price,
            'timestamp': timestamp,
        }
        sig_data_string = '&'.join(['{}={}'.format(k, v) for k, v in sig_data.items()])
        return hashlib.sha256(sig_data_string.encode('utf-8')).hexdigest()

    def _get_mKey(self):
        return hashlib.sha256(self.inipay_sign_key.encode('utf-8')).hexdigest()

    def inipay_get_form_action_url(self):
        return 'https://mobile.inicis.com/smart/payment/'

    def inipay_form_generate_values(self, values):
        base_url = self.get_base_url()
        tx = self.env['payment.transaction'].search([('reference', '=', values.get('reference'))])
        so = self.env['sale.order'].browse(tx.sale_order_ids[0].id)
        oid = values.get('reference')
        timestamp = tx._get_timestamp()
        currency = 'WON' if values.get('currency').name == 'KRW' else values.get('currency').name
        price = float_repr(float_round(values.get('amount'), 2) * 100, 0) if values.get('currency').name == 'USD' else float_repr(values.get('amount'), 0)
        inipay_values = dict(
            version='1.0',
            mid=self.inipay_mid,
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
            inipayment='CARD',
            nextUrl=urls.url_join(base_url, '/payment/inipay/return'),
        )
        return inipay_values

class PaymentTransactionINIpay(models.Model):
    _inherit = 'payment.transaction'

    def _get_timestamp(self):
        d = datetime.datetime.now()
        t = time.mktime(d.timetuple())
        return '%d%d' % (t, d.microsecond / 1000)

    def _get_signature(self, authToken, timestamp):
        sig_data = {
            'authToken': authToken,
            'timestamp': timestamp,
        }
        sig_data_string = '&'.join(['{}={}'.format(k, v) for k, v in sig_data.items()])
        return hashlib.sha256(sig_data_string.encode('utf-8')).hexdigest()

    def form_feedback(self, data, acquirer_name):
        if acquirer_name == 'inipay':
            reference, resultCode, resultMsg = data.get('orderNumber') or '', data.get('resultCode') or data.get('P_STATUS'), data.get('resultMsg') or data.get('P_RMESG1')
            if not (resultCode == "0000" or resultCode == "00"):
                raise ValidationError(_('INIpay: received data for reference %s; %s') % (reference, resultMsg))

            if resultCode == "0000":
                timestamp = self._get_timestamp()
                authToken = data.get('authToken')
                authUrl = data.get('authUrl')

                values = dict(
                    mid=data.get('mid'),
                    authToken=authToken,
                    timestamp=timestamp,
                    signature=self._get_signature(authToken, timestamp),
                    charset='UTF-8',
                    format='JSON',
                )
                try:
                    response = requests.post(authUrl, data=values)
                    _logger.info('response (HTTP status %s):\n%s', response.status_code, response.text)
                    _logger.info('response data:\n%s', response.json())
                    data.update(response.json())
                except Exception as e:
                    raise e
            elif resultCode == "00":
                tid = data.get('P_TID')
                reqUrl = data.get('P_REQ_URL')
                _logger.debug('\ntid: %s\nreqUrl: %s', tid, reqUrl)
                acquirer = self.env['payment.acquirer'].search([('provider', '=', 'inipay')], limit=1)
                values = dict(
                    P_TID=tid,
                    P_MID=acquirer.inipay_mid,
                )
                try:
                    response = requests.post(reqUrl, data=values)
                    res_dict = dict(urllib.parse.parse_qsl(response.text))
                    _logger.info('response (HTTP status %s):\n%s', response.status_code, response.text)
                    _logger.info('response data:\n%s', res_dict)
                    data.update(res_dict)
                except Exception as e:
                    raise e

            _logger.info('INIpay: entering form_feedback with post data %s' % pprint.pformat(data))
        return super(PaymentTransactionINIpay, self).form_feedback(data, acquirer_name)

    def _request_inipay_refund(self, **kwargs):
        d = datetime.datetime.now()
        timestamp = d.strftime('%Y%m%d%H%M%S')
        hostname = request.httprequest.host.split(":")[0]
        server_public_ip = socket.gethostbyname(hostname)
        refund_url = 'https://%s.inicis.com/api/v1/refund' % (
            'iniapi' if self.acquirer_id.state == 'enabled' else 'stginiapi')
        tid = kwargs.get('tid')
        msg = kwargs.get('reason')

        values = dict(
            type='Refund',
            paymethod='Card',
            timestamp=timestamp,
            clientIp=server_public_ip,
            mid=self.acquirer_id.inipay_mid,
            tid=tid
        )

        if not self.acquirer_id.inipay_mid_key:
            raise UserError(_("Please configure the INIpay acquirer's Merchant ID Key."))
        data = self.acquirer_id.inipay_mid_key+''.join([v for k, v in values.items()])
        _logger.info('_request_inipay_refund: data:\n%s', data)
        hashdata = hashlib.sha512(data.encode('utf-8')).hexdigest()
        _logger.info('_request_inipay_refund: hashdata:\n%s', hashdata)
        values = dict(
            values,
            msg=msg,
            hashData=hashdata
        )
        _logger.info('_request_inipay_refund: Sending values to inipay URL, values:\n%s', pprint.pformat(values))
        try:
            response = requests.post(refund_url, data=values)
            _logger.info('response (HTTP status %s):\n%s', response.status_code, response.text)
            _logger.info('response data:\n%s', response.json())
        except Exception as e:
            raise e

        return response.json()

    def inipay_s2s_do_refund(self, **kwargs):
        self.ensure_one()
        result = self._request_inipay_refund(**kwargs)
        return self._inipay_s2s_validate_tree(result)

    def _inipay_s2s_validate_tree(self, tree):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info('INIpay: trying to validate an already validated tx (ref %s)', self.reference)
            return True
        vals = {
            "date": fields.datetime.now(),
        }
        if tree.get('resultCode') == '00':
            _logger.info('Validated INIpay payment for tx %s: set as done' % (self.reference))
            vals.update(state='done')
            self._set_transaction_done()
            self.write(vals)
            self.execute_callback()
            return True
        else:
            error = 'Received unrecognized status for INIpay payment %s, set as error' % (self.reference)
            _logger.info(error)
            vals.update(state='cancel', state_message=error)
            self._set_transaction_cancel()
            return self.write(vals)

    @api.model
    def _inipay_form_get_tx_from_data(self, data):
        """ Given a data dict coming from inipay, verify it and find the related
        transaction record. """
        reference = data.get('orderNumber') or data.get('P_OID')
        if not reference:
            raise ValidationError(_('INIpay: received data with missing reference (%s)') % (reference))

        transaction = self.search([('reference', '=', reference)])
        if not transaction:
            error_msg = (_('INIpay: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (_('INIpay: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)
        return transaction

    def _inipay_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.acquirer_reference and (data.get('tid') or data.get('P_TID')) != self.acquirer_reference:
            invalid_parameters.append(('Reference code', (data.get('tid') or data.get('P_TID')), self.acquirer_reference))
        return invalid_parameters

    def _inipay_form_validate(self, data):
        self.ensure_one()
        res = {
            'acquirer_reference': data.get('tid') or data.get('P_TID') ,
        }

        if data.get('resultCode') == '0000' or data.get('P_STATUS') == '00':
            _logger.info('Validated INIpay payment for tx %s: set as done' % (self.reference))
            res.update(state='done', date=fields.Datetime.now())
            self._set_transaction_done()
            self.write(res)
            self.execute_callback()
            return True
        else:
            error = 'Received unrecognized status for INIpay payment %s, set as error' % (self.reference)
            _logger.info(error)
            res.update(state='cancel', state_message=error)
            self._set_transaction_cancel()
            return self.write(res)
