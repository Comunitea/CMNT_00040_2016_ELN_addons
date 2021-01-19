# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    commercial_route_id = fields.Many2one(
        string='Commercial route',
        comodel_name='commercial.route',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="[('user_id', '=', user_id)]")


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super(AccountInvoiceRefund, self).compute_refund(mode)
        new_ids = res['domain'][1][2]
        for invoice in self.env['account.invoice'].browse(new_ids):
            orig = invoice.origin_invoices_ids
            if not orig:
                continue
            invoice.commercial_route_id = orig[0].commercial_route_id
        return res
