# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
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
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp import netsvc

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'merged_into_id': fields.many2one('mrp.production', 'Merged into', required=False, readonly=True, help='Production order in which this production order has been merged into.'),
        'merged_from_ids': fields.one2many('mrp.production', 'merged_into_id', 'Merged from', help='List of production orders that have been merged into the current one.'),
    }

    def _do_merge(self, cr, uid, ids, invalid_ids=[], context=None):

        main_obj = self.browse(cr, uid, ids[0], context=context)
        wizard = self.pool.get('change.production.qty')
        product_qty = 0.0
        picking_ids = []
        if ids[0] in invalid_ids:
            invalid_ids.remove(ids[0])

        if main_obj.state not in ['confirmed','ready']:
            raise osv.except_osv(_('Error !'), _('Production order "%s" must be in status "confirmed" or "ready".') % main_obj.name)
        product_qty += main_obj.product_qty

        for production in self.pool.get('mrp.production').browse(cr, uid, invalid_ids, context=None):
            if production.state not in ['confirmed','ready']:
                raise osv.except_osv(_('Error !'), _('Production order "%s" must be in status "confirmed" or "ready".') % production.name)

            if production.product_id != main_obj.product_id:
                raise osv.except_osv(_('Error !'), _('Production order "%s" product is different from the one in the first selected order.') % production.name)
            if production.product_uom != main_obj.product_uom:
                raise osv.except_osv(_('Error !'), _('Production order "%s" UOM is different from the one in the first selected order.') % production.name)

            if production.bom_id != main_obj.bom_id:
                raise osv.except_osv(_('Error !'), _('Production order "%s" BOM is different from the one in the first selected order.') % production.name)

            if production.routing_id != main_obj.routing_id:
                raise osv.except_osv(_('Error !'), _('Production order "%s" routing is different from the one in the first selected order.%s - %s') % (production.name, production.routing_id, main_obj.routing_id) )

            if production.product_uos != main_obj.product_uos:
                raise osv.except_osv(_('Error !'), _('Production order "%s" UOS is different from the one in the first selected order.') % production.name)

            product_qty += production.product_qty
            picking_ids.append( production.picking_id.id )


        self.write(cr, uid, ids, {
            'merged_into_id': main_obj.id,
        }, context)

        workflow = netsvc.LocalService("workflow")

        # Cancel 'old' production: We must cancel pickings before cancelling production orders
        for id in picking_ids:
            workflow.trg_validate(uid, 'stock.picking', id, 'button_cancel', cr)
        for id in invalid_ids:
            workflow.trg_validate(uid, 'mrp.production', id, 'button_cancel', cr)


        ctx = context.copy()
        ctx['active_id'] = ids[0]
        wizard.change_prod_qty(cr, uid, [wizard.create(cr, uid, {'product_qty': product_qty})], ctx)

        return ids[0]

mrp_production()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
