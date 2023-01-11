# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _compute_dua_invoice(self):
        for invoice in self:
            if invoice.fiscal_position.name == u'Importación con DUA' and \
                    invoice.tax_line.\
                    filtered(lambda x: x.tax_code_id.code in
                             ['DIBAC5', 'DIBAC0']):
                invoice.sii_dua_invoice = True
            else:
                super(AccountInvoice, invoice)._compute_dua_invoice()
