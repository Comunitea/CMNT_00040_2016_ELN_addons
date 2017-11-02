# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import base64, StringIO, csv
from openerp.osv import orm, fields, osv
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp import _
from openerp import netsvc
import time
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class sale_order_import(orm.TransientModel):
    _name = 'sale.order.import'
    _description = 'Import sale order from file'
    _columns = {
        'file': fields.binary('File', required=True),
        'file_name': fields.char('Filename', size=128, required=True),
        'file_type': fields.selection([('model_apolo','Exclusivas Apolo')], 'File type', required=True),
        'import_actions': fields.selection([('sale','Create sale order'),('sale_and_picking','Create sale order and stock picking')], 'Actions to do', required=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=False),
        'note': fields.text('Log'),
    }
    _defaults = {
        'file_name': '',
    }

    def onchange_file_type(self, cr, uid, ids, file_type):
        res = {}
        shop_obj = self.pool.get('sale.shop')
        if file_type == 'model_apolo':
            shop_id = shop_obj.search(cr, uid, [('name', 'ilike', 'apolo')]) or False
            import_actions = 'sale'
        else:
            shop_id = False
            import_actions = False
        res['value'] = {'shop_id': shop_id and shop_id[0] or False, 'import_actions': import_actions}
        return res

    def sale_order_import(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')
        result_view = mod_obj.get_object_reference(cr, uid, 'sale_order_import', 'sale_order_import_result_view')
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product UoS')

        for wizard in self.browse(cr, uid, ids , context):
            #import ipdb; ipdb.set_trace()
            if wizard.file_type == 'model_apolo':
                csv_separator = '|'
                decimal_separator = ','
                lines = base64.decodestring(wizard.file)
                try:
                    unicode(lines, 'utf8')
                except Exception, ex: # Si no puede convertir a UTF-8 es que debe estar en ISO-8859-1: Lo convertimos
                    lines = unicode(lines, 'iso-8859-1').encode('utf-8')
                reader = csv.reader(StringIO.StringIO(lines), delimiter=csv_separator)

                picking_i = 0
                date_i = 1
                order_ref_i = 2
                partner_code_i = 3
                product_code_i = 4
                sign_i = 5
                quantity_i = 6
                lot_i = 7

                old_picking = ''
                err_log = ''
                sales_created = []

                for ln in reader:
                    if not ln or ln and ln[0] and ln[0][0] in ['', '#']:
                        continue
                    if ln[sign_i] == '-' or ln[picking_i] == '': # Solo vamos a procesar lineas positivas y con numero de albaran
                        continue
                    if ln[picking_i] != old_picking: # Cabecera
                        if (sale_obj.search(cr, uid, [('origin', '=', ('ALB.' + ln[picking_i])), ('state', '!=', 'cancel')]) or False): # Ya existe el albaran en el sistema
                            _logger.info(_("Error: document '%s' is already in the system!") %(ln[picking_i]))
                            err_msg = _("Error processing sale with origin '%s': document is already in the system!") %(ln[picking_i])
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue
                        partner_id = self.pool.get('res.partner').search(cr, uid, [('ref', '=', ln[partner_code_i].strip())]) or False
                        if not partner_id:
                            _logger.info(_("Error: customer with ref '%s' not found!") %(ln[partner_code_i].strip()))
                            err_msg = _("Error processing sale with origin '%s': customer with ref '%s' not found!") %(ln[picking_i], ln[partner_code_i].strip())
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue

                        old_picking = ln[picking_i]

                        shipping_dir = self.pool.get('res.partner').browse(cr, uid, partner_id, context)
                        partner = shipping_dir.parent_id and self.pool.get('res.partner').browse(cr, uid, shipping_dir.parent_id.id, context) or shipping_dir
                        addr = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['delivery', 'invoice', 'contact'])
                        invoice_dir = addr['invoice']

                        if not partner.property_product_pricelist:
                            _logger.info(_("Error: customer with ref '%s' whitout pricelist!") %(ln[partner_code_i].strip()))
                            err_msg = _("Error processing sale with origin '%s': customer with ref '%s' whithout pricelist!") %(ln[picking_i], ln[partner_code_i].strip())
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue
                        
                        values = {
                            'date_order': datetime.strptime(ln[date_i], '%d%m%Y').strftime('%Y-%m-%d') or time.strftime('%Y-%m-%d'),
                            'requested_date': datetime.strptime(ln[date_i], '%d%m%Y').strftime('%Y-%m-%d') or time.strftime('%Y-%m-%d'),
                            'shop_id': wizard.shop_id.id,
                            'client_order_ref': ln[order_ref_i].strip() or False,
                            'partner_id': partner.id,
                            'partner_invoice_id': invoice_dir,
                            'partner_shipping_id': shipping_dir.id,
                            'pricelist_id': partner.property_product_pricelist.id,
                            'fiscal_position': partner.property_account_position.id,
                            'payment_term': partner.property_payment_term.id,
                            'payment_mode_id': partner.customer_payment_mode.id,
                            'early_payment_discount': 0.0,
                            'user_id' : partner.user_id and partner.user_id.id or uid,
                            'origin' : ('ALB.' + ln[picking_i]),
                            'note': "",
                        }
                        order_id = sale_obj.create(cr, uid, values)
                        sales_created.append(order_id)
                        # Ahora voy a ejecutar los onchanges para actualizar valores
                        data = {}
                        data.update(sale_obj.onchange_shop_id2(cr, uid, [order_id], wizard.shop_id.id, partner.id)['value'])
                        data.update(sale_obj.onchange_partner_id2(cr, uid, [order_id], partner.id, 0.0, partner.property_payment_term.id, context)['value'])
                        if 'partner_shipping_id' in data and data['partner_shipping_id']:
                            del data['partner_shipping_id']
                        sale_obj.write(cr, uid, [order_id], data)
                        _logger.info(_("Created sale order with origin '%s'.") %(ln[picking_i]))

                    # Creamos lineas de pedido
                    product_id = product_obj.search(cr, uid, [('default_code', '=', ln[product_code_i].strip())]) or False
                    if not product_id:
                        _logger.info(_("Error: product with ref '%s' not found!") %(ln[product_code_i].strip()))
                        err_msg = _("Error processing sale with origin '%s': product with ref '%s' not found!") %(ln[picking_i], ln[product_code_i].strip())
                        if not (err_log.find(err_msg) >= 0):
                            err_log += '\n' + err_msg
                        continue
                    if len(product_id) > 1:
                        _logger.info(_("Error: product with ref '%s' found multiple times!") %(ln[product_code_i].strip()))
                        err_msg = _("Error processing sale with origin '%s': product with ref '%s' found multiple times!") %(ln[picking_i], ln[product_code_i].strip())
                        if not (err_log.find(err_msg) >= 0):
                            err_log += '\n' + err_msg
                        continue
                    product_uom_qty = round(str2float(ln[quantity_i], decimal_separator), dp)

                    product_aux = product_obj.browse(cr, uid, [product_id[0]])[0]
                    t_uom = self.pool.get('product.uom')
                    uom_id = product_aux.uom_id and product_aux.uom_id.id
                    uos_id = product_aux.uos_id and product_aux.uos_id.id

                    #si la unidad es kg interpretamos que la cantidad la pasan en UdV
                    #se le avisara para que la pasen en UdM
                    #Por tanto convertimos la cantidad a UdM
                    kgm_uom = self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, 'product.product_uom_kgm')
                    if uom_id == kgm_uom:
                        product_uom_qty = t_uom._compute_qty(cr, uid, uos_id, product_uom_qty, uom_id)
                    #FIN conversion graneles
                    product_uos_qty = t_uom._compute_qty(cr, uid, uom_id, product_uom_qty, uos_id)
                    values = {
                        'order_id': order_id,
                        'product_id': product_id[0],
                        'name': ' ' or False,
                        'product_uom_qty': product_uom_qty,
                        'product_uom': uom_id,
                        'product_uos_qty': product_uos_qty,
                        'product_uos': uos_id,
                        'pre_prodlot': ln[lot_i].strip() or False,
                    }
                    c = context.copy()
                    c.update(partner_id=partner.id, address_id=shipping_dir.id)
                    line_id = sale_line_obj.create(cr, uid, values, c)
                    so = sale_obj.browse(cr, uid, order_id)
                    # Ahora voy a ejecutar los onchanges para actualizar valores
                    data = {}
                    #Llamo al onchange del producto
                    ctx = dict(context, partner_id=so.partner_id.id, quantity=product_uom_qty,
                                   pricelist=so.pricelist_id.id, shop=so.shop_id.id, uom=False)  # FALSE SHOP POST-MIGRATION
                    data.update(sale_line_obj.product_id_change(cr, uid, [line_id], so.pricelist_id.id, product_id[0], product_uom_qty,
                                                                uom_id, product_uos_qty, uos_id, '', so.partner_id.id, False, True, so.date_order,
                                                                False, so.fiscal_position.id, False, context=ctx)['value'])
                    if 'product_uom_qty' in data and data['product_uom_qty']:
                        del data['product_uom_qty']
                    if 'tax_id' in data and data['tax_id']:
                        data['tax_id'] = [(6, 0, data['tax_id'])]
                    #En lugar de hacer write sobre la linea lo hago sobre la cabecera para que dispare correctamente algunos campos funcion como el descuento por pronto pago
                    #sale_line_obj.write(cr, uid, [line_id], data)
                    sale_obj.write(cr, uid, [order_id], {'order_line': [(1, line_id, data)]})
                    #-------
                    _logger.info(_("Created sale order line with origin '%s' and product '%s'.") %(so.name, ln[product_code_i].strip()))
                _logger.info(u"<-------------------  IMPORT PROCESS END  ------------------->" )
                if wizard.import_actions == 'sale_and_picking':
                    wf_service = netsvc.LocalService("workflow")
                    for sale_id in sales_created:
                        so = sale_obj.browse(cr, uid, sale_id)
                        if so and so.order_line and so.state == 'draft':
                            _logger.info(_("Confirming sale order with id '%s'.") %(sale_id))
                            wf_service.trg_validate(uid, 'sale.order', sale_id, 'order_confirm', cr) #Suponemos que los pedidos ya se han servido y no comprobamos riesgo
                            #wf_service.trg_validate(uid, 'sale.order', sale_id, 'draft_to_risk', cr)

        if err_log:
            self.write(cr, uid, ids[0], {'note': err_log})
            return {
                'name': _('Import File result'),
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.import',
                'view_id': [result_view[1]],
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        else:
            err_log = _("No errors were found.")
            err_log += '\n' + _("Import process completed successfully.")
            self.write(cr, uid, ids[0], {'note': err_log})
            return {
                'name': _('Import File result'),
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.import',
                'view_id': [result_view[1]],
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            #return {'type': 'ir.actions.act_window_close'}

sale_order_import()

def str2float(amount, decimal_separator):
    if not amount:
        return 0.0
    else:
        if decimal_separator == '.':
            return float(amount.replace(',',''))
        else:
            return float(amount.replace('.','').replace(',','.'))
