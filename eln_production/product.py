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
import openerp.addons.decimal_precision as dp


class product_product(osv.osv):
    _inherit = 'product.product'
    
    def _product_real_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        """ Finds the incoming and outgoing quantity of product.
        @return: Dictionary of values
        """
        if not field_names:
            field_names = []
        if context is None:
            context = {}
        
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0.0)
       
        for id in ids:            
            product = self.pool.get('product.product').browse(cr, uid, id)
            res[id] = product.qty_available - product.outgoing_qty
            
        return res

    _columns = {
        'real_virtual_available': fields.function(_product_real_available, digits_compute=dp.get_precision('Product Unit of Measure'),type='float', string='Real Quantity Available',
                                help="Forecast quantity (computed as Quantity On Hand "
                                     "- Outgoing)\n"
                                     "In a context with a single Stock Location, this includes "
                                     "goods stored at this Location, or any of its children.\n"
                                     "In a context with a single Warehouse, this includes "
                                     "goods stored in the Stock Location of this Warehouse, or any "
                                     "of its children.\n"
                                     "In a context with a single Shop, this includes goods "
                                     "stored in the Stock Location of the Warehouse of this Shop, "
                                     "or any of its children.\n"
                                     "Otherwise, this includes goods stored in any Stock Location "
                                     "typed as 'internal'."),
        'sample_location': fields.boolean('Sample Location'),
        'qty_sample': fields.float('Qty. Sample',  digits_compute=dp.get_precision('Product Unit of Measure'))
    }
    
product_product()
