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
from openerp.osv import fields, orm

import time
from datetime import datetime
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class product_pricelist_item(orm.Model):
    _inherit = "product.pricelist.item"

    def _get_price_calculated(self, cr, uid, ids, name, arg, context=None):
        """ return the price calculated if it's possible for price list item """
        res = {}

        partner_id = False
        
        for item in self.browse(cr, uid, ids, context=context):
            res[item.id] = 0
            if item.product_id:
                pricelist = item.price_version_id.pricelist_id.id
                if pricelist:
                    product = item.product_id.id
                    qty = item.min_quantity
                    uom = item.product_id.uom_id.id
                    date_price = item.price_version_id.date_start or item.price_version_id.date_end 
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], 
                            product, qty or 1.0, partner_id, dict(context,
                                uom=uom,
                                date=date_price,
                                ))[pricelist]
                    if not price:
                        res[item.id] = 0.0
                    else:
                        res[item.id] = price        

        return res
    
    _columns = {
        'price_calculated': fields.function(
            _get_price_calculated,
            type='float',
            precision=dp.get_precision('Sale Price'),
            string="Price Calculated"),
    }
    _defaults = {
        'price_calculated': lambda *a: 0,
    }

