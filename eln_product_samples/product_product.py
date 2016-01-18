# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved.
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

from openerp.osv import fields, osv
import decimal_precision as dp


class product_product(osv.osv):

    def _get_product_samples(self, cr, uid, ids, field_name, arg, context):
        """
            Gets remaining samples checking sale order lines with its product and checkbox 'Sample?' check
        """
        res = {}
        qty = 0.0
        c = context.copy()
        action_model, samples_location =  self.pool.get('ir.model.data').get_object_reference(cr, uid, 'eln_product_samples', "stock_physical_location_samples2")
        c.update({'location': samples_location})
        c.update({'warehouse': False})
        for product in self.pool.get('product.product').browse(cr, uid, ids, context=c):
            qty += round(product.qty_available, 2)            
            res[product.id] = qty
            
        return res

    _inherit = 'product.product'

    _columns = {
        'remaining_samples':fields.function(_get_product_samples, method=True, string='Samples', type='float', digits_compute=dp.get_precision('Product UoM'), help="Given Samples (in UoM)", readonly=True),
    }

product_product()
