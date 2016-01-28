# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
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
from datetime import datetime
from dateutil.relativedelta import relativedelta

# POST-MIGRATION: NO HAY SALE SHOP
# class sale_shop(osv.osv):
#     _inherit = 'sale.shop'
#
#     _columns = {
#         'supplier_id': fields.many2one('res.partner', 'Supplier', select=True),
#         'order_policy': fields.selection([
#             ('prepaid', 'Pay before delivery'),
#             ('manual', 'Deliver & invoice on demand'),
#             ('picking', 'Invoice based on deliveries'),
#             ('postpaid', 'Invoice on order after delivery'),
#             ('no_bill', 'No bill'),
#             ], 'Invoice Policy',
#                     help="""The Invoice Policy is used to synchronise invoice and delivery operations.
#   - The 'Pay before delivery' choice will first generate the invoice and then generate the picking order after the payment of this invoice.
#   - The 'Deliver & Invoice on demand' will create the picking order directly and wait for the user to manually click on the 'Invoice' button to generate the draft invoice based on the sale order or the sale order lines.
#   - The 'Invoice on order after delivery' choice will generate the draft invoice based on sales order after all picking lists have been finished.
#   - The 'Invoice based on deliveries' choice is used to create an invoice during the picking process.
#   - The 'No bill' choice is used to not create an invoice."""
#             ),
#         'indirect_invoicing': fields.boolean('Indirect Invoicing', help="Check the indirect invoicing field if the shop is a shop of indirect invoicing."),
#     }
#
# sale_shop()
#
# class sale_order(osv.osv):
#     _inherit = 'sale.order'
#
#     def onchange_shop_id(self, cr, uid, ids, shop_id):
#         v = {}
#         if shop_id:
#             shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
#             v['project_id'] = shop.project_id.id
#             v['company_id'] = shop.company_id.id
#             # overriden by the customer priceslist if existing
#             if shop.pricelist_id.id:
#                 v['pricelist_id'] = shop.pricelist_id.id
#             if shop.supplier_id.id:
#                 v['supplier_id'] = shop.supplier_id.id
#             if shop.order_policy:
#                 v['order_policy'] = shop.order_policy
#             v['order_policy'] = shop.order_policy
#             v['supplier_id'] = shop.supplier_id.id
#         return {'value': v}
#
#     def onchange_shop_id2(self, cr, uid, ids, shop_id, partner_id=False):
#         res = self.onchange_shop_id(cr, uid, ids, shop_id)
#         if not shop_id:
#             res['value']['pricelist_id'] = False
#             return res
#
#         if partner_id:
#             shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id)
#             partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
#
#             if shop_obj.indirect_invoicing:
#                 if partner_obj.property_product_pricelist_indirect_invoicing:
#                     res['value']['pricelist_id'] = partner_obj.property_product_pricelist_indirect_invoicing.id
#             else:
#                 if partner_obj.property_product_pricelist:
#                     res['value']['pricelist_id'] = partner_obj.property_product_pricelist.id
#
#         return res
#
# sale_order()
