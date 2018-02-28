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

from openerp import models, fields


class SaleShop(models.Model):
    _name = 'sale.shop'
    _description = 'Sale Type'

    name = fields.Char('Type Name', size=64, required=True)
    payment_default_id = fields.Many2one(string="Default Payment Term", comodel_name='account.payment.term')
    warehouse_id = fields.Many2one(string="Warehouse", comodel_name='stock.warehouse')
    pricelist_id = fields.Many2one(string="Pricelist", comodel_name='product.pricelist')
    project_id = fields.Many2one(string="Analytic Account", comodel_name='account.analytic.account', domain=[('parent_id', '!=', False)])
    company_id = fields.Many2one(string="Company", comodel_name='res.company')
    supplier_id = fields.Many2one(string="Supplier", comodel_name='res.partner', select=True)
    order_policy = fields.Selection([
        ('manual', 'On Demand'), 
        ('picking', 'On Delivery Order'), 
        ('prepaid', 'Before Delivery'), 
        ('no_bill', 'No bill')], string="Create Invoice", 
        help="On demand: A draft invoice can be created from the sales order when needed. \nOn delivery order: A draft invoice can be created from the delivery order when the products have been delivered. \nBefore delivery: A draft invoice is created from the sales order and must be paid before the products can be delivered.")
    indirect_invoicing = fields.Boolean(
        string='Indirect Invoicing',
        default=False,
        help="Check the indirect invoicing field if the shop is a shop of indirect invoicing.")
