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
from openerp import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    lines_product_name_str = fields.Char('Lines', size=255,
        compute='_get_products_names', readonly=True)
    container_numbers = fields.Char('Container numbers', size=64,
        readonly=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Container numbers assigned to the order.",)
    invoice_method = fields.Selection(default='picking')

    @api.multi
    def _get_products_names(self):
        for purchase in self:
            stream = [line.product_id.name 
                for line in purchase.order_line
                if line.product_id.name]
            purchase.lines_product_name_str = u" ###, ".join(stream)

    @api.multi
    def set_order_line_status(self, status):
        # No queremos que el abastecimiento se establezca a
        # estado 'exception', sino a 'cancel'
        res = super(PurchaseOrder, self).set_order_line_status(status=status)
        proc_obj = self.env['procurement.order']
        if status == 'cancel':
            order_line_ids = self.mapped('order_line')
            domain = [
                ('purchase_line_id', 'in', order_line_ids.ids),
                ('state', '!=', 'done')
            ]
            procs = proc_obj.search(domain)
            procs.write({'state': 'cancel'})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def unlink(self):
        # No queremos que el abastecimiento se establezca a
        # estado 'exception', sino a 'cancel'
        proc_obj = self.env['procurement.order']
        domain = [
            ('purchase_line_id', 'in', self.ids),
            ('state', '!=', 'done')
        ]
        procs = proc_obj.search(domain)
        res = super(PurchaseOrderLine, self).unlink()
        procs.write({'state': 'cancel'})
        return res


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _calc_new_qty_price(self, procurement, po_line=None, cancel=False):
        """
        En la función original cuando se llama a price_get
        no se tiene en cuenta la compañía del abastecimiento,
        y cuando es llamada desde planificadores usa
        la del usuario (generalmente admin)
        lo cual es un error en caso de multicompañía
        """
        qty, price = super(ProcurementOrder, self)._calc_new_qty_price(
            procurement=procurement, po_line=po_line, cancel=cancel)
        if not po_line:
            po_line = procurement.purchase_line_id
        price = po_line.price_unit
        if qty != po_line.product_qty:
            order_id = po_line.order_id
            pricelist_id = order_id.partner_id.property_product_pricelist_purchase.id
            ctx = dict(
                self._context,
                force_company=procurement.company_id.id,
                uom=procurement.product_id.uom_po_id.id
            )
            pricelist_obj = self.env['product.pricelist']
            pricelist = pricelist_obj.with_context(ctx).browse(pricelist_id)
            price = pricelist.price_get(
                procurement.product_id.id, qty, order_id.partner_id.id)[pricelist_id]
        return qty, price
