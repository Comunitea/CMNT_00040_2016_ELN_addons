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
from openerp import api, _, exceptions, models, fields

class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.model
    def view_init(self, fields_list):
        active_ids = self.env.context.get('active_ids', [])
        invalid_ids = self.env['stock.picking'].search([('id', 'in', active_ids), ('state', '!=', 'done')])
        if invalid_ids:
            raise exceptions.Warning(_("Warning!"), _("At least one of the selected picking lists are not in 'done' state and cannot be invoiced."))
        return super(StockInvoiceOnshipping, self).view_init(fields_list)
