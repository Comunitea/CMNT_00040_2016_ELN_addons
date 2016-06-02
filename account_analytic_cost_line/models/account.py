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
        t_uom = self.env['product.uom']
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
                from_unit = analytic_move.product_uom_id.id
                product_unit = analytic_move.product_id.uom_id.id
                uom_qty = analytic_move.unit_amount
                if from_unit != product_unit:
                    uom_qty = t_uom._compute_qty(from_unit,
                                                 analytic_move.unit_amount,
                                                 product_unit)
                amount = currency.compute(
                    analytic_move.product_id.standard_price *
                    uom_qty, company_currency) * sign
                analytic_move.copy(
                    {'journal_id':
                     analytic_move.journal_id.analytic_cost_journal.id,
                     'amount': amount})
        return super(AccountInvoice, self).invoice_validate()


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    @api.multi
    def fix(self):
        journal_id = self[0].journal_id.id
        lines = self.search([('journal_id', '=', journal_id)])
        t_uom = self.env['product.uom']
        for l in lines:
            if l.product_uom_id.id != l.product_id.uom_id:
                invoice_id = False
                for l2 in l.move_id.analytic_lines:
                    if l2.invoice_id:
                        invoice_id = l2.invoice_id
                if not invoice_id:
                    continue
                company_currency = invoice_id.company_id.currency_id
                currency = invoice_id.currency_id.\
                    with_context(date=invoice_id.date_invoice)
                sign = -1 if invoice_id.type == 'out_invoice' else 1
                from_unit = l.product_uom_id.id
                product_unit = l.product_id.uom_id.id
                uom_qty = l.unit_amount
                uom_qty = t_uom._compute_qty(from_unit,
                                             l.unit_amount,
                                             product_unit)
                amount = currency.compute(
                    l.product_id.standard_price *
                    uom_qty, company_currency) * sign
                l.amount = amount
        return
