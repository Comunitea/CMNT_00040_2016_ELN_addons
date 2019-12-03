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

    chanel = fields.Selection([
        ('erp', 'ERP'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
        ('ecomerce', 'E-commerce')
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
        
        shop_id = vals.get('shop_id', False)
        if not shop_id:
            ir_values = self.env['ir.values']
            company_id = self.env.user.company_id.id
            shop_id = ir_values.get_default('sale.order', 'shop_id', company_id=company_id)

        create_date = vals.get('create_date', False) or fields.Datetime.now()
        date_order = vals.get('date_order', False) or fields.Datetime.now()
        requested_date = vals.get('requested_date', False)
        client_order_ref = vals.get('client_order_ref', False)
        pricelist_id = vals.get('pricelist_id', False)
        warehouse_id = vals.get('warehouse_id', False)
        chanel = vals.get('chanel', False)

        values = {
            'create_date': create_date,
            'date_order': date_order,
            'requested_date': requested_date,
            'client_order_ref': client_order_ref,
            'partner_id': partner.id,
            'partner_invoice_id': invoice_dir,
            'partner_shipping_id': shipping_dir.id,
            'pricelist_id': pricelist_id,
            'fiscal_position': partner.property_account_position.id,
            'payment_term': partner.property_payment_term.id,
            'payment_mode_id': partner.customer_payment_mode.id,
            'early_payment_discount': False,
            'user_id' : partner.user_id.id,
            'note': False,
            'shop_id': shop_id,
            'warehouse_id': warehouse_id,
            'chanel': chanel,
        }
        # Se van a ejecutar los onchanges de la cabecera para actualizar valores
        data = {}
        data.update(
            sale_obj.onchange_partner_id3(
                partner.id, False, partner.property_payment_term.id,
                shop_id)['value']
        )
        if 'partner_shipping_id' in data and data['partner_shipping_id']:
            del data['partner_shipping_id']
        values.update(data)
        order_id = sale_obj.create(values)
        order_id.onchange_shop_id()
        dp = self.env['decimal.precision'].precision_get('Product Price')
        order_line = vals.get('order_line', [])
        for line in order_line:
            product_id = line[2]['product_id']
            product_uom_qty = line[2]['product_uom_qty']
            product_uos_qty = line[2]['product_uos_qty']
            uom_id = line[2]['product_uom']
            uos_id = line[2]['product_uos']
            price_unit = round(line[2]['price_unit'], dp)
            discount = round(line[2]['discount'], 2)
            values = {
                'order_id': order_id.id,
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
            data = {}
            # Llamo al onchange del producto
            ctx = dict(
                self._context,
                partner_id=order_id.partner_id.id,
                address_id=shipping_dir.id,
                fiscal_position=order_id.fiscal_position.id,
                quantity=product_uom_qty,
                pricelist=order_id.pricelist_id.id,
                shop=order_id.shop_id.id,
                uom=False
            )
            data.update(
                order_id.order_line.with_context(ctx).product_id_change(
                    order_id.pricelist_id.id, product_id, product_uom_qty,
                    uom_id, product_uos_qty, uos_id, '', order_id.partner_id.id,
                    False, True, order_id.date_order,
                    False, order_id.fiscal_position.id, False)['value']
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
            values.update(data)
            # Contexto para que asigne las comisiones
            ctx = dict(
                self._context,
                partner_id=partner.id,
                address_id=shipping_dir.id
            )
            line_id = sale_line_obj.with_context(ctx).create(values)
        res = order_id
        if res:
            # Para diferenciar del estado 'draft' ponemos el estado como 'quotation_sent'
            # Otra opción es dejar el estado como 'draft' y filtrar por el campo chanel 
            res.signal_workflow('quotation_sent')
            _logger.info("APP. Respuesta a create_and_confirm <%s> " %(res))
            return res.id
        _logger.info("APP. Respuesta ERROR!! create_and_confirm <%s> " %(res))
        return False


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

