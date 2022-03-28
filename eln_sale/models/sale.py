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
from datetime import datetime
from dateutil import tz
from dateutil.rrule import rrule
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    supplier_id = fields.Many2one(
        string="Supplier",
        comodel_name='res.partner',
        readonly=True, select=True,
        domain = [('supplier','=',True)],
        states={'draft': [('readonly', False)]})
    order_policy = fields.Selection(selection_add=[('no_bill', 'No bill')])
    supplier_cip = fields.Char(
        string="CIP", size=9, readonly=True,
        states={'draft': [('readonly', False)],'waiting_date': [('readonly', False)],'manual': [('readonly', False)],'progress': [('readonly', False)]},
        help="Internal supplier code")
    shop_id = fields.Many2one(
        string="Sale type",
        comodel_name='sale.shop',
        required=True)
    commercial_partner_id = fields.Many2one(
        string="Partner Company",
        comodel_name='res.partner',
        related='partner_id.commercial_partner_id',
        store=True, readonly=True)
    effective_date = fields.Date(
        string="Effective Date",
        compute="_get_effective_date", store=True,
        help="Date on which the first delivery order was delivered.")
    lead_time = fields.Integer(
        string="Lead Time",
        compute="_get_lead_time", store=True,
        help="Number of days between order confirmation and delivery of the products to the customer.\n" \
        "If the order has a delivery date, this value indicates the deviation with that date.\n"\
        "When this value cannot be calculated, it will be set to -1.\n"\
        "Values greater than 20 will also be set to -1.\n"\
        "Negative values should generally not be taken into account for statistical calculations.")
    procurement_group_id = fields.Many2one(select=True) # Redefine index

    @api.multi
    @api.depends('state')
    def _get_effective_date(self):
        """Read the shipping effective date from the related pickings"""
        for order in self:
            if order.state in ('cancel', 'draft'):
                order.effective_date = False
            else:
                order.update_effective_date()

    @api.multi
    @api.depends('effective_date', 'date_confirm', 'requested_date')
    def _get_lead_time(self):
        for order in self:
            lead_time = -1
            if order.effective_date and (order.date_confirm or order.requested_date):
                effective_date = datetime.strptime(order.effective_date, '%Y-%m-%d')
                if order.requested_date:
                    date_confirm = datetime.strptime(order.requested_date[:10], '%Y-%m-%d')
                else:
                    date_confirm = datetime.strptime(order.date_confirm, '%Y-%m-%d')
                diff_dates = effective_date - date_confirm
                excluded_dates = (rrule(
                    freq=3, # Daily
                    byweekday=(5, 6), # Sat and Sun
                    wkst=0,
                    dtstart=date_confirm,
                    interval=1)
                    .between(date_confirm, effective_date, inc=True)
                )
                is_weekend = (effective_date.weekday() > 4)
                lead_time = diff_dates.days - len(excluded_dates) + (is_weekend and 1 or 0)
                if abs(lead_time) > 20: # Un valor superior entendemos que se debe a un error
                    lead_time = -1
            order.lead_time = lead_time

    @api.onchange('shop_id')
    def onchange_shop_id(self):
        if self.shop_id:
            self.company_id = self.shop_id.company_id
            self.pricelist_id = self.shop_id.pricelist_id
            self.supplier_id = self.shop_id.supplier_id
            self.order_policy = self.shop_id.order_policy
            self.warehouse_id = self.shop_id.warehouse_id
            if self.shop_id.project_id and not self.project_id:
                self.project_id = self.shop_id.project_id
            if self.partner_id:
                partner_id = self.partner_id.commercial_partner_id
                if self.shop_id.indirect_invoicing:
                    self.supplier_cip = False
                else:
                    self.supplier_cip = partner_id.commercial_partner_id.supplier_cip
                if self.shop_id.indirect_invoicing:
                    if partner_id.property_product_pricelist_indirect_invoicing:
                        self.pricelist_id = partner_id.property_product_pricelist_indirect_invoicing
                else:
                    if partner_id.property_product_pricelist:
                        self.pricelist_id = partner_id.property_product_pricelist
                domain = [
                    ('partner_id', '=', partner_id.id),
                    ('shop_id', '=', self.shop_id.id)
                ]
                partner_shop_ids = self.env['partner.shop.payment'].search(domain, limit=1)
                if partner_shop_ids.customer_payment_mode:
                    self.payment_mode_id = partner_shop_ids.customer_payment_mode
                    self.payment_term = partner_shop_ids.customer_payment_term
                else:
                    self.payment_mode_id = partner_id.customer_payment_mode
                    self.payment_term = partner_id.property_payment_term
        else:
            self.pricelist_id = False

    @api.multi
    def action_ship_create(self):
        res = super(SaleOrder, self).action_ship_create()
        user_tz = self.env.user.tz
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(user_tz)
        for order in self:
            for picking in order.picking_ids:
                if order.requested_date:
                    datetime_requested = \
                        datetime.strptime(order.requested_date,
                                          '%Y-%m-%d %H:%M:%S').\
                        replace(tzinfo=from_zone).astimezone(to_zone)
                    date_requested = datetime.strftime(datetime_requested,
                                                       '%Y-%m-%d')
                    date_effective = date_requested
                else:
                    date_requested = False
                    datetime_effective = \
                        datetime.strptime(order.commitment_date,
                                          '%Y-%m-%d %H:%M:%S').\
                        replace(tzinfo=from_zone).astimezone(to_zone)
                    date_effective = datetime.strftime(datetime_effective,
                                                       '%Y-%m-%d')
                vals = {'note': order.note,
                        'requested_date': date_requested,
                        'effective_date': date_effective,
                        }
                if order.supplier_id and picking.state != 'cancel' \
                        and not picking.supplier_id:
                    vals.update({'supplier_id': order.supplier_id.id})
                picking.write(vals)
        return res

    @api.multi
    def onchange_partner_id(self, part):
        res = super(SaleOrder, self).onchange_partner_id(part)
        if not part:
            res['value']['project_id'] = False
            res['value']['partner_invoice_id'] = False
            res['value']['user_id'] = False
            res['value']['supplier_cip'] = False
            return res
        partner = self.env['res.partner'].browse(part)
        date=datetime.now().strftime('%Y-%m-%d')
        company_id = self.env.user.company_id.id
        rec = self.env['account.analytic.default'].account_get(
                    product_id=False, partner_id=partner.commercial_partner_id.id,
                    user_id=self._uid, date=date, company_id=company_id)
        res['value']['project_id'] = rec and rec.analytic_id.id or False
        res['value']['supplier_cip'] = partner.commercial_partner_id.supplier_cip
        # Modificamos para que la dirección de factura sea la que tenga la empresa padre
        addr = partner.commercial_partner_id.address_get(['invoice'])
        res['value']['partner_invoice_id'] = addr['invoice']
        dedicated_salesman = False
        if res['value'].get('partner_shipping_id', False):
            part_ship_id = res['value']['partner_shipping_id']
            partner_ship = self.env['res.partner'].browse(part_ship_id)
            dedicated_salesman = partner_ship.user_id and \
                partner_ship.user_id.id or False
        if dedicated_salesman:
            res['value']['user_id'] = dedicated_salesman
        return res

    @api.multi
    def onchange_delivery_id(self, company_id, partner_id, delivery_id, fiscal_position):
        res = super(SaleOrder, self).onchange_delivery_id(
                company_id, partner_id, delivery_id, fiscal_position)
        if delivery_id:
            partner_ship = self.env['res.partner'].browse(delivery_id)
            res['value']['user_id'] = partner_ship.user_id and \
                partner_ship.user_id.id or \
                (partner_ship.commercial_partner_id.user_id and
                    partner_ship.commercial_partner_id.user_id.id or False)
        return res

    @api.multi
    def onchange_partner_id3(self, part, early_payment_discount=False, payment_term=False, shop=False):
        res = self.onchange_partner_id2(part, early_payment_discount, payment_term)
        partner_id = self.env['res.partner'].browse(part)
        commercial_partner_id = partner_id.commercial_partner_id
        if not part:
            res['value']['pricelist_id'] = False
            return res
        if shop:
            shop_id = self.env['sale.shop'].browse(shop)
            if shop_id.pricelist_id:
                res['value']['pricelist_id'] = shop_id.pricelist_id.id
            if shop_id.indirect_invoicing:
                if commercial_partner_id.property_product_pricelist_indirect_invoicing:
                    res['value']['pricelist_id'] = \
                        commercial_partner_id.property_product_pricelist_indirect_invoicing.id
            else:
                if commercial_partner_id.property_product_pricelist:
                    res['value']['pricelist_id'] = \
                        commercial_partner_id.property_product_pricelist.id
            domain = [
                ('partner_id', '=', commercial_partner_id.id),
                ('shop_id', '=', shop_id.id)
            ]
            partner_shop_ids = self.env['partner.shop.payment'].search(domain, limit=1)
            if partner_shop_ids.customer_payment_mode:
                res['value']['payment_mode_id'] = partner_shop_ids.customer_payment_mode.id
                res['value']['payment_term'] = partner_shop_ids.customer_payment_term.id
        else:
            res['value']['pricelist_id'] = \
                commercial_partner_id.property_product_pricelist.id
        return res

    @api.multi
    def update_effective_date(self):
        for order in self:
            pickings = order.picking_ids.filtered(lambda r: r.state != 'cancel' and r.effective_date)
            dates_list = pickings.mapped('effective_date')
            min_date = dates_list and min(dates_list) or False
            if order.effective_date != min_date:
                order.effective_date = min_date

    @api.model
    def _prepare_invoice(self, order, lines):
        inv_vals = super(SaleOrder, self)._prepare_invoice(order, lines)
        inv_vals.update({
            'supplier_cip': order.supplier_cip,
            })
        return inv_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='',
            partner_id=False,
            lang=False, update_tax=True, date_order=False,
            packaging=False,
            fiscal_position=False, flag=False):
        """
        Heredamos para poner por defecto una unidad de venta y convertir a unidad principal
        """
        if not product:
            return {'value': {'th_weight': 0,
                    'product_uos_qty': qty}, 'domain': {'product_uom': [],
                    'product_uos': []}}
        prod_obj = self.env['product.product'].browse(product)
        set_uos = False
        if not uos and prod_obj.uos_id:
            uos = prod_obj.uos_id.id
            qty_uos = 1.0
            uom = False  # Hará que haga la conversión de uos a uom
            set_uos = True
        res = super(SaleOrderLine, self).product_id_change(
                pricelist, product, qty=qty,
                uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id,
                lang=lang, update_tax=update_tax, date_order=date_order,
                packaging=packaging,
                fiscal_position=fiscal_position, flag=flag)
        if set_uos:
            res['value']['product_uos_qty'] = 1.0
            res['value']['product_uos'] = uos
        return res

    @api.multi
    def product_uom_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        """
        Modificamos para que solo permita seleccionar una unidad de medida de la misma categoría y si
        se selecciona una de diferente categoría pone la que tiene por defecto el producto.
        Lo usamos también para la unidad de venta. En este caso si cambia ponemos siempre la asignada en el producto.
        Última modificación: se comenta la parte de la categoría y se añade uom = product_obj.uom_id.id or False para que no se pueda
        cambiar la unidad de medida por defecto tampoco en la venta. (no se pone readonly=True en la vista porque sino no se guarda el valor)
        Con todo esto evitamos sobre todo problemas en precios en facturas (_get_price_unit_invoice)
        """
        if product:
            product_obj = self.env['product.product'].browse(product)
            uom = product_obj.uom_id and product_obj.uom_id.id or False
            uos = product_obj.uos_id and product_obj.uos_id.id or False

        res = super(SaleOrderLine, self).product_uom_change(
                pricelist, product, qty, uom, qty_uos, uos, name,
                partner_id, lang, update_tax, date_order)

        res['value']['product_uom'] = uom
        res['value']['product_uos'] = uos

        if product:
            res['domain'] = {'product_uom': [('category_id', '=', product_obj.uom_id.category_id.id)]} #Esto sobra porque tenemos fijada la uom y no se permite cambiar
        return res


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    sale_line_id = fields.Many2one(select=True) # Redefine index

