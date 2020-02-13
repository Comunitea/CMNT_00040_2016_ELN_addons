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
        warehouse_id = vals.get('warehouse_id', False)
        channel = vals.get('chanel', False)
        note = vals.get('note', '').replace('Nota: ', '').replace('Nota:', '')

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
            'user_id': partner.user_id.id,
            'note': False,
            'shop_id': shop_id,
            'warehouse_id': warehouse_id,
            'channel': channel,
            'company_id': company_id.id,
            'note': note,
        }
        # Se van a ejecutar los onchanges de la cabecera para actualizar valores
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
        order_line = vals.get('order_line', [])

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
            line_values = {
                'product_id': product_id,
                'name': ' ' or False,
                'product_uom_qty': product_uom_qty,
                'product_uom': uom_id,
                'product_uos_qty': product_uos_qty,
                'product_uos': uos_id,
                'price_unit': price_unit,
                'discount': discount,
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
        )
        values['order_line'] = order_lines
        # Creamos el pedido
        order_id = sale_obj.with_context(ctx).create(values)
        # onchange shop_id (se hace al final porque está con API nueva
        order_id.onchange_shop_id()
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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """
        La función search tiene que ser llamada con API antigua para que funcione la APP.
        En el módulo l10n_es_partner es llamada con API nueva, por tanto tenemos que parchearla
		heredándola y llamámdola con API antigua.
		Nota: poner el módulo donde es llamada con API nueva como dependencia y heredar
        """
        return super(ResPartner, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)

