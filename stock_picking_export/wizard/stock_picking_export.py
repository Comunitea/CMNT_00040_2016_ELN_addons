# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import re
from openerp import models, fields, api, exceptions, _
from datetime import datetime
from unidecode import unidecode


class StockPickingExport(models.TransientModel):
    _name = 'stock.picking.export'
    _description = 'Export pickings to file'

    file_name = fields.Char(string='Filename', size=128, required=True, default='')
    file_type = fields.Selection([
        ('model_salica', 'SALICA'),
        ('model_aspil', 'ASPIL'),
        ('model_mars', 'MARS'),
        ('model_deleben', 'DELEBEN'),
        ], string='File type', required=True)
    note_1 = fields.Text(string='Log')
    note_2 = fields.Text(string='Log')
    data = fields.Binary('File', readonly=True)
    subtract_returns = fields.Boolean(
        string='Subtract returns',
        default=True,
        help="Check this box to subtract related returns to picking")
    sent_to_supplier = fields.Boolean(
        string='Set picking as sent to supplier',
        default=False,
        help="Check this box if the physical delivery note has been sent to the supplier")
    bypass_warnings = fields.Boolean(
        string='Skip warnings',
        default=False,
        help="Check this box to bypass warnings")
    state = fields.Selection([
        ('choose', 'choose'),
        ('get', 'get'),
        ], string='File type', required=True, default='choose')

    @api.model
    def default_get(self, fields):
        res = super(StockPickingExport, self).default_get(fields)
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        file_type = False
        if pickings and pickings[0].supplier_id:
            if not (pickings[0].supplier_id.name.upper().find('SALICA') == -1):
                file_type = 'model_salica'
            elif not (pickings[0].supplier_id.name.upper().find('EXTRUSIONADOS') == -1):
                file_type = 'model_aspil'
            elif not (pickings[0].supplier_id.name.upper().find('MARS') == -1):
                file_type = 'model_mars'
            elif not (pickings[0].supplier_id.name.upper().find('BAHLSEN') == -1):
                file_type = 'model_deleben'
        res.update(file_type=file_type)
        return res


    @api.onchange('file_type')
    def onchange_file_type(self):
        if self.file_type == 'model_salica':
            self.file_name = 'albacli.txt'
        elif self.file_type == 'model_aspil':
            self.file_name = 'aspil_albaranes.xls'
        elif self.file_type == 'model_mars':
            sold_to_mayorista = '17610705' # VQ
            date_now = datetime.now().strftime('%Y%m%d%H%M%S')
            file_name = sold_to_mayorista + date_now + '.txt'
            self.file_name = file_name
        elif self.file_type == 'model_deleben':
            self.file_name = 'LIALBA.txt'
        else:
            self.file_name = 'albaran.txt'

    @staticmethod
    def parse_string(string, length, fill=' ', fill_mode='right'):
        if not string:
            return fill * length
        if isinstance(string, float):
            string = str(string)
            point_pos = string.index('.')
            if len(string[point_pos+1:]) < 2:
                string += '0'
            string = string.replace('.', '')
        else:
            string = unidecode(unicode(string))

        if len(string) > length:
            string = string[:length]

        string = string[0:length]

        if fill_mode == 'left':
            new_string = fill * (length - len(string)) + string
        else:
            new_string = string + fill * (length - len(string))

        if len(new_string) != length:
            raise exceptions.except_orm(_('Error parsing!'), _('The length of "%s" is greater of %s.') % (new_string, length))
        return new_string

    @staticmethod
    def parse_short_date(date_str, date_format='%Y%m%d'):
        if len(date_str) != 10:
            raise exceptions.except_orm(_('Date error'), _('Error parsing short date'))
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime(date_format)

    @staticmethod
    def parse_number(number, int_length, dec_length=0, dec_separator='.',
                     include_sign=False, positive_sign='+', negative_sign='-',
                     zero_fill=True):
        if number == '':
            number = 0.0
        number = float(number)
        if number >= 0:
            sign = positive_sign or ''
        else:
            sign = negative_sign or ''
        number = abs(number)
        int_part = int(number)
        ascii_string = ''
        if include_sign:
            ascii_string += sign
            int_length -= len(sign)
        if dec_length > 0:
            if zero_fill:
                ascii_string += '%0*.*f' % (int_length + dec_length + 1, dec_length, number)
            else:
                ascii_string += '%*.*f' % (int_length + dec_length + 1, dec_length, number)
            ascii_string = ascii_string.replace('.', dec_separator)
        elif int_length > 0:
            if zero_fill:
                ascii_string += '%.*d' % (int_length, int_part)
            else:
                ascii_string += '%*d' % (int_length, int_part)
        total_length = (include_sign and sign and len(sign) or 0) + \
                       int_length + dec_length + \
                       (dec_length and dec_separator and 1 or 0)
        assert len(ascii_string) == total_length, \
            _("The formated string must match the given length")
        return str(ascii_string)

    @api.multi
    def stock_picking_export(self):
        for wizard in self:
            text = ''
            if wizard.file_type == 'model_salica':
                text, err_log, pickings_exported = wizard.get_model_salica()
            if wizard.file_type == 'model_aspil':
                text, err_log, pickings_exported = wizard.get_model_aspil()
            if wizard.file_type == 'model_mars':
                text, err_log, pickings_exported = wizard.get_model_mars()
            if wizard.file_type == 'model_deleben':
                text, err_log, pickings_exported = wizard.get_model_deleben()
            # -------------------------------------------------------------------------------------------------------------------------------
            # GENERAMOS FICHERO
            # -------------------------------------------------------------------------------------------------------------------------------
            if text:
                if wizard.file_type == 'model_aspil':
                    if err_log and not wizard.bypass_warnings:
                        err_log = _("Export completed with errors:") + '\n' + err_log
                        wizard.write({'state': 'choose', 'note_2': err_log})
                        self._context.get('active_ids', [])
                        return {
                            'name': _('Export File Result'),
                            'type': 'ir.actions.act_window',
                            'res_model': 'stock.picking.export',
                            'view_mode': 'form',
                            'view_type': 'form',
                            'res_id': wizard.id,
                            'views': [(False, 'form')],
                            'target': 'new',
                            'context': self._context,
                        }
                    else:
                        if self.sent_to_supplier:
                            self.set_pickings_sent_to_supplier(pickings_exported)
                        return {
                            'type': 'ir.actions.report.xml',
                            'report_name': 'stock_picking_export_aspil_xls',
                            'datas': {'lines': text}
                        }
                else:
                    data = base64.encodestring(text)
                    file_name = _("%s") % (wizard.file_name or 'albaran.txt')
                    if err_log:
                        err_log = _("Export completed with errors:") + '\n' + err_log
                    else:
                        err_log = _("Export completed without errors!")
                    if self.sent_to_supplier:
                        self.set_pickings_sent_to_supplier(pickings_exported)
                    wizard.write({'state': 'get', 'data': data, 'file_name': file_name, 'note_1': err_log})
                    return {
                        'name': _('Export File Result'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'stock.picking.export',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_id': wizard.id,
                        'views': [(False, 'form')],
                        'target': 'new',
                        'context': self._context,
                    }
            else:
                return {}

    @api.model
    def set_pickings_sent_to_supplier(self, pickings):
        picks = pickings.filtered(
            lambda r: not r.sent_to_supplier)
        picks.write({'sent_to_supplier': True})

    @api.model
    def get_picking_lines(self, pickings):
        lines = {}
        picks = pickings.filtered(
            lambda r: r.state == 'done')
        if picks:
            sql = """
                SELECT
                    spo.product_id    AS product_id,
                    spo.lot_id        AS lot_id,
                    smol.move_id      AS move_id,
                    SUM(smol.qty)     AS product_qty,
                    spo.picking_id    AS picking_id
                FROM stock_pack_operation spo
                JOIN stock_move_operation_link smol
                    ON spo.id = smol.operation_id
                WHERE spo.product_id IS NOT NULL
                    AND spo.picking_id in %s
                GROUP BY
                    smol.move_id,
                    spo.product_id,
                    spo.lot_id,
                    spo.picking_id
            """
            self._cr.execute(sql, [picks._ids])
            records = self._cr.fetchall()
            for record in records:
                product_id = self.env['product.product'].browse(record[0])
                lot_id = self.env['stock.production.lot'].browse(record[1])
                move_id = self.env['stock.move'].browse(record[2])
                product_qty = record[3] or 0.0
                picking_id = self.env['stock.picking'].browse(record[4])
                total = 0.0
                if move_id.procurement_id.sale_line_id:
                    total = move_id.order_price_unit * product_qty
                vals = {
                    'product_id': product_id,
                    'lot_id': lot_id,
                    'move_id': move_id,
                    'product_qty': product_qty,
                    'picking_id': picking_id,
                    'total': total,
                }
                if picking_id.id not in lines:
                    lines[picking_id.id] = []
                lines[picking_id.id].append(vals)
        # Ordenamos por código, ean13, nombre, movimmiento y lote
        for pick in pickings:
            if pick.id not in lines:
                lines[pick.id] = []
            else:
                lines[pick.id] = sorted(
                    lines[pick.id], key=lambda a: (
                        a['product_id'].default_code, a['product_id'].ean13, a['product_id'].name, a['move_id'], a['lot_id']
                    )
                )
        return lines

    @api.model
    def get_model_salica(self):
        err_log = ''
        text = ''
        separator = '|'
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        picking_lines = self.get_picking_lines(pickings)
        pickings_exported = self.env['stock.picking']
        for picking in pickings:
            line_pos = 0
            if picking.state != 'done':
                raise exceptions.Warning(_('Warning'), _("You can only export pickings in 'done' state!"))
            if not picking.supplier_id or picking.supplier_id.name.upper().find('SALICA') == -1:
                raise exceptions.Warning(_('Warning'), _("You can only export pickings from the supplier 'SALICA'!"))
            if picking.id not in picking_lines or not picking_lines[picking.id]: # Esto no debería pasar nunca
                err_msg = _("Error in picking '%s': not report lines!") % (picking.name)
                err_log += '\n' + err_msg
                continue
            commercial_partner_id = picking.partner_id.commercial_partner_id
            location_usage = picking.move_lines and picking.move_lines[0].location_id.usage
            location_dest_usage = picking.move_lines and picking.move_lines[0].location_dest_id.usage
            if not (location_usage == 'internal' and location_dest_usage == 'customer' or
                    location_usage == 'customer' and location_dest_usage == 'internal'):
                raise exceptions.Warning(_('Warning'), _("You can only export customer outgoing or incoming pickings! Picking: %s") % (picking.name))
            if location_dest_usage == 'customer' and not picking.sale_id:
                raise exceptions.Warning(_('Warning'), _("You can only export customer outgoing pickings with sales orders! Picking: %s") % (picking.name))
            # Signo para las cantidades (positivo = venta, negativo = abono)
            sign = -1 if location_dest_usage == 'internal' else 1
            # Obtenemos la tienda del pedido de venta si lo hay, y sino la averiguamos por el proveedor del albarán
            if picking.sale_id:
                shop_id = picking.sale_id.shop_id
            else:
                domain = [
                    ('supplier_id', '=', picking.supplier_id.id),
                    ('indirect_invoicing', '=', True)
                ]
                shop_id = self.env['sale.shop'].search(domain, limit=1)
            if not shop_id:
                raise exceptions.Warning(_('Warning'), _("No valid shop for picking %s!") % (picking.name))
            # Obtenemos el modo de pago del pedido si lo hay, y sino el que tenga por defecto el cliente.
            if picking.sale_id:
                payment_mode = picking.sale_id.payment_mode_id and picking.sale_id.payment_mode_id.name.upper() or ''
            else:
                domain = [
                    ('partner_id', '=', commercial_partner_id.id),
                    ('shop_id', '=', shop_id.id)
                ]
                partner_shop_ids = self.env['partner.shop.payment'].search(domain, limit=1)
                payment_mode = partner_shop_ids.customer_payment_mode or \
                    commercial_partner_id.customer_payment_mode
                payment_mode = payment_mode and payment_mode.name.upper() or ''
            if payment_mode.find('GIRO') != -1:
                payment_mode = 'G'
            elif payment_mode.find('TRANSFERENCIA') != -1:
                payment_mode = 'N'
            elif payment_mode.find('PAGARE') != -1:
                payment_mode = 'P'
            elif payment_mode.find('CONTADO') != -1 or payment_mode.find('MANO') != -1:
                payment_mode = 'T'
            else:
                raise exceptions.Warning(_('Warning'), _('Picking %s without know payment mode') % (picking.name))
            # Obtenemos el código de cliente
            domain = [
                ('partner_id', '=', picking.partner_id.id),
                ('shop_id', '=', shop_id.id)
            ]
            partner_shop_ids = self.env['partner.shop.ref'].search(domain, limit=1)
            partner_code = partner_shop_ids.ref or picking.partner_id.ref or ''
            if len(partner_code) > 0 and partner_code[:2] not in ['36', '15', '27', '32']:
                err_msg = _("Error in picking '%s': Partner %s with bad reference!") % (picking.name, picking.partner_id.name)
                err_log += '\n' + err_msg
            if not partner_code:
                raise exceptions.Warning(_('Warning'), _('Partner %s without reference (%s)') % (picking.partner_id.name, picking.name))
            # Recorremos las lineas del albarán
            lines = picking_lines[picking.id]
            for line in lines:
                product_id = line['product_id']
                lot_id = line['lot_id']
                move_id = line['move_id']
                if move_id.state != 'done': # Esto no debería pasar nunca
                    err_msg = _("Error in picking '%s': move not done!") % (picking.name)
                    err_log += '\n' + err_msg
                    continue
                l_text = ''
                # Tipo de registro: siempre un 1 (significa venta)
                l_text += '1'
                l_text += separator
                # N. albarán (9 cifras en total). Tiene que empezar por 36. Pot tanto adaptamos nuestro número
                numalb = re.findall('\d+', picking.name[-7:])[0]
                l_text += '36' + self.parse_number(numalb, 7, dec_length=0)
                l_text += separator
                # N. pallet (8 ceros)
                l_text += self.parse_string('00000000', 8)
                l_text += separator
                # Código artículo (14 caracteres) = Código artículo sálica (9 cifras) + 5 espacios en blanco
                supplier_product_code = product_id.seller_ids and product_id.seller_ids[0].product_code or False
                if not supplier_product_code:
                    raise exceptions.Warning(_('Warning'), _('Product %s without supplier code') % (product_id.display_name))
                supplier_product_code = self.parse_string(supplier_product_code, 9)
                l_text += self.parse_string(supplier_product_code, 14)
                l_text += separator
                # Código Lote (12 caracteres). Rellenear con espacios en blanco
                l_text += self.parse_string(lot_id.name, 12)
                l_text += separator
                # Fecha caducidad en formato aammdd
                lot_date = lot_id.use_date and lot_id.use_date[:10] or ''
                l_text += self.parse_short_date(lot_date, '%y%m%d')
                l_text += separator
                # Agencia de transporte (6 caracteres). Valquin = 360001
                l_text += '360001'
                l_text += separator
                # Cantidad unidades de venta en unidades (8 posiciones sin comas, y signo para los abonos) ej, para 23 ó -23 : |00000023| ó |-0000023|
                product_uom_qty = line['product_qty'] * sign
                if self.subtract_returns and move_id.returned_move_ids:
                    for smol in move_id.returned_move_ids.linked_move_operation_ids:
                        if lot_id == smol.operation_id.lot_id:
                            product_uom_qty -= smol.qty * sign
                if product_uom_qty == 0: # No grabamos la linea
                    l_text = ''
                    continue
                if (product_uom_qty * sign) < 0:
                    raise exceptions.Warning(_('Warning'), _('Picking %s with negative quantities') % (picking.name))
                extra_move = move_id.picking_id.sale_id and not move_id.procurement_id.sale_line_id
                if extra_move:
                    err_msg = _("Error in picking '%s': extra move detected!") % (move_id.picking_id.name)
                    err_log += '\n' + err_msg
                l_text += self.parse_number(round(product_uom_qty, 0), 8, dec_length=0, include_sign=True, positive_sign='0', negative_sign='-')
                l_text += separator
                # Modo de pago (1 caracter) -> Giro: G, Transferencia: T, Pagaré: P, Contado: T
                l_text += payment_mode
                l_text += separator
                # Posición de albarán (3 digitos): 001, 002, etc
                line_pos += 1
                l_text += self.parse_number(line_pos, 3, dec_length=0)
                l_text += separator
                # Referencia cliente (número de pedido) 12 espacios alfanuméricos
                l_text += self.parse_string(picking.sale_id.client_order_ref, 12)
                l_text += separator
                # Ubicación destino (12 espacios en blanco)
                l_text += ' ' * 12
                l_text += separator
                # Código cliente Sálica (6 cifras)
                l_text += self.parse_string(partner_code, 6)
                l_text += separator
                # Precio artículo/unidad (4 enteros, una coma y 4 decimales) Formato=eeee,dddd
                price = move_id.procurement_id.sale_line_id.price_unit or 0.0
                l_text += self.parse_number(price, 4, dec_length=4, dec_separator=',')
                l_text += separator
                # Descuento uno (2 enteros, una coma y 2 decimales) Formato=ee,dd
                discount = move_id.procurement_id.sale_line_id.discount or 0
                l_text += self.parse_number(discount, 2, dec_length=2, dec_separator=',')
                l_text += separator
                # Descuento dos (2 enteros, una coma y 2 decimales) Formato=ee,dd
                discount = 0.0
                l_text += self.parse_number(discount, 2, dec_length=2, dec_separator=',')
                l_text += separator
                # Descripción del artículo utilizada por Distribuidor (30 espacios alfanuméricos)
                l_text += self.parse_string(product_id.name, 30)
                l_text += separator
                text += ('\r\n' + l_text) if text else l_text
            if line_pos > 0: # Significa que se ha generado al menos un registro por albarán
                pickings_exported |= picking
        return (text, err_log, pickings_exported)

    @api.model
    def get_model_aspil(self):
        err_log = ''
        text = []
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        picking_lines = self.get_picking_lines(pickings)
        pickings_exported = self.env['stock.picking']
        picking_pos = 0
        for picking in pickings:
            line_pos = 0
            if picking.state != 'done':
                raise exceptions.Warning(_('Warning'), _("You can only export pickings in 'done' state!"))
            if not picking.supplier_id or picking.supplier_id.name.upper().find('EXTRUSIONADOS') == -1:
                raise exceptions.Warning(_('Warning'), _("You can only export pickings from the supplier 'ASPIL'!"))
            if picking.id not in picking_lines or not picking_lines[picking.id]: # Esto no debería pasar nunca
                err_msg = _("Error in picking '%s': not report lines!") % (picking.name)
                err_log += '\n' + err_msg
                continue
            location_usage = picking.move_lines and picking.move_lines[0].location_id.usage
            location_dest_usage = picking.move_lines and picking.move_lines[0].location_dest_id.usage
            if not (location_usage == 'internal' and location_dest_usage == 'customer' or
                    location_usage == 'customer' and location_dest_usage == 'internal'):
                raise exceptions.Warning(_('Warning'), _("You can only export customer outgoing or incoming pickings! Picking: %s") % (picking.name))
            if location_dest_usage == 'customer' and not picking.sale_id:
                raise exceptions.Warning(_('Warning'), _("You can only export customer outgoing pickings with sales orders! Picking: %s") % (picking.name))
            # Signo para las cantidades (positivo = venta, negativo = abono)
            sign = -1 if location_dest_usage == 'internal' else 1
            # Obtenemos la tienda del pedido de venta si lo hay, y sino la averiguamos por el proveedor del albarán
            if picking.sale_id:
                shop_id = picking.sale_id.shop_id
            else:
                domain = [
                    ('supplier_id', '=', picking.supplier_id.id),
                    ('indirect_invoicing', '=', True)
                ]
                shop_id = self.env['sale.shop'].search(domain, limit=1)
            if not shop_id:
                raise exceptions.Warning(_('Warning'), _("No valid shop for picking %s!") % (picking.name))
            # Obtenemos el código de cliente
            domain = [
                ('partner_id', '=', picking.partner_id.id),
                ('shop_id', '=', shop_id.id)
            ]
            partner_shop_ids = self.env['partner.shop.ref'].search(domain, limit=1)
            partner_code = partner_shop_ids.ref or picking.partner_id.ref or ''
            if not partner_code:
                raise exceptions.Warning(_('Warning'), _('Partner %s without reference (%s)') % (picking.partner_id.name, picking.name))
            # Recorremos las lineas del albarán
            lines = picking_lines[picking.id]
            picking_pos += 1
            for line in lines:
                product_id = line['product_id']
                lot_id = line['lot_id']
                move_id = line['move_id']
                if move_id.state != 'done': # Esto no debería pasar nunca
                    err_msg = _("Error in picking '%s': move not done!") % (picking.name)
                    err_log += '\n' + err_msg
                    continue
                l_text = {}
                # Número de albarán o contador de cabecera
                #picking_number = int(re.findall('\d+', picking.name[-7:])[0])
                picking_number = picking_pos
                # Código de cliente APEX (partner_code)
                # Número de pedido cliente
                client_order_ref = picking.sale_id.client_order_ref
                # Número de albarán
                picking_name = picking.name
                # Fecha albarán
                date_done = picking.date_done and picking.date_done[:10] or ''
                picking_date = self.parse_short_date(date_done, '%d/%m/%Y')
                # Código de artículo APEX
                supplier_product_code = product_id.seller_ids and product_id.seller_ids[0].product_code or False
                if not supplier_product_code:
                    raise exceptions.Warning(_('Warning'), _('Product %s without supplier code') % (product_id.display_name))
                # Código almacén asignado al distribuidor
                warehouse_code = 'D42'
                # Cantidad (en cajas). Para especificar cantidades en bolsas hay que calcular la parte proporcional de caja que supone.
                product_uom_qty = line['product_qty'] * sign
                if self.subtract_returns and move_id.returned_move_ids:
                    for smol in move_id.returned_move_ids.linked_move_operation_ids:
                        if lot_id == smol.operation_id.lot_id:
                            product_uom_qty -= smol.qty * sign
                if product_uom_qty == 0: # No grabamos la linea
                    l_text = ''
                    continue
                extra_move = move_id.picking_id.sale_id and not move_id.procurement_id.sale_line_id
                if extra_move:
                    err_msg = _("Error in picking '%s': extra move detected!") % (move_id.picking_id.name)
                    err_log += '\n' + err_msg
                if (product_uom_qty * sign) < 0:
                    raise exceptions.Warning(_('Warning'), _('Picking %s with negative quantities') % (picking.name))
                t_uom = self.env['product.uom']
                uom_id = product_id.uom_id.id
                uos_id = move_id.product_uos.id or product_id.uos_id.id
                product_uos_qty = t_uom._compute_qty(uom_id, product_uom_qty, uos_id)
                # Lote
                lot_name = lot_id.name
                # Precio (0 para regalos. '' para cálculo automático)
                price = ''
                #if extra_move:
                #    price = ''
                #else:
                #    price = move_id.procurement_id.sale_line_id.price_unit or 0.0
                #    price = round(price * product_uom_qty / product_uos_qty, 3)
                #    price = 0.0 if price == 0.0 else ''
                # Número línea
                line_pos += 1

                l_text = {
                    'picking_number': picking_number, # Número de albarán o contador de cabecera
                    'partner_code': partner_code, # Código de cliente APEX (partner_code)
                    'client_order_ref': client_order_ref, # Número de pedido cliente
                    'picking_name': picking_name, # Número de albarán
                    'picking_date': picking_date, # Fecha albarán
                    'line_pos': line_pos, # Número línea
                    'supplier_product_code': supplier_product_code, # Código de artículo APEX
                    'warehouse_code': warehouse_code, # Código almacén asignado al distribuidor
                    'product_uos_qty': product_uos_qty, # Cantidad (en cajas)
                    'lot_name': lot_name, # Lote
                    'price': price, # Precio (0 para regalos. '' para cálculo automático)
                }
                text.append(l_text)
            if line_pos > 0: # Significa que se ha generado al menos un registro por albarán
                pickings_exported |= picking
        return (text, err_log, pickings_exported)

    @api.model
    def get_model_mars(self):
        err_log = ''
        text = ''
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        picking_lines = self.get_picking_lines(pickings)
        pickings_exported = self.env['stock.picking']
        for picking in pickings:
            line_pos = 0
            if picking.state != 'done':
                raise exceptions.Warning(_('Warning'), _("You can only export pickings in 'done' state!"))
            if not picking.supplier_id or picking.supplier_id.name.upper().find('MARS') == -1:
                raise exceptions.Warning(_('Warning'), _("You can only export pickings from the supplier 'MARS'!"))
            if picking.id not in picking_lines or not picking_lines[picking.id]: # Esto no debería pasar nunca
                err_msg = _("Error in picking '%s': not report lines!") % (picking.name)
                err_log += '\n' + err_msg
                continue
            location_usage = picking.move_lines and picking.move_lines[0].location_id.usage
            location_dest_usage = picking.move_lines and picking.move_lines[0].location_dest_id.usage
            if not (location_usage == 'internal' and location_dest_usage == 'customer' or
                    location_usage == 'customer' and location_dest_usage == 'internal'):
                raise exceptions.Warning(_('Warning'), _("You can only export customer outgoing or incoming pickings! Picking: %s") % (picking.name))
            if location_dest_usage == 'customer' and not picking.sale_id:
                raise exceptions.Warning(_('Warning'), _("You can only export customer outgoing pickings with sales orders! Picking: %s") % (picking.name))
            # Signo para las cantidades (positivo = venta, negativo = abono)
            sign = -1 if location_dest_usage == 'internal' else 1
            # Obtenemos la tienda del pedido de venta si lo hay, y sino la averiguamos por el proveedor del albarán
            if picking.sale_id:
                shop_id = picking.sale_id.shop_id
            else:
                domain = [
                    ('supplier_id', '=', picking.supplier_id.id),
                    ('indirect_invoicing', '=', True)
                ]
                shop_id = self.env['sale.shop'].search(domain, limit=1)
            if not shop_id:
                raise exceptions.Warning(_('Warning'), _("No valid shop for picking %s!") % (picking.name))
            # Obtenemos el código de cliente
            domain = [
                ('partner_id', '=', picking.partner_id.id),
                ('shop_id', '=', shop_id.id)
            ]
            partner_shop_ids = self.env['partner.shop.ref'].search(domain, limit=1)
            partner_code = partner_shop_ids.ref or ''
            if not partner_code:
                raise exceptions.Warning(_('Warning'), _('Partner %s without reference (%s)') % (picking.partner_id.name, picking.name))
            sold_to_mayorista = '17610705' # VQ
            # Preparamos la cabecera
            l_text = '6CABPEDIDOMAYORISTA'
            text += ('\r\n' + l_text) if text else l_text
            # 1. Tipo de pedido (2)
            l_text = '3A'
            # 2. Sold to del mayorista (8)
            l_text += sold_to_mayorista
            # 3. Número de pedido del cliente (9)
            numped = picking.sale_id.client_order_ref or ''
            numped = re.findall('\d+', numped[-9:]) or ['0']
            numped = self.parse_number(numped[-1], 9)
            l_text += numped
            # 4. Ship to del cliente (8)
            ship_to_cliente = self.parse_string(partner_code, 8, fill='0', fill_mode='left')
            l_text += ship_to_cliente
            # 5. Fecha de pedido ddmmyy (6)
            sale_date = picking.sale_id.date_order and picking.sale_id.date_order[:10] or ''
            l_text += self.parse_short_date(sale_date, '%d%m%y')
            # 6. Número de albarán (15)
            numalb = self.parse_string(picking.name, 15)
            l_text += numalb
            # 7. Fecha de entrega ddmmyy (6)
            picking_date = picking.effective_date and picking.effective_date[:10] or '' # picking.date_done[:10]
            l_text += self.parse_short_date(picking_date, '%d%m%y')
            # 8. Indenticket (15)
            l_text += self.parse_string(' ', 15)
            text += '\r\n' + l_text
            # Recorremos las lineas del albarán
            l_text = '6LINPEDIDOMAYORISTA'
            text += '\r\n' + l_text
            lines = picking_lines[picking.id]
            for line in lines:
                product_id = line['product_id']
                lot_id = line['lot_id']
                move_id = line['move_id']
                if move_id.state != 'done': # Esto no debería pasar nunca
                    err_msg = _("Error in picking '%s': move not done!") % (picking.name)
                    err_log += '\n' + err_msg
                    continue
                l_text = ''
                # 1. Tipo de pedido (2)
                l_text = '3A'
                # 2. Sold to del mayorista (8)
                l_text += sold_to_mayorista
                # 3. Número de pedido del cliente (9)
                l_text += numped
                # 4. Ship to del cliente (8)
                l_text += ship_to_cliente
                # 5. Rep Item (6)
                supplier_product_code = product_id.seller_ids and product_id.seller_ids[0].product_code or False
                if not supplier_product_code:
                    raise exceptions.Warning(_('Warning'), _('Product %s without supplier code') % (product_id.display_name))
                l_text += self.parse_string(supplier_product_code, 6)
                # 6. Cantidad servida (4)
                product_uom_qty = line['product_qty'] * sign
                if self.subtract_returns and move_id.returned_move_ids:
                    for smol in move_id.returned_move_ids.linked_move_operation_ids:
                        if lot_id == smol.operation_id.lot_id:
                            product_uom_qty -= smol.qty * sign
                if product_uom_qty == 0: # No grabamos la linea
                    l_text = ''
                    continue
                if (product_uom_qty * sign) < 0:
                    raise exceptions.Warning(_('Warning'), _('Picking %s with negative quantities') % (picking.name))
                extra_move = move_id.picking_id.sale_id and not move_id.procurement_id.sale_line_id
                if extra_move:
                    err_msg = _("Error in picking '%s': extra move detected!") % (move_id.picking_id.name)
                    err_log += '\n' + err_msg
                t_uom = self.env['product.uom']
                uom_id = product_id.uom_id and product_id.uom_id.id
                uos_id = move_id.product_uos or product_id.uos_id
                if not uos_id:
                    raise exceptions.Warning(_('Warning'), _('Product %s without uos') % (product_id.display_name))
                product_uos_qty = t_uom._compute_qty(uom_id, product_uom_qty, uos_id.id)
                if round(abs(product_uos_qty - int(product_uos_qty)), 2) != 0:
                    err_msg = _("Error in picking '%s': quantities with decimals!") % (picking.name)
                    if err_log.find(err_msg) == -1:
                        err_log += '\n' + err_msg
                l_text += self.parse_number(round(product_uos_qty, 0), 4, dec_length=0, include_sign=True, positive_sign='', negative_sign='-')
                # 7. Unidad de medida (3)
                uos_name = uos_id.name
                if not uos_name:
                    err_msg = _("Error in picking '%s': not UoS in code %s!") % (move_id.picking_id.name, product_id.default_code)
                    err_log += '\n' + err_msg
                uos_code = ''
                if uos_name.upper().find('ESTUCHE') != -1:
                    uos_code = 'SB'
                if uos_name.upper().find('CAJA') != -1:
                    uos_code = 'CS'
                if uos_name.upper().find('BOLSA') != -1:
                    uos_code = 'PCE'
                if not uos_code:
                    err_msg = _("Error in picking '%s': invalid UoS in code %s!") % (move_id.picking_id.name, product_id.default_code)
                    err_log += '\n' + err_msg
                l_text += self.parse_string(uos_code, 3)
                # 8. Item category (2)
                l_text += '00'
                text += ('\r\n' + l_text) if text else l_text
                # Número línea
                line_pos += 1
            if line_pos > 0: # Significa que se ha generado al menos un registro por albarán
                pickings_exported |= picking
        return (text, err_log, pickings_exported)

    @api.model
    def get_model_deleben(self):
        err_log = ''
        text = ''
        separator = ' '
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        pickings_exported = self.env['stock.picking']
        for picking in pickings:
            if picking.state != 'done':
                raise exceptions.Warning(_('Warning'), _("You can only export pickings in 'done' state!"))
            if picking.picking_type_code != 'outgoing':
                raise exceptions.Warning(_('Warning'), _("You can only export outgoing pickings!"))
            if not picking.supplier_id or picking.supplier_id.name.upper().find('BAHLSEN') == -1:
                raise exceptions.Warning(_('Warning'), _("You can only export outgoing pickings from the supplier 'DELEBEN'!"))
            if not picking.sale_id:
                raise exceptions.Warning(_('Warning'), _("You can only export pickings from sales! (%s)") % (picking.name))
        for move in pickings.mapped('move_lines'):
            if not move.procurement_id.sale_line_id:
                err_msg = _("Error in picking '%s': extra move detected!") % (move.picking_id.name)
                err_log += '\n' + err_msg
        line_pos = 0
        for picking in pickings:
            lines = picking.pack_operation_ids.read_group(
                [('picking_id', 'in', picking.ids)],
                ['product_id', 'product_qty'],
                ['product_id']
            )
            returned_lines = picking.pack_operation_ids.read_group(
                [('picking_id', 'in', picking.mapped('move_lines.returned_move_ids.picking_id').ids)],
                ['product_id', 'product_qty'],
                ['product_id']
            )
            if returned_lines:
                lines_to_check = lines
                lines = []
                for line in lines_to_check:
                    for returned_line in returned_lines:
                        if line['product_id'][0] == returned_line['product_id'][0]:
                            line['product_qty'] -= returned_line['product_qty']
                            returned_lines.remove(returned_line)
                            break
                    if line['product_qty'] > 0:
                        lines.append(line)
                    if line['product_qty'] < 0:
                        raise exceptions.Warning(_('Warning'), _('Picking %s with negative quantities') % (picking.name))
            for line in lines:
                l_text = ''
                product_id = self.env['product.product'].browse(line['product_id'][0])
                # Tipo de registro: siempre un 1 (significa venta)
                l_text += '1'
                l_text += separator
                # Desconocido. 4 espacios
                l_text += ' ' * 4
                l_text += separator
                # Distribuidor. Valquin = 54.
                l_text += '54'
                l_text += separator
                # Código cliente Deleben (7 cifras)
                domain = [
                    ('partner_id', '=', picking.partner_id.id),
                    ('shop_id', '=', picking.sale_id.shop_id.id)
                ]
                partner_shop_ids = self.env['partner.shop.ref'].search(domain, limit=1)
                partner_code = partner_shop_ids.ref or picking.partner_id.ref or ''
                if not partner_code:
                    raise exceptions.Warning(_('Warning'), _('Partner %s without reference (%s)') % (picking.partner_id.name, picking.name))
                l_text += self.parse_string(partner_code, 7)
                l_text += separator
                # Desconocido. 3 espacios
                l_text += ' ' * 3
                l_text += separator
                # Desconocido. N.
                l_text += 'N'
                l_text += separator
                # Desconocido. 6 espacios
                l_text += ' ' * 6
                l_text += separator
                # N. albarán (9 cifras en total). Eliminamos '/'
                numalb = picking.name.replace('/','')
                numalb = numalb.replace('\\','')
                if len(numalb) > 9:
                    err_msg = _("Error in picking '%s': number '%s' exceed 9 characters!") % (picking.name, numalb)
                    err_log += '\n' + err_msg
                    numalb = numalb[-9:]
                l_text += self.parse_string(numalb, 9)
                l_text += separator
                # Fecha albarán en formato dd-mm-aaaa (10 posiciones)
                picking_date = picking.date_done[:10] # picking.effective_date[:10]
                l_text += self.parse_short_date(picking_date, '%d-%m-%Y')
                l_text += separator
                # Desconocido. 1 espacios
                l_text += ' ' * 1
                l_text += separator
                # Código artículo (4 caracteres)
                supplier_product_code = product_id.seller_ids[0].product_code
                if not supplier_product_code:
                    raise exceptions.Warning(_('Warning'), _('Product %s without supplier code') % (product_id.display_name))
                l_text += self.parse_string(supplier_product_code[:4], 4)
                l_text += separator
                # Cantidad unidades de venta en cajas (23 posiciones con comas y dos decimales) 20 enteros + coma + 2 decimales
                t_uom = self.env['product.uom']
                uom_id = product_id.uom_id and product_id.uom_id.id
                uos_id = product_id.uos_id and product_id.uos_id.id
                if not uos_id:
                    raise exceptions.Warning(_('Warning'), _('Product %s without uos') % (product_id.display_name))
                product_uom_qty = line['product_qty']
                product_uos_qty = t_uom._compute_qty(uom_id, product_uom_qty, uos_id)
                if round(abs(product_uos_qty - int(product_uos_qty)), 2) != 0:
                    err_msg = _("Error in picking '%s': quantities with decimals!") % (picking.name)
                    if err_log.find(err_msg) == -1:
                        err_log += '\n' + err_msg
                l_text += self.parse_number(product_uos_qty, 20, dec_length=2, dec_separator=',', zero_fill=False)
                l_text += separator
                # Desconocido. 34 espacios
                l_text += ' ' * 34
                l_text += separator
                # Referencia cliente (número de pedido) 15 espacios alfanuméricos
                l_text += self.parse_string(picking.sale_id.client_order_ref, 15)
                # Número línea
                line_pos += 1
                text += ('\r\n' + l_text) if text else l_text
            if line_pos > 0: # Significa que se ha generado al menos un registro por albarán
                pickings_exported |= picking
        return (text, err_log, pickings_exported)

