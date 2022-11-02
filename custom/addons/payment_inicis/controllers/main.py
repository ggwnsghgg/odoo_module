# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint
import werkzeug

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


_logger = logging.getLogger(__name__)


class InicisController(http.Controller):

    _return_url = '/payment/inicis/return'
    _webhook_url = '/payment/inicis/webhook'


    def _get_inipay_subdomain(self):
        inicis = request.env['payment.provider'].search([('state', '=', 'inicis')], limit=1)

        if inicis.state == 'enabled':
            return 'stdpay'
        else:  # test
            return 'stgstdpay'

    @http.route(_return_url, type='http', auth='public', methods=['GET'] , csrf=False)
    def inipay_return(self, **post):
        """ INIpay."""
        _logger.info('INIpay: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'inicis')
        return werkzeug.utils.redirect('/payment/process')

    @http.route(_webhook_url, type='http', auth='public', methods=['POST'], csrf=False)
    def inipay_close(self, **post):
        return """<script language="javascript" type="text/javascript" 
                        src="https://%s.inicis.com/stdjs/INIStdPay_close.js" charset="UTF-8"></script>""" % self._get_inipay_subdomain()
