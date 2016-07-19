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
from dateutil import tz
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
import time
from openerp import api


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def _get_effective_date(self, cr, uid, ids, name, arg, context=None):
        """Read the shipping effective date from the related packings"""
        res = {}
        dates_list = []
        for order in self.browse(cr, uid, ids, context=context):
            dates_list = []
            for pick in order.picking_ids:
                dates_list.append(pick.effective_date)
            if dates_list:
                res[order.id] = min(dates_list)
            else:
                res[order.id] = False
        return res

    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,domain = [('supplier','=',True)],states={'draft': [('readonly', False)]}, select=True),
        'order_policy': fields.selection([
            ('prepaid', 'Pay before delivery'),
            ('manual', 'Deliver & invoice on demand'),
            ('picking', 'Invoice based on deliveries'),
            ('postpaid', 'Invoice on order after delivery'),
            ('no_bill', 'No bill')
        ], 'Invoice Policy', required=True, readonly=True, states={'draft': [('readonly', False)]}, change_default=True),
        'supplier_cip': fields.char('CIP', help="Código interno del proveedor.", size=32, readonly=True, states={'draft': [('readonly', False)],'waiting_date': [('readonly', False)],'manual': [('readonly', False)],'progress': [('readonly', False)]}),
        'shop_id': fields.many2one('sale.shop', 'Sale type', required=True),
        'commercial_partner_id': fields.many2one('res.partner', invisible=True),
        'effective_date': fields.function(_get_effective_date, type='date',
            store=True, string='Effective Date',
            help="Date on which the first Delivery Order was delivered."),
    }

    def onchange_shop_id(self, cr, uid, ids, shop_id):
        v = {}
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
            v['project_id'] = shop.project_id.id
            v['company_id'] = shop.company_id.id
            # overriden by the customer priceslist if existing
            if shop.pricelist_id.id:
                v['pricelist_id'] = shop.pricelist_id.id
            if shop.supplier_id.id:
                v['supplier_id'] = shop.supplier_id.id
            if shop.order_policy:
                v['order_policy'] = shop.order_policy
            if shop.warehouse_id:
                v['warehouse_id'] = shop.warehouse_id.id
            v['order_policy'] = shop.order_policy
            v['supplier_id'] = shop.supplier_id.id

        return {'value': v}

    def onchange_shop_id2(self, cr, uid, ids, shop_id, partner_id=False, project_id=False):
        res = self.onchange_shop_id(cr, uid, ids, shop_id)
        if project_id:
            res['value']['project_id'] = project_id
        if not shop_id:
            res['value']['pricelist_id'] = False
            return res

        if partner_id:
            shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop_id)
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)

            if shop_obj.indirect_invoicing:
                if partner_obj.property_product_pricelist_indirect_invoicing:
                    res['value']['pricelist_id'] = partner_obj.property_product_pricelist_indirect_invoicing.id
            else:
                if partner_obj.property_product_pricelist:
                    res['value']['pricelist_id'] = partner_obj.property_product_pricelist.id

        return res

    def action_ship_create(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_ship_create(cr, uid, ids,
                                                         context=context)
        user_tz = self.pool['res.users'].browse(cr, uid, uid).tz
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(user_tz)
        for order in self.browse(cr, uid, ids):
            if order.picking_ids:
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
                    self.pool.get('stock.picking').write(cr, uid, picking.id,
                                                         vals)
        return res

    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context)
        company_id = self.pool.get('res.users').browse(cr, uid, [uid]).company_id.id
        partner = self.pool.get('res.partner').browse(cr, uid, part)
        commercial_partner = partner.commercial_partner_id.id
        rec = self.pool.get('account.analytic.default').account_get(cr, uid, product_id=False, partner_id=commercial_partner, user_id=uid,
                                                                    date=time.strftime('%Y-%m-%d'),company_id=company_id, context={})
        if rec:
            res['value']['project_id'] = rec.analytic_id.id
        else:
            res['value']['project_id'] = False

        #Modificamos para que la dirección de factura sea la que tenga la empresa padre
        addr = self.pool.get('res.partner').address_get(cr, uid, [commercial_partner], ['invoice'])
        res['value']['partner_invoice_id'] = \
            addr['invoice']
        dedicated_salesman = False
        if res['value'].get('partner_shipping_id', False):
            part_ship_id = res['value']['partner_shipping_id']
            partner_ship = self.pool.get('res.partner').browse(cr, uid,
                                                               part_ship_id)
            dedicated_salesman = partner_ship.user_id and \
                partner_ship.user_id.id or False
        if dedicated_salesman:
            res['value']['user_id'] = dedicated_salesman
        return res

    def onchange_delivery_id(self, cr, uid, ids, company_id, partner_id,
                             delivery_id, fiscal_position, context=None):
        res = super(sale_order, self).onchange_delivery_id(cr, uid, ids,
                                                           company_id,
                                                           partner_id,
                                                           delivery_id,
                                                           fiscal_position,
                                                           context=context)
        if delivery_id:
            partner_ship = self.pool.get('res.partner').browse(cr, uid,
                                                               delivery_id,
                                                               context)
            res['value']['user_id'] = partner_ship.user_id and \
                partner_ship.user_id.id or \
                (partner_ship.commercial_partner_id.user_id and
                    partner_ship.commercial_partner_id.user_id.id or False)
        return res

    def onchange_partner_id3(self, cr, uid, ids, part, early_payment_discount=False, payment_term=False, shop=False):
        """extend this event for change the pricelist when the shop is to indirect invoice"""
        res = self.onchange_partner_id2(cr, uid, ids, part, early_payment_discount, payment_term)
        partner_obj = self.pool.get('res.partner').browse(cr, uid, part)
        res['value']['commercial_partner_id'] = \
            partner_obj.commercial_partner_id.id
        if not part:
            res['value']['pricelist_id'] = False
            return res

        if shop:
            shop_obj = self.pool.get('sale.shop').browse(cr, uid, shop)

            if shop_obj.pricelist_id and shop_obj.pricelist_id.id:
                res['value']['pricelist_id'] = shop_obj.pricelist_id.id

            if shop_obj.indirect_invoicing:
                if partner_obj.commercial_partner_id.property_product_pricelist_indirect_invoicing:
                    res['value']['pricelist_id'] = \
                        partner_obj.commercial_partner_id.property_product_pricelist_indirect_invoicing.id
            else:
                if partner_obj.commercial_partner_id.property_product_pricelist:
                    res['value']['pricelist_id'] = \
                        partner_obj.commercial_partner_id.property_product_pricelist.id
        else:
            res['value']['pricelist_id'] = \
                partner_obj.commercial_partner_id.property_product_pricelist.id


        return res

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def product_uos_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, fpos=False, context=None):
        res = {}
        if context is None:
            context = {}
        if product:
            product_obj = self.pool.get('product.product').browse(cursor, user, product)
            if uos:
                qty_uom = 0.0
                if self.pool.get('product.uom').browse(cursor, user, uos).category_id.id == product_obj.uos_id.category_id.id:
                    if qty_uos:
                        if product_obj.uos_coeff:
                            qty_uom = qty_uos / product_obj.uos_coeff
                        if not fpos and partner_id:
                            partner = self.pool.get('res.partner').browse(cursor, user, partner_id, context=context)
                            fpos = partner.property_account_position and partner.property_account_position.id or False
                        res = self.product_id_change(cursor, user, ids, pricelist, product,
                            qty=qty_uom, uom=False, qty_uos=qty_uos, uos=uos, name=name,
                            partner_id=partner_id, lang=lang, update_tax=update_tax,
                            date_order=date_order, fiscal_position=fpos, context=context)
                        if 'product_uom' in res['value']:
                            del res['value']['product_uom']
        return res

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False,
                          lang=False, update_tax=True, date_order=False,
                          packaging=False,
                          fiscal_position=False, flag=False, context=None):
        """
        Heredamos para poner por defecto una unidad de venta y convertir a unidad principal
        """
        if not product:
            return {'value': {'th_weight': 0,
                    'product_uos_qty': qty}, 'domain': {'product_uom': [],
                    'product_uos': []}}
        prod_obj = self.pool.get('product.product').browse(cr, uid, product,
                                                           context=context)
        set_uos = False
        if not uos and prod_obj.uos_id:
            uos = prod_obj.uos_id.id
            qty_uos = 1.0
            uom = False  # Hará que haga la conversión de uos a uom
            set_uos = True

        res = super(sale_order_line, self).product_id_change(cr, uid, ids,
                                                             pricelist, product, qty=qty,
                                                             uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                                                             partner_id=partner_id,
                                                             lang=lang, update_tax=update_tax, date_order=date_order,
                                                             packaging=packaging,
                                                             fiscal_position=fiscal_position, flag=flag, context=context)
        if set_uos:
            res['value']['product_uos_qty'] = 1.0
            res['value']['product_uos'] = uos
        return res

    def product_uom_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        """
        Modificamos para que solo permita seleccionar una unidad de medida de la misma categoría y si
        se selecciona una de diferente categoría pone la que tiene por defecto el producto.
        Lo usamos también para la unidad de venta. En este caso si cambia ponemos siempre la asignada en el producto.
        Última modificación: se comenta la parte de la categoría y se añade uom = product_obj.uom_id.id or False para que no se pueda
        cambiar la unidad de medida por defecto tampoco en la venta. (no se pone readonly=True en la vista porque sino no se guarda el valor)
        Con todo esto evitamos sobre todo problemas en precios en facturas (_get_price_unit_invoice)
        """
        if product:
            product_obj = self.pool.get('product.product')
            product_obj = product_obj.browse(cr, uid, product, context=context)
            uom = product_obj.uom_id and product_obj.uom_id.id or False
            uos = product_obj.uos_id and product_obj.uos_id.id or False

        res = super(sale_order_line, self).product_uom_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, context)

        res['value']['product_uom'] = uom
        res['value']['product_uos'] = uos

        if product:
            res['domain'] = {'product_uom': [('category_id', '=', product_obj.uom_id.category_id.id)]} #Esto sobra porque tenemos fijada la uom y no se permite cambiar

        return res
