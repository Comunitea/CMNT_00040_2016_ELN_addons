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
from openerp.osv import osv,fields

class stock_location_templates(osv.osv):
    _name = 'stock.location.templates'
    _description = 'Templates logistics flows'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'flow_pull_ids': fields.one2many('product.pulled.flow', 'template_id', 'Pulled Flows'),
        'path_ids': fields.one2many('stock.location.path', 'template_id', 'Pushed Flow',
            help="These rules set the right path of the product in the "\
            "whole location tree."),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.pulled.flow', context=c),
    }
    
stock_location_templates()

class stock_location_path(osv.osv):
    _inherit = "stock.location.path"
    _columns = {
        'template_id': fields.many2one('stock.location.templates', 'Template')
    }
    
stock_location_path()

class product_pulled_flow(osv.osv):
    _inherit = 'product.pulled.flow'
    _columns = {
        'product_id':fields.many2one('product.product', 'Product', ondelete='cascade'),
        'template_id': fields.many2one('stock.location.templates', 'Template', ondelete='cascade'),
        'automatic_exec': fields.boolean('Automatic Exec.')
    }
product_pulled_flow()

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):
        """ Cuando tenemos un flujo arrastrado que mueve producto de por ejemplo quival a intercompañías y de intercompañías a valquin
        tenemos un problema de permisos al validar el movimiento de almacén, porque en el campo move_dest_id se hace referencia al movimiento de 
        la otra compañía. Para ello podemos validar desde la compañía padre o bien con el usuario admin.
        Para este caso comprobamos si el movimiento tiene ubicación destino intercompañías y si tiene move_dest_id. En ese caso continuamos como admin
        y si no, no hacemos ningún cambio. 
        """
        if context is None:
            context = {}
            
        prodlot_obj = self.pool.get('stock.production.lot')
        
        for move in self.browse(cr, 1, ids, context=context):
            if move.move_dest_id.id and move.location_dest_id.usage in ('transit') and move.company_id != move.move_dest_id.company_id:
                super(stock_move, self).action_done(cr, 1, [move.id], context)
                if move.prodlot_id.id: #Si tenemos lote para enviar comprobamos si ya existe en la compañía destino uno relacionado
                    lot_dest_ids = prodlot_obj.search(cr, 1, [('multicompany_prodlot_id', '=', move.prodlot_id.id)])
                    if not lot_dest_ids:
                        new_id = prodlot_obj.copy(cr, 1, move.prodlot_id.id, {'company_id': move.move_dest_id.company_id.id, 'multicompany_prodlot_id': move.prodlot_id.id}, context)
                        lot_dest_ids = [new_id]
                    if not move.move_dest_id.prodlot_id and move.product_id == move.move_dest_id.product_id: #Asignamos ya el nuevo lote, si en el destino no había ninguno
                        self.write(cr, 1, [move.move_dest_id.id], {'prodlot_id': lot_dest_ids[0]}, context)
            else:
                super(stock_move, self).action_done(cr, uid, [move.id], context)
                
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cuando tenemos un flujo arrastrado que mueve producto de por ejemplo quival a intercompañías y de intercompañías a valquin
        tenemos un problema de permisos al cancelar el movimiento de almacén desde quival (si cancel_cascade es True en el flujo), 
        porque en el campo move_dest_id se hace referencia al movimiento de 
        la otra compañía. Para ello podemos validar desde la compañía padre o bien con el usuario admin.
        Para este caso comprobamos si el movimiento tiene ubicación destino intercompañías y si tiene move_dest_id. En ese caso continuamos como admin
        y si no, no hacemos ningún cambio. 
        """
        if not len(ids):
            return True
        if context is None:
            context = {}

        for move in self.browse(cr, 1, ids, context=context):
            if move.cancel_cascade and move.move_dest_id.id and move.location_dest_id.usage in ('transit') and move.company_id != move.move_dest_id.company_id:
                res = super(stock_move, self).action_cancel(cr, 1, [move.id], context)
            else:
                res = super(stock_move, self).action_cancel(cr, uid, [move.id], context)

        return res

stock_move()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    #Creamos este campo para cuando enviamos mercancía de quival a valquin y duplicamos el lote
    #De esta forma si existe el id origen en algun lote en el campo multicompany_prodlot_id no será necesario crearlo de nuevo
    _columns = {
        'multicompany_prodlot_id': fields.integer('multicompany_prodlot_id',
            help='Campo que relaciona lote origen con destino en intercambios multicompañía'),
    }

    def copy(self, cr, uid, id, defaults, context=None):
        if defaults is None:
            defaults = {}
        if context is None:
            context = {}
        defaults = defaults.copy()
        if not defaults.get('multicompany_prodlot_id', False):
            defaults['multicompany_prodlot_id'] = None

        return super(stock_production_lot, self).copy(cr, uid, id, defaults, context=context)

stock_production_lot()
