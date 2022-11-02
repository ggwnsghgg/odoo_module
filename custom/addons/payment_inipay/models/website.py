# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    inipay_acquirer_id = fields.Many2one('payment.acquirer', compute='_compute_inipay_acquirer_id')
    inipay_state = fields.Selection(related='inipay_acquirer_id.state')

    def _compute_inipay_acquirer_id(self):
        for website in self:
            website.inipay_acquirer_id = self.env['payment.acquirer'].search([('provider', '=', 'inipay')], limit=1)
