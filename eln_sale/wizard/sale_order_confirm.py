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

from openerp.osv import orm
from openerp import _


class sale_order_confirm(orm.TransientModel):
    """
    This wizard will confirm the all the selected draft sales orders
    """

    _name = "sale.order.confirm"


    def sale_order_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data_sale = self.pool.get('sale.order').read(cr, uid, context['active_ids'], ['state', 'order_line'], context=context)

        for record in data_sale:
            if record['state'] not in ('draft',):
                raise orm.except_orm(_('Warning'), _("Selected Sale(s) cannot be confirmed as they are not in 'Draft' state!"))
            if not record['order_line']:
                raise orm.except_orm(_('Warning'), _("You cannot confirm a sale order which has no line."))
        for record in data_sale:
            self.pool.get('sale.order').signal_workflow(cr, uid, [record['id']], 'draft_to_risk')
            #wf_service.trg_validate(uid, 'sale.order', record['id'], 'order_confirm', cr)
        return {'type': 'ir.actions.act_window_close'}
