# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Omar Castiñeira Saavedra$ <omar@pexego.es>
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
from osv import osv, fields


class product_supplierinfo(osv.osv):
    _inherit = "product.supplierinfo"
    _columns = {
        'name' : fields.many2one('res.partner', 'Supplier/Customer', required=True, ondelete='cascade', help="Supplier or Customer of this product"),
    }
    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product_ids = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id','=',product_id)])
            if product_ids:
                product_obj = self.pool.get('product.product').browse(cr, uid, product_ids[0])
                res['product_uom'] = product_obj.uom_id.id

        return {'value': res}
product_supplierinfo()