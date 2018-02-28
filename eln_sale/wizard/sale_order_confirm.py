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

from openerp import models, api, exceptions, _


class SaleOrderConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft sales orders
    """
    _name = "sale.order.confirm"

    @api.multi 
    def sale_order_confirm(self):
        data_sale = self.env['sale.order'].browse(self._context['active_ids'])
        for record in data_sale:
            if record.state != 'draft':
                raise exceptions.Warning(_('Warning'), _("Selected Sale(s) cannot be confirmed as they are not in 'Draft' state!"))
            if not record.order_line:
                raise exceptions.Warning(_('Warning'), _("You cannot confirm a sale order which has no line."))
        for record in data_sale:
            record.signal_workflow('draft_to_risk')
