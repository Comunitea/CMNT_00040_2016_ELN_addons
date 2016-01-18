# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Santiago Argüeso Armesto$ <santiago@pexego.es>
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
import time


class product_template(osv.osv):
    _inherit = 'product.template'

    def price_date(self, cr, uid, ids, field_names, arg, context=None):
        if context is None:
            context = {}
        c = context.copy()
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            pmp_domain = [('product_id', '=', product.id)]
            to_date = c.get('date', False)
            if not to_date:
                to_date = time.strftime('%Y-%m-%d %H:%M:%S')
            pmp_domain.append(('date', '<=', to_date))
            company_id = c.get('company_id', False)
            if company_id:
                pmp_domain.append(('company_id', '=', company_id))
            pmp_obj = self.pool.get('weighted.average.price')
            pmp_ids = pmp_obj.search(cr, uid, pmp_domain, order='date desc', limit=1)

            if pmp_ids:
                pmp = pmp_obj.browse(cr, uid, pmp_ids[0], context=context)
                pmp_cur = pmp.pmp
            else:
                pmp_cur = product.standard_price

            res[product.id] = pmp_cur
        return res

    _columns = {
        'standard_price_date': fields.function(price_date, type='float',
                                               string='Price on date'),
    }


product_template()

class product_uom(osv.osv):

    _inherit = "product.uom"

    def public_compute_price(self, cr, uid, from_uom_id, price, to_uom_id=False):
        #public method to allow call remotely _compute_price function
        return self._compute_price(cr, uid, from_uom_id, price, to_uom_id=to_uom_id)


product_uom()



class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'real_date': fields.datetime('Real Date',
                                     help="Real Date of Completion"),
    }

    _defaults = {
        'real_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
mrp_production()
