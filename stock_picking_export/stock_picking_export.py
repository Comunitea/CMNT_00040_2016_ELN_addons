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
    _description = 'Export stock picking to file'

    file_name = fields.Char(string='Filename', size=128, required=True, default='')
    file_type = fields.Selection([
        ('model_salica', 'SALICA'),
        ('model_deleben', 'DELEBEN'),
        ], string='File type', required=True)
    note = fields.Text(string='Log')
    data = fields.Binary('File', readonly=True)
    sent_to_supplier = fields.Boolean(
        string='Set picking as sent to supplier',
        default=False,
        help="Check this box if the physical delivery note has been sent to the supplier")
    state = fields.Selection([
        ('choose', 'choose'),
        ('get', 'get'),
        ], string='File type', required=True, default='choose')

    @api.onchange('file_type')
    def onchange_file_type(self):
        if self.file_type == 'model_salica':
            self.file_name = 'albacli.txt'
        elif self.file_type == 'model_deleben':
            self.file_name = 'LIALBA.txt'
        else:
            self.file_name = 'albaran.txt'

    @staticmethod
    def parse_string(string, length, fill=' '):
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
            sign = positive_sign
        else:
            sign = negative_sign
        number = abs(number)
        int_part = int(number)
        ascii_string = ''
        if include_sign:
            ascii_string += sign
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
        total_length = (include_sign and sign and 1 or 0) + \
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
                text, err_log = wizard.get_model_salica()
            if wizard.file_type == 'model_deleben':
                text, err_log = wizard.get_model_deleben()
            # -------------------------------------------------------------------------------------------------------------------------------
            # GENERAMOS FICHERO
            # -------------------------------------------------------------------------------------------------------------------------------
            if text:
                data = base64.encodestring(text)
                file_name = _("%s") % (wizard.file_name or 'albaran.txt')
                if err_log:
                    err_log = _("Export completed with errors:") + '\n' + err_log
                else:
                    err_log = _("Export completed without errors!")
                wizard.write({'state': 'get', 'data': data, 'file_name': file_name, 'note': err_log})
                return {
                    'name': _('Export File Result'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.picking.export',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': wizard.id,
                    'views': [(False, 'form')],
                    'target': 'new',
                }
            else:
                return {}

    @api.model
    def get_model_salica(self):
        err_log = ''
        text = ''
        separator = '|'
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
        for picking in pickings:
            if picking.state != 'done':
                raise exceptions.Warning(_('Warning'), _("You can only export pickings in 'done' state!"))
            if picking.picking_type_code != 'outgoing':
                raise exceptions.Warning(_('Warning'), _("You can only export outgoing pickings!"))
            if not picking.supplier_id or picking.supplier_id.name.upper().find('SALICA') == -1:
                raise exceptions.Warning(_('Warning'), _("You can only export outgoing pickings from the supplier 'SALICA'!"))
            if not picking.sale_id:
                raise exceptions.Warning(_('Warning'), _("You can only export pickings from sales! (%s)") % (picking.name))
        for move in pickings.mapped('move_lines'):
            if not move.procurement_id.sale_line_id:
                err_msg = _("Error in picking '%s': extra move detected!") % (move.picking_id.name)
                err_log += '\n' + err_msg
        out_report_lines = pickings.compute_out_report_lines()
        for picking in pickings:
            if picking.id not in out_report_lines or not out_report_lines[picking.id]: # Esto no debería pasar nunca
                err_msg = _("Error in picking '%s': not report lines!") % (picking.name)
                err_log += '\n' + err_msg
                continue
            lines = out_report_lines[picking.id]
            line_pos = 0
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
                # N. albaran (9 cifras en total). Tiene que empezar por 36. Pot tanto adaptamos nuestro número
                numalb = re.findall('\d+', picking.name[-7:])[0]
                l_text += '36' + self.parse_number(numalb, 7, dec_length=0)
                l_text += separator
                # N. pallet (8 ceros)
                l_text += self.parse_string('00000000', 8)
                l_text += separator
                # Código artículo (14 caracteres) = Código artículo sálica (9 cifras) + 5 espacios en blanco
                supplier_product_code = product_id.seller_ids[0].product_code
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
                product_uom_qty = line['product_qty']
                if move_id.returned_move_ids:
                    for smol in move_id.returned_move_ids.linked_move_operation_ids:
                        if lot_id == smol.operation_id.lot_id:
                            product_uom_qty -= smol.qty
                if product_uom_qty == 0: # No grabamos la linea
                    l_text = ''
                    continue
                if product_uom_qty < 0:
                    raise exceptions.Warning(_('Warning'), _('Picking %s with negative quantities') % (picking.name))
                l_text += self.parse_number(round(product_uom_qty, 0), 7, dec_length=0, include_sign=True, positive_sign='0', negative_sign='-')
                l_text += separator
                # Modo de pago (1 caracter) -> Giro: G, Transferencia: T, Pagaré: P, Contado: T
                payment_mode = picking.sale_id.payment_mode_id and picking.sale_id.payment_mode_id.name.upper() or ''
                if payment_mode.find('GIRO') != -1:
                    payment_mode = 'G'
                elif payment_mode.find('TRANSFERENCIA') != -1:
                    payment_mode = 'N'
                elif payment_mode.find('PAGARE') != -1:
                    payment_mode = 'P'
                elif payment_mode.find('CONTADO') != -1 or payment_mode.find('MANO') != -1:
                    payment_mode = 'T'
                else:
                    payment_mode = False
                if not payment_mode:
                    raise exceptions.Warning(_('Warning'), _('Picking %s (%s) without know payment mode') % (picking.name, picking.sale_id.name))
                l_text += payment_mode
                l_text += separator
                # Posición de albarán (3 digitos): 001, 002, etc
                line_pos += 1
                l_text += self.parse_number(line_pos, 3, dec_length=0)
                l_text += separator
                # Referencia cliente (numero de pedido) 12 espacios alfanuméricos
                l_text += self.parse_string(picking.sale_id.client_order_ref, 12)
                l_text += separator
                # Ubicación destino (12 espacios en blanco)
                l_text += ' ' * 12
                l_text += separator
                # Código cliente Sálica (6 cifras)
                domain = [
                    ('partner_id', '=', picking.partner_id.id),
                    ('shop_id', '=', picking.sale_id.shop_id.id)
                ]
                partner_shop_ids = self.env['partner.shop.ref'].search(domain, limit=1)
                partner_code = partner_shop_ids.ref or picking.partner_id.ref or ''
                if len(partner_code) > 0 and partner_code[:2] not in ['36', '15', '27', '32']:
                    err_msg = _("Error in picking '%s': Partner %s with bad reference!") % (picking.name, picking.partner_id.name)
                    err_log += '\n' + err_msg
                if not partner_code:
                    raise exceptions.Warning(_('Warning'), _('Partner %s without reference (%s)') % (picking.partner_id.name, picking.name))
                l_text += self.parse_string(partner_code, 6)
                l_text += separator
                # Precio artículo/unidad (4 enteros, una coma y 4 decimales) Formato=eeee,dddd
                price = move_id.procurement_id.sale_line_id.price_unit
                l_text += self.parse_number(price, 4, dec_length=4, dec_separator=',')
                l_text += separator
                # Descuento uno (2 enteros, una coma y 2 decimales) Formato=ee,dd
                discount = move_id.procurement_id.sale_line_id.discount
                l_text += self.parse_number(discount, 2, dec_length=2, dec_separator=',')
                l_text += separator
                # Descuento dos (2 enteros, una coma y 2 decimales) Formato=ee,dd
                discount = 0.0
                l_text += self.parse_number(discount, 2, dec_length=2, dec_separator=',')
                l_text += separator
                # Descripción del artículo utilizada por Distribuidor (30 espacios alfanuméricos)
                l_text += self.parse_string(product_id.name, 30)
                l_text += separator
                if l_text:
                    if text:
                        text += '\r\n'
                    text += l_text
                    if self.sent_to_supplier and not picking.sent_to_supplier:
                        picking.write({'sent_to_supplier': True})
        return (text, err_log)

    @api.model
    def get_model_deleben(self):
        err_log = ''
        text = ''
        separator = ' '
        active_ids = self._context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(active_ids)
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
                    #print 'line', line['product_id'][0]
                    for returned_line in returned_lines:
                        print 'returned_line', returned_line['product_id'][0]
                        if line['product_id'][0] == returned_line['product_id'][0]:
                            print 'encuentro coincidencia'
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
                # N. albaran (9 cifras en total). Eliminamos '/'
                numalb = picking.name.replace('/','')
                numalb = numalb.replace('\\','')
                if len(numalb) > 9:
                    err_msg = _("Error in picking '%s': number '%s' exceed 9 characters!") % (picking.name, numalb)
                    err_log += '\n' + err_msg
                    numalb = numalb[-9:]
                l_text += self.parse_string(numalb, 9)
                l_text += separator
                # Fecha albaran en formato dd-mm-aaaa (10 posiciones)
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
                # Referencia cliente (numero de pedido) 15 espacios alfanuméricos
                l_text += self.parse_string(picking.sale_id.client_order_ref, 15)
                if l_text:
                    if text:
                        text += '\r\n'
                    text += l_text
                    if self.sent_to_supplier and not picking.sent_to_supplier:
                        picking.write({'sent_to_supplier': True})
        return (text, err_log)

