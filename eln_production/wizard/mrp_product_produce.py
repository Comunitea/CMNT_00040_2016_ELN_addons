# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Javier Colmenero Fern´andez$ <javier@comunitea.com>
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
from openerp.osv import fields, osv

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"
    _description = "Product Produce"

    _columns = {
        # Add Produce Only
        'mode': fields.selection([('consume_produce', 'Consume & Produce'),
                                  ('consume', 'Consume Only'),
                                  ('produce', 'Produce Only')], 'Mode', required=True,
                                  help="'Consume only' mode will only consume the products with the quantity selected.\n"
                                        "'Consume & Produce' mode will consume as well as produce the products with the quantity selected "
                                        "and it will finish the production order when total ordered quantities are produced.")
        }



    def on_change_qty(self, cr, uid, ids, product_qty, consume_lines, context=None):
        """
        Get the products to consume when product is already confirmed
        """
        # import ipdb; ipdb.set_trace()
        if context.get('active_id') and context.get('default_mode', False) and context['default_mode'] == 'consume':  # Custom behaivor, set closed state
            production =self.pool.get('mrp.production').browse(cr, uid, context['active_id'], context)
            if production.move_created_ids2:
                product_qty = production.move_created_ids2[0].product_uom_qty  
        return super(mrp_product_produce, self).on_change_qty(cr, uid, ids, product_qty, consume_lines, context=context)