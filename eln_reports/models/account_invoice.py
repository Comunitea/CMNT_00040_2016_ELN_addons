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


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tax_str = fields.Char('Taxes', compute='_get_tax_str', store=True)

    @api.multi
    @api.depends('invoice_line_tax_id.name')
    def _get_tax_str(self):
        for line in self:
            line.tax_str = ', '.join([x.name.split('%')[0].split(' ')[-1] for x in line.invoice_line_tax_id if x.name])
