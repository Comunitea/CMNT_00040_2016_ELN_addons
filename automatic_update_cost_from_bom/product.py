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

from openerp.osv import osv, fields

class product_product(osv.osv):
    
    _inherit = "product.product"
    
    def onchange_categ_id(self, cr, uid, ids, categ_id=False):
        res = {}
        
        if categ_id:
            categ = self.pool.get('product.category').browse(cr, uid, categ_id)
            res = {'value': {'calculate_price': categ.calculate_price}}
            
        return res

