# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Comunitea
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
from dateutil.rrule import rrule
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    channel = fields.Selection([
        ('erp', 'ERP'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
        ('ecommerce', 'E-commerce')
        ], string='Channel', readonly=True)
    app_note = fields.Text(string='App notes')

    @api.model
    def create_and_confirm(self, vals):
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        
        partner_shipping_id = vals.get('partner_shipping_id', False)
        shipping_dir = self.env['res.partner'].browse(partner_shipping_id)
        partner = shipping_dir.commercial_partner_id
        addr = partner.address_get(['delivery', 'invoice', 'contact'])
        invoice_dir = addr['invoice']
        company_id = self.env.user.company_id
        shop_id = vals.get('shop_id', False)
        if not shop_id:
            ir_values = self.env['ir.values']
            shop_id = ir_values.get_default('sale.order', 'shop_id', company_id=company_id.id)
        create_date = vals.get('create_date', False) or fields.Datetime.now()
        date_order = vals.get('date_order', False) or fields.Datetime.now()
        requested_date = vals.get('requested_date', False)
        client_order_ref = vals.get('client_order_ref', False)
        pricelist_id = vals.get('pricelist_id', False)
        warehouse_id = self.env['stock.warehouse'].search([], limit=1) # El valor que envía la app no sirve
        channel = vals.get('channel', False)
        note = vals.get('note', '')
        order_line = vals.get('order_line', [])
        values = {
            'create_date': create_date,
            'date_order': date_order,
            'requested_date': requested_date,
            'client_order_ref': client_order_ref,
            'partner_id': partner.id,
            'partner_invoice_id': invoice_dir,
            'partner_shipping_id': shipping_dir.id,
            'pricelist_id': pricelist_id,
            'fiscal_position': False,
            'payment_term': False,
            'payment_mode_id': False,
            'early_payment_discount': False,
            'user_id': shipping_dir.user_id.id,
            'shop_id': shop_id,
            'warehouse_id': warehouse_id.id,
            'channel': channel,
            'company_id': company_id.id,
            'app_note': note,
        }
        # Creamos el pedido
        order_id = sale_obj.with_context(mail_notrack=True).create(values)
        # Se van a ejecutar los onchanges de la cabecera para actualizar valores
        # onchange shop_id
        order_id.onchange_shop_id()
        read_fields = [
            'date_order', 'partner_id', 'partner_shipping_id', 'pricelist_id',
            'fiscal_position', 'payment_term', 'early_payment_discount',
            'shop_id', 'warehouse_id', 'company_id',
        ]
        values = order_id.read(fields=read_fields, load='_classic_write')[0]
        # onchange partner_id
        data = {}
        data.update(
            sale_obj.with_context(no_check_risk=True).onchange_partner_id3(
                values['partner_id'],
                early_payment_discount=values['early_payment_discount'],
                payment_term=False, shop=values['shop_id'])['value']
        )
        if 'partner_shipping_id' in data and data['partner_shipping_id']:
            del data['partner_shipping_id']
        values.update(data)
        # onchange partner_shipping_id
        data = {}
        data.update(
            sale_obj.onchange_delivery_id(
                values['company_id'],
                values['partner_id'], values['partner_shipping_id'],
                values['fiscal_position'])['value']
        )
        values.update(data)
        dp = self.env['decimal.precision'].precision_get('Product Price')
        # onchange payment_term
        data = {}
        data.update(
            sale_obj.onchange_payment_term(
                values['payment_term'],
                values['partner_id'])['value']
        )
        values.update(data)
        # Consultamos la ruta de transporte y ponemos mensaje fuera de ruta en notas app si procede
        delivery_route_id = shipping_dir.delivery_route_id or \
            shipping_dir.commercial_partner_id.delivery_route_id
        loading_date = delivery_route_id.next_loading_date
        if loading_date:
            today = fields.Date.context_today(self)
            initial_date = datetime.strptime(today, "%Y-%m-%d")
            end_date = datetime.strptime(loading_date, "%Y-%m-%d")
            diff_days = -1 + len(rrule(
                freq=3, # Daily
                byweekday=(0, 1, 2, 3, 4),
                wkst=0,
                dtstart=initial_date,
                until=end_date,
                interval=1)
                .between(initial_date, end_date, inc=True)
            )
            if diff_days == 0:
                app_note = '*** RUTA CARGANDOSE/CARGADA ***' + ((note and '\n' + note) or '')
                values.update({'app_note': app_note})
            elif diff_days > 4:
                app_note = '*** FUERA DE RUTA ***' + ((note and '\n' + note) or '')
                values.update({'app_note': app_note})

        # Obtenemos las lineas del pedido
        order_lines = []
        for line in order_line:
            product_id = line[2]['product_id']
            product_uom_qty = line[2]['product_uom_qty']
            product_uos_qty = line[2]['product_uos_qty']
            uom_id = line[2]['product_uom']
            uos_id = line[2]['product_uos']
            price_unit = round(line[2]['price_unit'], dp)
            discount = round(line[2]['discount'], 2)
            app_discount_type = line[2].get('discount_type', False)
            if app_discount_type not in ('-1', '0', '1', '2', '3'):
                app_discount_type = False
            if app_discount_type == '0' and discount > 0 or app_discount_type == '-1':
                app_discount_type = False
            line_values = {
                'order_id': order_id.id,
                'product_id': product_id,
                'name': '',
                'product_uom_qty': product_uom_qty,
                'product_uom': uom_id,
                'product_uos_qty': product_uos_qty,
                'product_uos': uos_id,
                'price_unit': price_unit,
                'discount': discount,
                'app_discount_type': app_discount_type,
            }
            # Se van a ejecutar los onchanges de las lineas para actualizar valores
            # Llamo al onchange del producto
            data = {}
            ctx = dict(
                self._context,
                partner_id=values['partner_id'],
                address_id=values['partner_shipping_id'],
                fiscal_position=values['fiscal_position'],
                quantity=line_values['product_uom_qty'],
                pricelist=values['pricelist_id'],
                shop=values['shop_id'], # Necesario en eln_partner_discount
                company_id=values['company_id'],
                uom=False
            )
            data.update(
                sale_line_obj.with_context(ctx).product_id_change_with_wh(
                    values['pricelist_id'], product_id, qty=product_uom_qty,
                    uom=uom_id, qty_uos=product_uos_qty, uos=uos_id, name='',
                    partner_id=values['partner_id'],
                    lang=False, update_tax=True, date_order=values['date_order'],
                    packaging=False, fiscal_position=values['fiscal_position'],
                    flag=False, warehouse_id=values['warehouse_id'])['value']
            )
            if 'product_uom_qty' in data:
                del data['product_uom_qty']
            if 'tax_id' in data:
                data['tax_id'] = [(6, 0, data['tax_id'])]
            if 'price_unit' in data:
                del data['price_unit']
            if 'discount' in data:
                if discount: # Hacemos descuento encadenado
                    data['discount'] = 100 - (100 * (1 - data['discount'] / 100) * (1 - discount / 100))
                # del data['discount']
            line_values.update(data)
            order_lines.append((0, 0, line_values))
        # Contexto para que asigne las comisiones en las lineas
        ctx = dict(
            self._context,
            partner_id=values['partner_id'],          # Necesario en módulo sale_commission
            address_id=values['partner_shipping_id'], # Necesario en módulo sale_commission
            mail_notrack=True,
        )
        # Creamos las lineas del pedido
        values['order_line'] = order_lines
        order_id.with_context(ctx).write(values)
        if order_id:
            # Para diferenciar del estado 'draft' ponemos el estado como 'quotation_sent'.
            order_id.signal_workflow('quotation_sent')
            _logger.info("SALES APP: Pedido <%s> OK. Usuario: <%s>" % (order_id.name, self.env.user.name))
            return order_id.id
        _logger.info("SALES APP: ERROR creando pedido. Usuario: <%s>" % (self.env.user.name))
        return False

    @api.model
    def easy_modification(self, order_id, vals):
        # TODO
        _logger.info("SALES APP: ERROR modificando pedido <%s>. Usuario: <%s>" % (vals.get('name', order_id), self.env.user.name))
        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    app_discount_type = fields.Selection([
        ('0', 'Type 0'),
        ('1', 'Type 1'),
        ('2', 'Type 2'),
        ('3', 'Type 3')
        ], string='App disc. type', readonly=True,
        help="Discount type applied from sales app")

    @api.onchange('discount', 'price_unit')
    def onchange_discount(self):
        self.app_discount_type = False

