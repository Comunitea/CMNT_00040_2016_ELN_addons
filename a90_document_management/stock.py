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
from openerp.osv import osv, fields

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'devolution_id': fields.many2one('stock.picking','Devolution', readonly=True)
    }

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        '''Call after the creation of the invoice'''
        # import ipdb; ipdb.set_trace()
        super(stock_picking, self)._invoice_hook(cr, uid, picking, invoice_id)
        if picking and invoice_id:
            if picking.x_expedient_id:
                invoice_obj = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
                if invoice_obj.x_expedient_id:
                    self.pool.get('expedient').write(cr, uid, [picking.x_expedient_id.id],{'parent_expedient': invoice_obj.x_expedient_id.id})
            
        return True

    def write(self, cr, uid, ids, vals, context=None):

        if context is None: context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        res = super(stock_picking, self).write(cr, uid, ids, vals, context=context)
        for current_obj in self.browse(cr, uid, ids):
            if 'x_expedient_id' in self._columns:
                if current_obj.x_expedient_id:
                    if vals.get('attached',False):
                        self.pool.get('expedient').validate_expedient(cr, uid, [current_obj.x_expedient_id.id],context=context)
                    if vals.get('date', False):
                        self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'date_origin_model': str(current_obj.date)},context=context)
                    if vals.get('address_id', False):
                        self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'partner_name_expedient': (current_obj.address_id and current_obj.address_id.partner_id and current_obj.address_id.partner_id.name or '')},context=context)
                    if vals.get('name', False):
                        self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'name_origin_model': current_obj.name},context=context)


        return res
    def create(self, cr, uid, vals, context=None):

        res = super(stock_picking, self).create(cr, uid, vals, context)
        if res:
            current_obj = self.browse(cr, uid, res)
            if current_obj:
                if 'x_expedient_id' in self._columns:
                    if current_obj.x_expedient_id:
                        if current_obj.date:
                            self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'date_origin_model': str(current_obj.date)},context=context)
                        if current_obj.address_id:
                            self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'partner_name_expedient': (current_obj.address_id and current_obj.address_id.partner_id and current_obj.address_id.partner_id.name or '')},context=context)
                        if current_obj.name:
                            self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'name_origin_model': current_obj.name},context=context)

        return res

#    def copy(self, cr, uid, id, default=None, context=None):
#        # name like return
#        import ipdb; ipdb.set_trace()
#        res = super(stock_picking, self).copy(cr, uid, id, default, context)
#        if res:
#            picking_obj = self.pool.get('stock.picking').browse(cr, uid, res, context=context)
#            if 'return' in picking_obj.name:
#                picking_orig = self.pool.get('stock.picking').browse(cr, uid, id, context=context)
#                if 'x_expedient_id' in picking_orig._columns and picking_orig.x_expedient_id:
#                    self.pool.get('stock.picking').write(cr, uid, picking_obj.id, {'x_expedient_id': picking_orig.x_expedient_id.id})
#
#        return res


class stock_return_picking(osv.osv_memory):

    _inherit = "stock.return.picking"

    def create_returns(self, cr, uid, ids, context=None):
        """returns correct view"""
        if context is None: context = {}
        pick_obj = self.pool.get('stock.picking')
        res = super(stock_return_picking, self).create_returns(cr, uid, ids, context=context)
        #Albaran de salida
        record_id = context and context.get('active_id', False) or False
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        #albarán de entrada - return
        domain = list(eval(res['domain']))
        picking_id = domain[0][2][0]


        pick_obj.write(cr, uid, picking_id, {'devolution_id': pick.id})

        return res
