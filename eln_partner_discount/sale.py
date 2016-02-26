# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY Pexego (<www.pexego.es>). All Rights Reserved
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

"""Inherits sale.order.line to drag partner discount to invoice lines"""

from openerp.osv import orm

class sale_order_line(orm.Model):
    """Inherits sale.order.line to drag partner discount to invoice lines"""

    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        import ipdb; ipdb.set_trace()
        """set partner discount to sale order lines discount"""
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, 
            uom, qty_uos, uos, name, partner_id, 
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        shop_obj = False
        
        if context and context.get('shop', False):
            shop_obj = self.pool.get('sale.shop').browse(cr, uid, context.get('shop'))        
            if partner_id and result.get('value', False):
                partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
                result['value']['discount'] = partner_obj.property_partner_sale_discount
                if shop_obj and shop_obj.indirect_invoicing:
                    result['value']['discount'] = 0.0

        return result


