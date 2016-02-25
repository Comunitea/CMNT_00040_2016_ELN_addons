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
from openerp.osv import orm, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta


# POST-MIGRATION: NO HAY SALE SHOP, RECREAMOS EL OBJETO ETIQUETANDOLO COMO TIPOE VENTA
class sale_shop(orm.Model):
    _name = 'sale.shop'
    _description = 'Sale Type'
    _columns = {
        # CAMPOS COPIADOS DE LA 6.1
        'name': fields.char('Type Name', size=64, required=True),
        'payment_default_id': fields.many2one('account.payment.term', 'Default Payment Term'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
        'project_id': fields.many2one('account.analytic.account', 'Analytic Account', domain=[('parent_id', '!=', False)]),
        'company_id': fields.many2one('res.company', 'Company', required=False),
        # CAMPOS POR DEFECTO
        'supplier_id': fields.many2one('res.partner', 'Supplier', select=True),
        'order_policy': fields.selection([
            ('prepaid', 'Pay before delivery'),
            ('manual', 'Deliver & invoice on demand'),
            ('picking', 'Invoice based on deliveries'),
            ('postpaid', 'Invoice on order after delivery'),
            ('no_bill', 'No bill'),
            ], 'Invoice Policy',
                    help="""The Invoice Policy is used to synchronise invoice and delivery operations.
  - The 'Pay before delivery' choice will first generate the invoice and then generate the picking order after the payment of this invoice.
  - The 'Deliver & Invoice on demand' will create the picking order directly and wait for the user to manually click on the 'Invoice' button to generate the draft invoice based on the sale order or the sale order lines.
  - The 'Invoice on order after delivery' choice will generate the draft invoice based on sales order after all picking lists have been finished.
  - The 'Invoice based on deliveries' choice is used to create an invoice during the picking process.
  - The 'No bill' choice is used to not create an invoice."""
            ),
        'indirect_invoicing': fields.boolean('Indirect Invoicing', help="Check the indirect invoicing field if the shop is a shop of indirect invoicing."),
    }
