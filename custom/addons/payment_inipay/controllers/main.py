# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class INIpayController(http.Controller):

    def _get_inipay_subdomain(self):
        inipay = request.env['payment.acquirer'].search([('provider', '=', 'inipay')], limit=1)
        if inipay.state == 'enabled':
            return 'stdpay'
        else:
            return 'stgstdpay'

    @http.route(['/payment/inipay/return'], type='http', auth='public', csrf=False)
    def inipay_return(self, **post):
        """ INIpay."""
        _logger.info('INIpay: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'inipay')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/inipay/close'], type='http',auth='public', csrf=False)
    def inipay_close(self, **post):
        return """<script language="javascript" type="text/javascript" 
                        src="https://%s.inicis.com/stdjs/INIStdPay_close.js" charset="UTF-8"></script>""" % self._get_inipay_subdomain()


    @http.route(['/payment/inipay/popup'], type='http', auth='public', csrf=False)
    def inipay_popup(self, **post):
        return """<script language="javascript" type="text/javascript" 
                        src="https://%s.inicis.com/stdjs/INIStdPay_popup.js" charset="UTF-8"></script>""" % self._get_inipay_subdomain()
