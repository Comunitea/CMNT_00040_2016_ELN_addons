# -*- coding: utf-8 -*-
# Copyright 2024 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    send_invoice_method = fields.Selection(
        string='Send by',
        related='partner_id.commercial_partner_id.send_invoice_method',
        readonly=True)
