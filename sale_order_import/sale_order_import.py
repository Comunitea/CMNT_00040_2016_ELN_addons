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

from openerp import models, fields, api, _
import base64, StringIO, csv
from openerp import netsvc
import time
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class SaleOrderImport(models.TransientModel):
    _name = 'sale.order.import'
    _description = 'Import sale order from file'

    file = fields.Binary('File', required=True)
    file_name = fields.Char(string='Filename', size=128, required=True, default='')
    file_type = fields.Selection([
        ('model_apolo', 'Exclusivas Apolo'),
        ], string='File type', required=True)
    import_actions = fields.Selection([
        ('sale', 'Create sale order'),
        ('sale_and_picking', 'Create sale order and stock picking'),
        ], string='Actions to do', required=True, default='sale')
    shop_id = fields.Many2one(string="Shop", comodel_name='sale.shop', required=False)
    note = fields.Text(string='Log')

    @api.onchange('file_type')
    def onchange_file_type(self):
        shop_obj = self.env['sale.shop']
        if self.file_type == 'model_apolo':
            self.shop_id = shop_obj.search([('name', 'ilike', 'apolo')], limit=1) or False
            self.import_actions = 'sale'
        else:
            self.shop_id = False
            self.import_actions = False

    @api.multi
    def sale_order_import(self):
        self = self.with_context(no_check_risk=True)
        mod_obj = self.env['ir.model.data']
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']
        partner_obj = self.env['res.partner']
        result_view = mod_obj.get_object_reference('sale_order_import', 'sale_order_import_result_view')
        dp = self.env['decimal.precision'].precision_get('Product UoS')

        for wizard in self:
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
                        if (sale_obj.search([('origin', '=', ('ALB.' + ln[picking_i])), ('state', '!=', 'cancel')]) or False): # Ya existe el albaran en el sistema
                            _logger.info(_("Error: document '%s' is already in the system!") %(ln[picking_i]))
                            err_msg = _("Error processing sale with origin '%s': document is already in the system!") %(ln[picking_i])
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue
                        partner_id = partner_obj.search([('ref', '=', ln[partner_code_i].strip())]) or False
                        if not partner_id:
                            _logger.info(_("Error: customer with ref '%s' not found!") %(ln[partner_code_i].strip()))
                            err_msg = _("Error processing sale with origin '%s': customer with ref '%s' not found!") %(ln[picking_i], ln[partner_code_i].strip())
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue
                        if len(partner_id) > 1:
                            _logger.info(_("Error: several customers with same ref '%s'!") %(ln[partner_code_i].strip()))
                            err_msg = _("Error processing sale with origin '%s': several customers with same ref '%s'!") %(ln[picking_i], ln[partner_code_i].strip())
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue

                        old_picking = ln[picking_i]

                        shipping_dir = partner_id
                        partner = shipping_dir.commercial_partner_id
                        addr = partner.address_get(['delivery', 'invoice', 'contact'])
                        invoice_dir = addr['invoice']

                        if wizard.shop_id.indirect_invoicing:
                            pricelist_id = partner.property_product_pricelist_indirect_invoicing
                        else:
                            pricelist_id = partner.property_product_pricelist
                        pricelist_id = pricelist_id or wizard.shop_id.pricelist_id

                        if not pricelist_id:
                            _logger.info(_("Error: customer with ref '%s' without pricelist!") %(ln[partner_code_i].strip()))
                            err_msg = _("Error processing sale with origin '%s': customer with ref '%s' without pricelist!") %(ln[picking_i], ln[partner_code_i].strip())
                            if not (err_log.find(err_msg) >= 0):
                                err_log += '\n' + err_msg
                            continue
                        
                        values = {
                            'date_order': datetime.strptime(ln[date_i], '%d%m%Y').strftime('%Y-%m-%d') or time.strftime('%Y-%m-%d'),
                            'requested_date': datetime.strptime(ln[date_i], '%d%m%Y').strftime('%Y-%m-%d') or time.strftime('%Y-%m-%d'),
                            'client_order_ref': ln[order_ref_i].strip() or False,
                            'partner_id': partner.id,
                            'partner_invoice_id': invoice_dir,
                            'partner_shipping_id': shipping_dir.id,
                            'pricelist_id': pricelist_id.id,
                            'fiscal_position': partner.property_account_position.id,
                            'payment_term': partner.property_payment_term.id,
                            'payment_mode_id': partner.customer_payment_mode.id,
                            'early_payment_discount': False,
                            'user_id' : partner.user_id and partner.user_id.id or self.env.uid,
                            'origin' : ('ALB.' + ln[picking_i]),
                            'note': "",
                            'shop_id': wizard.shop_id.id,
                            'project_id': wizard.shop_id.project_id.id,
                            'supplier_id': wizard.shop_id.supplier_id.id,
                            'order_policy': wizard.shop_id.order_policy,
                            'warehouse_id': wizard.shop_id.warehouse_id.id,
                        }
                        # Ahora voy a ejecutar los onchanges para actualizar valores
                        data = {}
                        data.update(
                            sale_obj.onchange_partner_id3(
                                partner.id, False, partner.property_payment_term.id,
                                wizard.shop_id.id)['value']
                        )
                        if 'partner_shipping_id' in data and data['partner_shipping_id']:
                            del data['partner_shipping_id']
                        values.update(data)
                        order_id = sale_obj.create(values)
                        sales_created.append(order_id)
                        _logger.info(_("Created sale order with origin '%s'.") %(ln[picking_i]))
                    # Creamos lineas de pedido
                    product_id = product_obj.search([('default_code', '=', ln[product_code_i].strip())]) or False
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

                    t_uom = self.env['product.uom']
                    uom_id = product_id.uom_id and product_id.uom_id.id
                    uos_id = product_id.uos_id and product_id.uos_id.id

                    # si la unidad es kg interpretamos que la cantidad la pasan en UdV
                    # se le avisara para que la pasen en UdM
                    # Por tanto convertimos la cantidad a UdM
                    kgm_uom = mod_obj.xmlid_to_res_id('product.product_uom_kgm')
                    if uom_id == kgm_uom:
                        product_uom_qty = t_uom._compute_qty(uos_id, product_uom_qty, uom_id)
                    # FIN conversion graneles
                    product_uos_qty = t_uom._compute_qty(uom_id, product_uom_qty, uos_id)
                    values = {
                        'order_id': order_id.id,
                        'product_id': product_id.id,
                        'name': ' ' or False,
                        'product_uom_qty': product_uom_qty,
                        'product_uom': uom_id,
                        'product_uos_qty': product_uos_qty,
                        'product_uos': uos_id,
                        'pre_prodlot': ln[lot_i].strip() or False,
                    }
                    # Ahora voy a ejecutar los onchanges para actualizar valores
                    data = {}
                    # Llamo al onchange del producto
                    ctx = dict(partner_id=order_id.partner_id.id, quantity=product_uom_qty,
                               pricelist=order_id.pricelist_id.id, shop=order_id.shop_id.id, uom=False)
                    data.update(
                        order_id.order_line.with_context(ctx).product_id_change(
                            order_id.pricelist_id.id, product_id.id, product_uom_qty,
                            uom_id, product_uos_qty, uos_id, '', order_id.partner_id.id, False, True, order_id.date_order,
                            False, order_id.fiscal_position.id, False)['value']
                    )
                    if 'product_uom_qty' in data and data['product_uom_qty']:
                        del data['product_uom_qty']
                    if 'tax_id' in data and data['tax_id']:
                        data['tax_id'] = [(6, 0, data['tax_id'])]
                    values.update(data)
                    ctx = dict(partner_id=partner.id, address_id=shipping_dir.id) # Para comisiones
                    line_id = sale_line_obj.with_context(ctx).create(values)
                    _logger.info(_("Created sale order line with origin '%s' and product '%s'.") %(order_id.name, ln[product_code_i].strip()))
                _logger.info(u"<-------------------  IMPORT PROCESS END  ------------------->" )
                if wizard.import_actions == 'sale_and_picking':
                    wf_service = netsvc.LocalService("workflow")
                    for order_id in sales_created:
                        if order_id and order_id.order_line and order_id.state == 'draft':
                            _logger.info(_("Confirming sale order with id '%s'.") %(order_id.id))
                            wf_service.trg_validate(self.env.uid, 'sale.order', order_id.id, 'order_confirm', self.env.cr) # Suponemos que los pedidos ya se han servido y no comprobamos riesgo
                            #wf_service.trg_validate(self.env.uid, 'sale.order', order_id.id, 'draft_to_risk', self.env.cr)

        if err_log:
            wizard.note = err_log
            return {
                'name': _('Import File result'),
                'res_id': wizard.id,
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
            wizard.note = err_log
            return {
                'name': _('Import File result'),
                'res_id':  wizard.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order.import',
                'view_id': [result_view[1]],
                'target': 'new',
                'type': 'ir.actions.act_window',
            }


def str2float(amount, decimal_separator):
    if not amount:
        return 0.0
    else:
        if decimal_separator == '.':
            return float(amount.replace(',',''))
        else:
            return float(amount.replace('.','').replace(',','.'))
