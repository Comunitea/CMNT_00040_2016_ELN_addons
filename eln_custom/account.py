# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
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
from openerp import models, fields


class AccountAnalyticPlanInstance(models.Model):

    _inherit = 'account.analytic.plan.instance'

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'
    invoice_type = fields.Selection(
        [('out_invoice','Customer Invoice'),
         ('in_invoice','Supplier Invoice'),
         ('out_refund','Customer Refund'),
         ('in_refund','Supplier Refund')],
         related='invoice_id.type', readonly=True)
