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

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        # Se establece el domain del campo journal_id para impedir elegir un diario de un tipo no permitido
        res = super(AccountInvoiceRefund, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        type = self._context.get('type', 'out_invoice')
        company_id = self.env.user.company_id.id
        journal_type = (type == 'out_invoice') and 'sale_refund' or \
                       (type == 'out_refund') and 'sale' or \
                       (type == 'in_invoice') and 'purchase_refund' or \
                       (type == 'in_refund') and 'purchase'
        for field in res['fields']:
            if field == 'journal_id':
                res['fields'][field]['domain'] = [('type', '=', journal_type), ('company_id', 'child_of', [company_id])]
        return res
