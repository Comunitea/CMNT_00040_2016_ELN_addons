# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_price_from_cost_structure(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.production_id and move.product_id.cost_structure_id:
                c = context.copy()
                c['cron'] = True
                c['product_id'] = move.product_id.id
                pcl_pool = self.pool.get('product.costs.line')
                cost = pcl_pool.get_product_costs(cr, uid, move.product_id, c)
                price = cost.get('inventory_cost', False)
                if price:
                    self.write(cr, uid, [move.id], {'price_unit': price},
                               context=context)
