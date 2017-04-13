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
from openerp import models, api, fields
#from openerp.osv import orm, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _get_products_names(self):
        for purchase in self:
            stream = [line.product_id.name 
                      for line in purchase.order_line
                      if line.product_id and line.product_id.name]
            purchase.lines_product_name_str = u" ###, ".join(stream)

    lines_product_name_str = fields.Char(compute='_get_products_names',
                                         string='Lines',
                                         size=255,
                                         readonly=True)
    container_numbers = fields.Char(string='Container numbers',
                                    size=64,
                                    help="Container numbers assigned to the order.",
                                    readonly=False,
                                    states={'done': [('readonly', True)],'cancel': [('readonly', True)]})
    invoice_method = fields.Selection(default='picking')

    @api.multi
    def set_order_line_status(self, status):
        res = super(PurchaseOrder, self).set_order_line_status(status=status)
        proc_obj = self.env['procurement.order']
        if status == 'cancel':
            order_line_ids = []
            for order in self:
                order_line_ids += [po_line.id for po_line in order.order_line]
            procs = proc_obj.search([('purchase_line_id', 'in', order_line_ids),
                                     ('state', '!=', 'done')])
            procs.write({'state': 'cancel'})
        return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def unlink(self):
        proc_obj = self.env['procurement.order']
        order_line_ids = [po_line.id for po_line in self]
        procs = proc_obj.search([('purchase_line_id', 'in', order_line_ids),
                                 ('state', '!=', 'done')])
        res = super(PurchaseOrderLine, self).unlink()
        procs.write({'state': 'cancel'})
        return res


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _calc_new_qty_price(self, procurement, po_line=None, cancel=False):
        """
        En la función original cuando se llama a price_get no se tiene en cuenta la compañía del abastecimiento,
        y cuando es llamada desde planificadores usa la del usuario (generalmente admin) lo cual es un error en caso de multicompañía
        """
        qty, price = super(ProcurementOrder, self)._calc_new_qty_price(procurement=procurement, po_line=po_line, cancel=cancel)
        if not po_line:
            po_line = procurement.purchase_line_id
        price = po_line.price_unit
        if qty != po_line.product_qty:
            pricelist_id = po_line.order_id.partner_id.property_product_pricelist_purchase.id
            uom_id = procurement.product_id.uom_po_id.id
            pricelist_obj = self.env['product.pricelist'].\
                            with_context(force_company=procurement.company_id.id, uom=uom_id).\
                            browse(pricelist_id)
            price = pricelist_obj.price_get(procurement.product_id.id, qty, po_line.order_id.partner_id.id)[pricelist_id]
        return qty, price
