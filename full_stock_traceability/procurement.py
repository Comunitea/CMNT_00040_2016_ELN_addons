# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
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

from osv import osv
from tools.translate import _

class procurement_order(osv.osv):
    
    _inherit = "procurement.order"
    
    def check_lot(self, cr, uid, ids, context=None):
        """checks if all procurement moves are done and if production lot is assigned"""
        if context is None: context = {}
        ok = True
        for procurement in self.browse(cr, uid, ids):
            if procurement.move_id:
                if not procurement.move_id.prodlot_id and procurement.move_id.product_id.track_all:
                    cr.execute('update procurement_order set message=%s where id=%s', (_('Production lot isn\'t set in reservation.'), procurement.id))
                    ok = False
            else:
                ok = False
        return ok
        
procurement_order()
