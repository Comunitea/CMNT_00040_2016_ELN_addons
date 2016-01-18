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
from openerp.tools.translate import _

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if isinstance(ids,(int,long)):
            ids = [ids]
        res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
        if vals.get('prodlot_id', False):
            for move in self.browse(cr, uid, ids):
                if move.production_ids and move.production_ids[0].picking_id and move.production_ids[0].picking_id.move_lines:
                    for line in move.production_ids[0].picking_id.move_lines:
                        if line.product_id and line.product_id.id == move.product_id.id \
                                and (line.prodlot_id and line.prodlot_id.id != vals['prodlot_id'] or not line.prodlot_id):
                            self.pool.get('stock.move').write(cr, uid, line.id, {'prodlot_id': vals['prodlot_id']})
        return res


    def product_id_change_mrp_productions(self, cr, uid, ids, prod_id=False, production_name='', context=None):
        if not prod_id:
            return {}
        mrp = False
        destination_location_id = False
        source_location_id = False
        mrp = self.pool.get('mrp.production').search(cr, uid, [('name','=', production_name)])
        if mrp:
            mrp = self.pool.get('mrp.production').browse(cr, uid, mrp[0])
            destination_location_id = mrp.product_id.product_tmpl_id.property_stock_production.id
            source_location_id = mrp.location_src_id.id

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context)[0]
        uos_id  = product.uos_id and product.uos_id.id or False

        result = {
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'name': _('PROD: %s') % production_name,
            'location_id': source_location_id,
            'location_dest_id': destination_location_id,
            'state': 'waiting',
        }

        return {'value': result}

    def unlink(self, cr, uid, ids, context=None):
        #27/11/2015
        #Se añadaen las lineas con PGC para que solo deje borrar movimientos "a consumir" de una producción
        #Sin eso y llamando directamente al orm permitia borrar todos los movimiento sin distinción.
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move') #PGC 
        proc = self.pool.get('procurement.order')
        procurements = []
        ids_unlink = []

        for move in self.browse(cr, uid, ids, context=context):
            procurements = proc.search(cr, uid, [('move_id','=', move.id)])
            
            #Si pertenece a una producción lo pongo como borrador para que se pueda borrar al llamar al super
            if move.production_ids and move.state not in ('done', 'cancel'): #PGC
                move_obj.write(cr, uid, move.id, {'state': 'draft'}) #PGC
                
            ids_unlink.append(move.id)
            if procurements:
                proc.write(cr, uid, procurements, {'state':'cancel'})
                proc.unlink(cr, uid, procurements)
                procurements = []
            if move.move_dest_id_lines:
                for dest in move.move_dest_id_lines:
                    procurements = proc.search(cr, uid, [('move_id','=', dest.id)])
                    if procurements:
                        proc.write(cr, uid, procurements, {'state':'cancel'})
                        proc.unlink(cr, uid, procurements)
                    #Si pertenece a una producción lo pongo como borrador para que se pueda borrar al llamar al super
                    if move.production_ids and move.state not in ('done', 'cancel'): #PGC
                        move_obj.write(cr, uid, dest.id, {'state': 'draft'}) #PGC
                    ids_unlink.append(dest.id)
        return super(stock_move, self).unlink(cr, uid, ids_unlink, context=context) #PGC
        #return osv.osv.unlink(self, cr, uid, ids_unlink, context=context) 

stock_move()

class stock_location(osv.osv):
    _inherit = 'stock.location'
    _columns = {
        'sample_location': fields.boolean('Sample location')
    }
stock_location()
