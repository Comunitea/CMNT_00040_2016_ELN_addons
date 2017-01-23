# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from openerp.osv import orm, fields
import re

class product_product(orm.Model):
    _inherit = 'product.product'

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        result = super(product_product, self).name_search(cr, user, name=name, args=args, operator=operator, context=context, limit=limit)
        prodpart = self.pool.get('partner.product')
        if name:
            if context.get('partner_id', False):
                prodids = prodpart.search(cr, user, [('partner_id', '=', context['partner_id']), ('name', '=', name)], limit=limit, context=context)
                ids = []
                if prodids:
                    ids = [x.product_id.id for x in prodpart.browse(cr, user, prodids)]
                if ids:
                    result = self.name_get(cr, user, ids, context=context)
        return result
