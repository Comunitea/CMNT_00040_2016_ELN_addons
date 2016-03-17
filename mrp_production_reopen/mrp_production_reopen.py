# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
#import decimal_precision as dp
import openerp.addons.decimal_precision as dp

class mrp_production_reopen(osv.osv):

    _inherit = 'mrp.production'
    _columns = {
        'product_qty': fields.float('Product Qty', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, states={'draft':[('readonly',False)], 'reopen':[('readonly',False)]}, readonly=True),
        'product_uos_qty': fields.float('Product UoS Qty', states={'draft':[('readonly',False)], 'reopen':[('readonly',False)]}, readonly=True),
        'state': fields.selection([('draft','New'),('picking_except', 'Picking Exception'),('confirmed','Waiting Goods'),('ready','Ready to Produce'),('in_production','In Production'),('cancel','Cancelled'),('done','Done'),('reopen', 'Reopen')],'State', readonly=True,
                                    help='When the production order is created the state is set to \'Draft\'.\n If the order is confirmed the state is set to \'Waiting Goods\'.\n If any exceptions are there, the state is set to \'Picking Exception\'.\
                                    \nIf the stock is available then the state is set to \'Ready to Produce\'.\n When the production gets started then the state is set to \'In Production\'.\n When the production is over, the state is set to \'Done\'.'),
    }
    
       
    def action_reopen(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'reopen'})
        picking_id = super(mrp_production_reopen, self).browse(cr, uid, ids)
        
        for move in picking_id[0].move_lines2:
            if move.state == "done":
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'draft'})
        
        for products in picking_id[0].move_created_ids2:
            if products.state == "done":
                self.pool.get('stock.move').write(cr, uid, [products.id], {'state': 'draft'})
        
        return True

    def action_redone(self, cr, uid, ids, context=None):
        picking_id = super(mrp_production_reopen, self).browse(cr, uid, ids)
        
        for move in picking_id[0].move_lines:
            if move.state == "draft":
                self.pool.get('stock.move').write(cr, uid, [move.id], {'state': 'done'})
        
        for products in picking_id[0].move_created_ids:
            if products.state == "draft":
                self.pool.get('stock.move').write(cr, uid, [products.id], {'state': 'done'})
        
        self.write(cr, uid, ids, {'state': 'done'})
        return True

