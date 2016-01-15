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


from openerp.osv import osv

class mrp_bom(osv.osv):
    
    _inherit = "mrp.bom"

    def run_compute_cost(self, cr, uid, ids=False, context=None):
        if context is None: context = {}
        if not ids:
            ids = self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',False)])
            
        for bom in self.browse(cr, uid, ids):
            if bom.bom_lines:
                self.run_compute_cost(cr, uid, [x.id for x in bom.bom_lines])
            bom.product_id.compute_price()
                
        return True