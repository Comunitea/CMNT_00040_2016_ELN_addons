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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def get_price_unit(self, cr, uid, move, context=None):
        """ Returns the unit price to store on the quant """
        if move.production_id:
            print '****************************************************************************************'
            print 'el valor para el quant si hay produccion', move.product_id, move.price_unit
            print '****************************************************************************************'
            #return move.price_unit

        return super(stock_move, self).get_price_unit(cr, uid, move, context=context)

    def attribute_price(self, cr, uid, move, context=None):
        """
            Attribute price to move, important in inter-company moves or receipts with only one partner
        """
        # The method attribute_price of the parent class sets the price to the standard product
        # price if move.price_unit is zero. We don't want this behavior in the case of a production
        if move.production_id:
            print '****************************************************************************************'
            print 'tendria que calcular el precio de la estructura', move.product_id, move.price_unit
            print '****************************************************************************************'
            price = False
            if context is None: context = {}
            c = context.copy()
            c['cron'] = True
            price = move.product_id.cost_structure_id and self.pool.get('product.costs.line').get_product_costs(cr, uid, move.product_id, c)['inventory_cost']
            if price:
                print 'voy a retornar en este caso:', price
                print '=============================='
                return self.write(cr, uid, [move.id], {'price_unit': price}, context=context)
            
        super(stock_move, self).attribute_price(cr, uid, move, context=context)
