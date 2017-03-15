# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2017 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp import models, api, fields, exceptions, _


class ModifyInvoiceAnalyticAccountWzd(models.TransientModel):
    _name = 'modify.invoice.analytic.account.wzd'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Account analytic')

    @api.model
    def default_get(self, fields):
        res = super(ModifyInvoiceAnalyticAccountWzd, self).default_get(fields)
        analytic_account_id = False
        if self._context.get('active_id', False):
            model = self._context.get('active_model')
            analytic_account_id = \
                self.env[model].browse(self._context['active_id']).\
                invoice_line[0].account_analytic_id
        res.update(analytic_account_id=analytic_account_id.id
                   if analytic_account_id else False)
        return res

    @api.multi
    def action_modify_invoice_analytic(self):
        self.ensure_one()
        res = {}
        if not self._context.get('active_id', False):
            return res
        for invoice in self.env['account.invoice'].browse(self._context['active_ids']):
            if invoice.state not in ('open', 'paid') or not invoice.move_id:
                raise exceptions.Warning(_('Invalid Action!'), 
                    _('The analytic account can not be modified using this wizard, because the invoice is not validated.'))

            # Establecemos nueva analítica en la factura
            for line in invoice.invoice_line:
                line.account_analytic_id = self.analytic_account_id

            # Establecemos nueva analítica en los apuntes generados por la factura
            # Para ello suponemos que todos los apuntes con producto establecido corresponden a una linea de factura
            # Además primero vemos cuantos apuntes se generarían al crear el asiento con analítica, para
            # despues ver cuales de los generados se corresponden con ellos, y así establecer la cuenta analítica
            # solo en esos apuntes
            lines_with_analytic = [ail for ail in self.env['account.invoice.line'].move_line_get(invoice.id)
                                    if ail.get('account_analytic_id', False)]
            for line_id in invoice.move_id.line_id.filtered(lambda x: x.product_id):
                if self.analytic_account_id:
                    key_account = (line_id.product_id.id,
                                   line_id.product_uom_id and line_id.product_uom_id.id,
                                   line_id.quantity or 0.0,
                                   line_id.credit or line_id.debit or 0.0,
                                   line_id.tax_code_id and line_id.tax_code_id.id)
                    for line_with_analytic in lines_with_analytic:
                        key_invoice = (line_with_analytic['product_id'],
                                       line_with_analytic['uos_id'],
                                       line_with_analytic['quantity'],
                                       line_with_analytic['price'],
                                       line_with_analytic['tax_code_id'])
                        if key_invoice == key_account:
                            line_id.analytic_account_id = self.analytic_account_id
                            self.pool.get('account.move.line').create_analytic_lines(self._cr, self._uid, [line_id.id], self._context)
                            lines_with_analytic.remove(line_with_analytic)
                            break
                else:
                    line_id.analytic_account_id = False
                    self.pool.get('account.move.line').create_analytic_lines(self._cr, self._uid, [line_id.id], self._context)
        return res

