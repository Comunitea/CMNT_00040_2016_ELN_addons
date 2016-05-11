# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class AccountAnalyticJournal(models.Model):

    _inherit = 'account.analytic.journal'

    analytic_cost_journal = fields.Many2one('account.analytic.journal',
                                            'Analytic cost journal')


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.type not in ('out_invoice', 'out_refund'):
                continue
            company_currency = self.company_id.currency_id
            currency = self.currency_id.with_context(date=self.date_invoice)
            sign = -1 if self.type == 'out_invoice' else 1
            for analytic_move in invoice.mapped(
                    'move_id.line_id.analytic_lines'):
                if not analytic_move.product_id:
                    continue
                product = analytic_move.product_id
                account = product.property_account_expense or product.categ_id.property_account_expense_categ
                amount = currency.compute(
                    product.standard_price *
                    analytic_move.unit_amount, company_currency) * sign
                analytic_move.copy(
                    {'journal_id':
                     analytic_move.journal_id.analytic_cost_journal.id,
                     'general_account_id': account.id,
                     'amount': amount})
        return super(AccountInvoice, self).invoice_validate()
