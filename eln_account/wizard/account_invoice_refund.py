# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, _, exceptions, models, fields

class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.model
    def _get_journal(self):
        res = super(AccountInvoiceRefund, self)._get_journal()
        active_id = self.env.context.get('active_id', False)
        invoice_id = self.env['account.invoice'].browse(active_id)
        if res and 'simplifi' in invoice_id.journal_id.name.lower():
            aj_obj = self.env['account.journal']
            journal_id = aj_obj.browse(res)
            domain = [
                ('type', '=', journal_id.type),
                ('company_id', '=', journal_id.company_id.id),
                ('name', 'ilike', 'simplifi'),
            ]
            new_journal_id = aj_obj.search(domain, limit=1)
            if not new_journal_id:
                raise exceptions.Warning(_("Warning!"), _("A valid journal was not found for simplified invoices."))
            res = new_journal_id.id
        return res

    journal_id = fields.Many2one(default=_get_journal)
