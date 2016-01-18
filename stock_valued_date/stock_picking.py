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
from openerp import netsvc
import time
from datetime import datetime, timedelta


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'real_date': fields.datetime('Real Date', help="Real Date of Completion"),
    }

    _defaults = {
        'real_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
mrp_production()


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _order = "real_date desc"

    _columns = {
        'real_date': fields.datetime('Real Date', help="Real Date of Completion"),
    }

    _defaults = {
        'real_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    def create(self, cr, uid, vals, context={}):
        """overwrites create method to set real_date equal to commitment_date"""
        res = super(stock_picking, self).create(cr, uid, vals, context=context)
        
        if res:
            picking = self.browse(cr, uid, res)
            if picking.commitment_date:
                self.write(cr, uid, [res], {'real_date': picking.commitment_date})

        return res

    def write(self, cr, uid, ids, vals, context=None):
        product_obj = self.pool.get('product.product')
        move_obj = self.pool.get('stock.move')
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(stock_picking, self).write(cr, uid, ids, vals, context=context)
        if vals.get('real_date', False):
            virtual_types = ["supplier", "customer", "inventory", "procurement", "production", "transit"]
            for picking in self.browse(cr, uid, ids):
                for move in picking.move_lines:
                    if move.state == 'done' and (move.location_id.usage in virtual_types or move.location_dest_id.usage in virtual_types):
                        new_date = datetime.strptime(vals['real_date'], "%Y-%m-%d %H:%M:%S")
                        move_date = datetime.strptime(move.date, "%Y-%m-%d %H:%M:%S")
                        context.update({'move_date': new_date < move_date and vals['real_date'] or move.date,
                                        'update_move': new_date < move_date and True or False})
                        move.write({'date': vals['real_date']})
                        self.pool.get('stock.move').recalculate_pmp(cr, uid, [move.id], (move.purchase_line_id and (move.purchase_line_id.price_unit * (1 - (move.purchase_line_id.discount or 0.0) /100.0)) or (move.price_unit or False)), move.product_uom.id, move.product_qty, context=context)
                    else:
                        move.write({'date': vals['real_date']})
        return res

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, move_product_uos_coeff, move_product_uos, move_product_uom_base, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)

                product = product_obj.browse(cr, uid, move.product_id.id)
                uom_base_id = product.uom_id and product.uom_id.id or False
                uos_coeff = product_obj.read(cr, uid, move.product_id.id, ['uos_coeff'])
                uos_id = product.uos_id and product.uos_id.id or False
                move_product_uom_base[move.id] = uom_base_id
                if uos_id:
                    move_product_uos[move.id] = uos_id
                    move_product_uos_coeff[move.id] = uos_coeff['uos_coeff'] or 1.0
                else:
                    move_product_uos[move.id] = product_uom
                    move_product_uos_coeff[move.id] = 1.0

                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if qty > 0:
                        pmp = self.pool.get('stock.move')._create_line_pmp(cr, uid, [move.id],product_currency, product_price, product_qty, product_uom, context=context)
                        # Write the field according to price type field
                        id_pmp = self.pool.get('weighted.average.price').search(cr, uid, [('product_id', '=', product.id),('company_id','=', move.company_id.id)],order='date desc', limit=1)
                        obj = self.pool.get('weighted.average.price').browse(cr, uid, id_pmp[0])

                        product_obj.write(cr, uid, [product.id], {'standard_price': obj.pmp})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})

            for move in too_few:
                product_qty = move_product_qty[move.id]
                product_qty_uom = self.pool.get('product.uom')._compute_qty(cr, uid, product_uoms[move.id], product_qty, move_product_uom_base[move.id])
                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty_uom * move_product_uos_coeff[move.id], 
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id],
                            'product_uos': move_product_uos[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - partial_qty[move.id],
                            'product_uos_qty': (
                                                self.pool.get('product.uom')._compute_qty(cr, uid, product_uoms[move.id], move.product_qty, move_product_uom_base[move.id]) -
                                                self.pool.get('product.uom')._compute_qty(cr, uid, product_uoms[move.id], partial_qty[move.id], move_product_uom_base[move.id])
                                                ) * move_product_uos_coeff[move.id],
                            'product_uos': move_product_uos[move.id]
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                product_qty_uom = self.pool.get('product.uom')._compute_qty(cr, uid, product_uoms[move.id], product_qty, move_product_uom_base[move.id])
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty_uom * move_product_uos_coeff[move.id],
                    'product_uom': product_uoms[move.id],
                    'product_uos': move_product_uos[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'inventory_ids':fields.many2many('stock.inventory', 'stock_inventory_move_rel','move_id', 'inventory_id', 'Inventories'),
        'production_ids': fields.many2many('mrp.production', 'mrp_production_move_ids', 'move_id', 'production_id', 'Consumed Products'),
    }

    def _calculate_pmp(self, cr, uid, old_move, product_currency, stock_cur, pmp_cur, stock_new, pmp_new, product_uom, context=None):
        move = self.pool.get('stock.move').browse(cr, uid, old_move[0])
        product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context={'to_date': move.date})
        move_currency_id = move.company_id.currency_id.id

        qty = self.pool.get('product.uom')._compute_qty(cr, uid, product_uom, stock_new, product.uom_id.id)
        if qty >= 0:
            new_price = self.pool.get('res.currency').compute(cr, uid, product_currency,
                    move_currency_id, pmp_new, round=False)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, product_uom, new_price,
                    product.uom_id.id)
            if stock_cur <= 0:
                pmp = new_price
            else:
                pmp = (( stock_cur * pmp_cur)+(stock_new * new_price))/(stock_cur + stock_new)

        return pmp

    def _create_line_pmp(self, cr, uid, ids, product_currency, product_price, product_qty, product_uom, context=None):
        if context is None:
            context = {}

        register_obj = self.pool.get('weighted.average.price')
        move_obj = self.pool.get('stock.move').browse(cr, uid, ids[0], context=context)
        product_id = move_obj.product_id.id
        date = move_obj.picking_id.real_date
        company_id = move_obj.company_id.id

        # pmps posteriores
        ids_registers_pos = register_obj.search(cr, uid, [('product_id', '=', product_id), ('company_id', '=', company_id), ('date', '>', date)], order='date asc')
        context.update({'to_date': datetime.strftime(datetime.strptime(date, "%Y-%m-%d %H:%M:%S") - timedelta(minutes=1), "%Y-%m-%d %H:%M:%S"),
                        'company_id': company_id})
        product = self.pool.get('product.product').browse(cr, uid, move_obj.product_id.id, context=context)

        #stock en fecha real
        stock_cur = product.qty_available
        pmp_cur = product.standard_price_date

        pmp = self._calculate_pmp(cr, uid, [move_obj.id], product_currency, stock_cur, pmp_cur, product_qty, product_price, product_uom, context=context)
        id_new = register_obj.create(cr, uid, {'product_id': product_id,
                                                                'date': date,
                                                                'pmp': pmp,
                                                                'move_id': move_obj.id,
                                                                'company_id': move_obj.company_id.id,
                                                                'pmp_old': pmp_cur
                                                            })

        if ids_registers_pos:
            self.update_pos_registers(cr, uid, ids_registers_pos, product_id, context=context)

        return id_new

    def update_pos_registers(self, cr, uid, ids, product_id, context=None):
        if context is None: context = {}
        register_obj = self.pool.get('weighted.average.price')
        product_obj = self.pool.get('product.product')

        for reg in ids:
            obj = register_obj.browse(cr, uid, reg, context=context)
            c_date = datetime.strftime(datetime.strptime(obj.date, "%Y-%m-%d %H:%M:%S") - timedelta(minutes=1), "%Y-%m-%d %H:%M:%S")
            context.update({'to_date': c_date,'date': c_date, 'company_id': obj.move_id.company_id.id})
            product = product_obj.browse(cr, uid, product_id, context=context)

            pmp_cur = product.standard_price_date
            stock_cur = product.qty_available
            if stock_cur < 0.0:
                stock_cur = 0.0

            pmp = self._calculate_pmp(cr, uid, [obj.move_id.id], obj.move_id.price_currency_id.id, product.qty_available, pmp_cur, obj.move_id.product_qty, (obj.move_id.purchase_line_id and (obj.move_id.purchase_line_id.price_unit * (1 - (obj.move_id.purchase_line_id.discount or 0.0) /100.0)) or (obj.move_id.price_unit or 0.0)), obj.move_id.product_uom.id,context=context)
            register_obj.write(cr, uid, reg, {'pmp': pmp, 'pmp_old': pmp_cur})

        return True

    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        res = super(stock_move, self).action_done(cr, uid, ids, context=context)
        virtual_types = ["supplier", "customer", "inventory", "procurement", "production", "transit"]
        for move in self.browse(cr, uid, ids, context=context):
            if move.state == 'done' and (move.location_id.usage in virtual_types or move.location_dest_id.usage in virtual_types):
                pmp_ids = self.pool.get('weighted.average.price').search(cr, uid, [('move_id', '=', move.id)])
                price = move.purchase_line_id and (move.purchase_line_id.price_unit * (1 - (move.purchase_line_id.discount or 0.0) /100.0)) or move.price_unit
                if move.location_id.usage == "transit" and move.picking_id.type == 'in' and not pmp_ids:
                    if price:
                        pmp = self.pool.get('stock.move')._create_line_pmp(cr, uid, [move.id], move.purchase_line_id and move.purchase_line_id.order_id.pricelist_id.currency_id.id or move.company_id.currency_id.id, price, move.product_qty, move.product_uom.id, context=context)
                        # Write the field according to price type field
                        id_pmp = self.pool.get('weighted.average.price').search(cr, uid, [('product_id', '=', move.product_id.id),('company_id','=', move.company_id.id)],order='date desc', limit=1)
                        obj = self.pool.get('weighted.average.price').browse(cr, uid, id_pmp[0])

                        self.pool.get('product.product').write(cr, uid, [move.product_id.id], {'standard_price': obj.pmp})
                else:
                    self.recalculate_pmp(cr, uid, [move.id], price, move.product_uom.id, move.product_qty, context=context)

        return res


    def recalculate_pmp(self, cr, uid, ids, new_price, uom, qty, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')

        move = move_obj.browse(cr, uid, ids[0], context=context)
        picking = picking_obj.browse(cr, uid, move.picking_id.id)
        product_id = move.product_id.id
        if context.get('move_date', False):
            date = context['move_date']
        else:
            date = move.date
        company_id = move.company_id.id
        register_obj  = self.pool.get('weighted.average.price')
        uom_obj = self.pool.get('product.uom')

        id_register = register_obj.search(cr, uid, [('move_id', '=', move.id)])

        if id_register and context.get('update_move', False): #si ya existe y la fecga nueva en menor a la anterior
            c_date = datetime.strftime(datetime.strptime(date, "%Y-%m-%d %H:%M:%S") - timedelta(minutes=1), "%Y-%m-%d %H:%M:%S")
            context.update({'to_date': c_date,'date': c_date, 'company_id': company_id})
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            #stock en fecha real
            stock_cur = product.qty_available
            if stock_cur < 0.0:
                stock_cur = 0.0

            pmp_cur = product.standard_price_date
            obj = register_obj.browse(cr, uid, id_register[0], context=context)
            move_currency_id = move.purchase_line_id and move.purchase_line_id.order_id.pricelist_id.currency_id.id or move.company_id.currency_id.id
            pmp = self._calculate_pmp(cr, uid, [move.id], move_currency_id, stock_cur, pmp_cur, qty, new_price, uom, context=context)
            register_obj.write(cr, uid, [id_register[0]], {'pmp': pmp, 'date': move.date, 'pmp_old': pmp_cur})
        elif id_register:
            register_obj.write(cr, uid, [id_register[0]], {'date': move.date})

        ids_registers_pos = register_obj.search(cr, uid, [('product_id', '=', product_id),('company_id','=', company_id),('date','>',date)],order='date asc')
        if context.get('update_move', False) and id_register:
            ids_registers_pos = list(set(ids_registers_pos) - set(id_register))

        if ids_registers_pos:
            self.update_pos_registers(cr, uid, ids_registers_pos, product_id, context=context)

        return True

stock_move()
