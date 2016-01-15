# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
from openerp.osv import osv, fields

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def write(self,cr,uid,ids,vals,context=None):
        if context is None:
            context = {}
        res = super(sale_order,self).write(cr,uid,ids,vals,context=context)
        for sale in self.browse(cr,uid,ids):
            if "x_expedient_id" in self._columns and sale.x_expedient_id:
                sale.x_expedient_id.write({'name_origin_model':sale.id})
        return res