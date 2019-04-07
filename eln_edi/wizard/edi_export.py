# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-TODAY
#       Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#        $Javier Colmenero Fernández$
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

from openerp.tools.translate import _
from openerp.osv import fields, orm
from edi_logging import logger
import os
from datetime import datetime
import time
from openerp import tools
import codecs
from unidecode import unidecode
from dateutil import tz
from base64 import b64encode
from reportlab.lib import units
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
import operator
log = logger("export_edi")


class edi_export (orm.TransientModel):
    _name = "edi.export"
    _columns = {
        'configuration': fields.many2one('edi.configuration', 'Configuration', required=True),
        'date_due': fields.date('Date Due', required=True),
    }
    _defaults = {
        'date_due': fields.date.context_today,
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(edi_export, self).default_get(cr, uid, fields, context=context)
        date_due = time.strftime('%Y-%m-%d')
        conf_ids = self.pool.get('edi.configuration').get_configuration(cr, uid, [])
        if context['active_model'] == u'account.invoice' :
            invoice_ids = self.pool.get(context['active_model']).browse(cr, uid, context['active_ids'])
            date_due = max([x.date_due for x in invoice_ids if x.date_due])
        res.update({
            'configuration': conf_ids[0].id,
            'date_due': date_due
        })
        return res

    def create_doc(self, cr, uid, ids, obj, file_name, context):
        doc_obj = self.pool.get('edi.doc')
        if obj:
            name = gln_ef = gln_ve = gln_co = gln_rf = gln_rm = gln_de = \
                doc_type = sale_order_id = picking_id = invoice_id = \
                coacsu_invoice_ids = False
            if context['active_model'] == u'sale.order':
                name = str(obj.id) + ' - ' + obj.number
                gln_ef = obj.partner_id.gln_ef
                gln_ve = obj.company_id.partner_id.gln_ve
                gln_co = obj.partner_invoice_id.gln_co
                gln_rm = obj.partner_shipping_id.gln_rm
                doc_type = 'ordrsp'
                sale_order_id = obj.id
            elif context['active_model'] == u'stock.picking':
                name = str(obj.id) + ' - ' + obj.name
                gln_ef = obj.company_id.gln_ef
                gln_ve = obj.partner_id.commercial_partner_id.gln_ve or obj.company_id.gln_ve
                gln_de = obj.partner_id.gln_de
                gln_rf = obj.partner_id.gln_rf
                gln_co = obj.partner_id.gln_co
                gln_rm = obj.partner_id.gln_rm
                gln_proveedor = obj.supplier_id and \
                    (obj.supplier_id.commercial_partner_id.gln_desadv or 
                     obj.supplier_id.commercial_partner_id.gln_de)
                gln_desadv = obj.partner_id.commercial_partner_id.gln_desadv or obj.partner_id.gln_de
                doc_type = 'desadv'
                picking_id = obj.id
            elif context['active_model'] == u'account.invoice':
                if not context.get('coacsu', False): 
                    name = str(obj.id) + ' - ' + obj.number
                    invoice_part = obj.partner_id
                    picking_part = obj.picking_ids and obj.picking_ids[0].partner_id or False
                    gln_ef = obj.company_id.gln_ef
                    gln_ve = picking_part and picking_part.commercial_partner_id.gln_ve or \
                             invoice_part.commercial_partner_id.gln_ve or obj.company_id.gln_ve
                    gln_de = picking_part and picking_part.gln_de or invoice_part.gln_de
                    gln_rf = picking_part and picking_part.gln_rf or invoice_part.gln_rf
                    gln_co = picking_part and picking_part.gln_co or invoice_part.gln_co
                    gln_rm = picking_part and picking_part.gln_rm or invoice_part.gln_rm
                    doc_type = 'invoic'
                    invoice_id = obj.id
                else:
                    name = file_name.replace('.ASC','').split('/')[-1]
                    invoice_part = obj[0].partner_id
                    picking_part = obj[0].picking_ids and obj[0].picking_ids[0].partner_id or False
                    gln_ef = obj[0].company_id.gln_ef
                    gln_ve = picking_part and picking_part.commercial_partner_id.gln_ve or \
                             invoice_part.commercial_partner_id.gln_ve or obj[0].company_id.gln_ve
                    gln_de = picking_part and picking_part.gln_de or invoice_part.gln_de
                    gln_rf = picking_part and picking_part.gln_rf or invoice_part.gln_rf
                    gln_co = picking_part and picking_part.gln_co or invoice_part.gln_co
                    gln_rm = picking_part and picking_part.gln_rm or invoice_part.gln_rm
                    doc_type = 'coacsu'
                    invoice_ids = [x.id for x in obj]
                    coacsu_invoice_ids = [(6, 0, invoice_ids)]
            else:
                raise orm.except_orm(_('Error'), _('El modelo no es ni un pedido ni un albarán ni una factura.'))
            f = open(file_name)
            values = {
                'name': name,
                'file_name': file_name.split('/')[-1],
                'status': 'export',
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'date_process': time.strftime('%Y-%m-%d %H:%M:%S'),
                'type': doc_type,
                'sale_order_id': sale_order_id,
                'picking_id': picking_id,
                'invoice_id': invoice_id,
                'coacsu_invoice_ids': coacsu_invoice_ids,
                'gln_ef': gln_ef,
                'gln_ve': gln_ve,
                'gln_de': gln_de,
                'gln_rf': gln_rf,
                'gln_co': gln_co,
                'gln_rm': gln_rm,
                'message': f.read(),
            }
            f.close()
            file_id = doc_obj.create(cr, uid, values, context) # Creamos siempre un nuevo registro, no actualizamos el existente. Si queremos actualizar, borramos esta linea y usamos el if de abajo.
            #if not doc_obj.search(cr, uid, [('name', '=', name)], context=context):
            #    file_id = doc_obj.create(cr, uid, values, context)
            #    log.info(u"Exportado %s " % file_name)
            #else:
            #    file_id = doc_obj.search(cr, uid, [('name', '=', name)], context=context)
            #    doc_obj.write(cr, uid, file_id, values, context)

        return file_id

    def addons_path(self, cr, uid, ids, path=False):
        if path:
            report_module = path.split(os.path.sep)[0]
            for addons_path in tools.config['addons_path'].split(','):
                if os.path.lexists(addons_path+os.path.sep+report_module):
                    return os.path.normpath(addons_path+os.path.sep+path)

        return os.path.dirname(self.path())

    def check_invoice_data(self, invoice):
        errors = ''
        invoice_part = invoice.partner_id
        picking_part = invoice.picking_ids and invoice.picking_ids[0].partner_id or False
        gln_ef = invoice.company_id.gln_ef
        gln_ve1 = invoice.company_id.gln_ve
        gln_ve2 = picking_part and picking_part.commercial_partner_id.gln_ve or invoice_part.commercial_partner_id.gln_ve
        gln_de = picking_part and picking_part.gln_de or invoice_part.gln_de
        gln_rf = picking_part and picking_part.gln_rf or invoice_part.gln_rf
        gln_co = picking_part and picking_part.gln_co or invoice_part.gln_co
        gln_rm = picking_part and picking_part.gln_rm or invoice_part.gln_rm
        if not self.check_ean13(gln_ef) or not self.check_ean13(gln_ve1):
            errors += _('The company %s not have some GLN defined correctly.\n') % \
                invoice.company_id.name
        if not invoice.company_id.edi_rm:
            errors += _('The company %s not have trade register defined.\n') % \
                invoice.company_id.name
        if not invoice.partner_id.commercial_partner_id.vat:
            errors += _('The partner %s not have vat.\n') % \
                invoice.partner_id.commercial_partner_id.name
        if not invoice.company_id.partner_id.vat:
            errors += _('The partner %s not have vat.\n') % \
                invoice.company_id.partner_id.name
        if not self.check_ean13(gln_de) or not self.check_ean13(gln_rf) or \
           not self.check_ean13(gln_co) or not self.check_ean13(gln_rm) or \
           (gln_ve2 and not self.check_ean13(gln_ve2)):
            errors += _('The partner %s not have some GLN defined correctly.\n') % \
                invoice.partner_id.name
        if not invoice.date_invoice:
            errors += _('The invoice not have date.\n')
        if not invoice.payment_mode_id.edi_code:
            errors += _('The invoice payment type is not defined or not have a edi code asigned.\n')
        if not invoice.origin:
            errors += _('The invoice not have origin.\n')
        for line in invoice.invoice_line:
            if line.product_id.default_code == 'DPP':
                if not invoice.early_payment_discount:
                    errors += _('Found early payment discount lines, but there is not set any percentage on the invoice.\n')
                continue
            if not line.product_id.ean13:
                errors += _('The product %s not have EAN.\n') % \
                    line.product_id.name
        if errors:
            raise orm.except_orm(_('Data error'), errors)

    @staticmethod
    def parse_number(number, length, decimales):
        if not number:
            return ' ' * length
        isnegative = False
        if isinstance(number, float):
            if number < 0:
                isnegative = True
                number = abs(number)
            number = round(number, decimales)
            number = str(number)
            point_pos = number.index('.')
            if len(number[point_pos+1:]) < decimales:
                number += (decimales - len(number[point_pos+1:])) * '0'
            if decimales == 0:
                number = number.replace('.0', '')
            number = number.replace('.', '')
        else:
            number = str(number)
        if not isnegative:
            new_number = (length - len(number)) * '0' + number
        else:
            new_number = '-' + (length - len(number) - 1) * '0' + number
        if len(new_number) != length:
            raise orm.except_orm(_('Error parsing'), _('Error parsing number'))
        return new_number

    @staticmethod
    def parse_string(string, length):
        if not string:
            string = u' '
        if isinstance(string, float):
            string = str(string)
            point_pos = string.index('.')
            if len(string[point_pos+1:]) < 2:
                string += '0'
            string = string.replace('.', '')
        else:
            string = unidecode(unicode(string))

        string = string[0:length]
        new_string = string + u' ' * (length - len(string))

        if len(new_string) != length:
            raise orm.except_orm(_('Error parsing!'), _('The length of "%s" is greater of %s.') % (new_string, length))
        return new_string

    @staticmethod
    def parse_short_date(date_str):
        if len(date_str) != 10:
            raise orm.except_orm(_('Date error'),
                                 _('Error parsing short date'))
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y%m%d')

    @staticmethod
    def parse_long_date(date_str):
        if len(date_str) != 19:
            raise orm.except_orm(_('Date error'), _('Error parsing long date'))
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date.strftime('%Y%m%d%H%M')

    @staticmethod
    def check_ean13(eancode):
        if not eancode or not eancode.isdigit():
            return False
        if not len(eancode) == 13:
            return False
        sum_digits = 0
        ean_len = int(len(eancode))
        for i in range(ean_len - 1):
            pos = int(ean_len - 2 - i)
            if (not i % 2): # Es par
                sum_digits += 3 * int(eancode[pos])
            else: # Es impar
                sum_digits += int(eancode[pos])
        check = 10 - operator.mod(sum_digits, 10)
        if check == 10:
            check = 0
        return check == int(eancode[-1])

    def parse_invoice(self, cr, uid, invoice, file_name, context=None):

        def parse_address(address, gln_val):
            address_data = ''
            address_data += self.parse_number(gln_val, 13, 0)
            address_data += self.parse_string(address.name, 35)
            address_data += self.parse_string(False, 35) # Reg. Mercantil
            address_data += self.parse_string(address.street, 35)
            address_data += self.parse_string(address.city, 35)
            address_data += self.parse_string(address.zip, 9)
            address_data += self.parse_string(address.commercial_partner_id.vat, 17)
            return address_data

        invoice_data = 'CAB'
        self.check_invoice_data(invoice)
        f = codecs.open(file_name, 'w', 'utf-8')

        invoice_part = invoice.partner_id
        picking_part = invoice.picking_ids and invoice.picking_ids[0].partner_id or False
        gln_ef = invoice.company_id.gln_ef
        gln_ve = picking_part and picking_part.commercial_partner_id.gln_ve or \
                 invoice_part.commercial_partner_id.gln_ve or invoice.company_id.gln_ve
        gln_de = picking_part and picking_part.gln_de or invoice_part.gln_de
        gln_rf = picking_part and picking_part.gln_rf or invoice_part.gln_rf
        gln_co = picking_part and picking_part.gln_co or invoice_part.gln_co
        gln_rm = picking_part and picking_part.gln_rm or invoice_part.gln_rm

        invoice_data += self.parse_number(gln_de, 13, 0)
        # datos de cabecera

        # tipo de factura
        if invoice.type == 'out_invoice':
            invoice_data += u'380'
        else:
            invoice_data += u'381'
        invoice_data += self.parse_string(invoice.number, 17)

        # Fecha de factura.
        invoice_data += self.parse_short_date(invoice.date_invoice)

        # modo de pago
        invoice_data += self.parse_string(invoice.payment_mode_id.edi_code, 3)

        # cargo o abono (siempre en blanco 3 espacios)
        invoice_data += ' ' * 3

        # código de sección de proveedor.
        section_code = invoice.partner_id.commercial_partner_id.section_code
        if invoice.partner_id.commercial_partner_id.edi_filename == u'ECI':
            # Para El Corte Inglés enviamos el código departamento interno en lugar de la sección.
            # Aunque este código de departamento va en este caso repetido en el fichero en otra posición,
            # no es mapeado en la traducción de Generix
            section_code = invoice.partner_id.commercial_partner_id.department_code_edi
        elif (section_code == u'03072901'
              and gln_rf in (u'8424818010006', u'8424818290002') # FRZ ó VMR
              and gln_rm not in (u'8424818019016', u'8424818299012')): # No es una Plataforma
            # En VQ, para FRZ/VMR debemos indicar un código de proveedor para
            # Tiendas (03072900), otro para Plataforma (03072901) y otro para EMD (03072902).
            # VQ usa un mismo partner con sus direcciones (incluida plataforma) para Tiendas y Plataforma y otro para EMD.
            # Debemos sin embargo diferenciar las Tiendas de la Plataforma y lo haremos mediante código.
            # En el partner (matriz) establecemos el de Plataforma y el de EMD y en código aplicamos la excepción para tiendas,
            # para las cuales podemos enviar el código 03072900 u omitirlo. Es preferible omitirlo ya que
            # lo contrario podría generar rechazos para otros partners del mismo grupo en los cuales no se estaba enviando.
            section_code = False
        invoice_data += self.parse_string(section_code, 9)

        # texto libre
        invoice_data += self.parse_string(False, 131)

        origin = [] # Vamos a comprobar si es una factura resumen. En ese caso no pondremos en la cabecera el num alb y pedido

        for line in invoice.invoice_line:
            if line.origin:
                origin.append(line.origin)
            origin = list(set(origin))
            if len(origin) > 1:
                break
        
        if len(origin) > 1: # Factura resumen
            # numero de albaran
            invoice_data += self.parse_string(False, 17)
            # numero de pedido
            invoice_data += self.parse_string(False, 17)
        else:
            if invoice.type == 'out_refund':
                # numero de albaran
                # si en el pedido de venta el campo origin tiene algun valor lo interpretamos como el albarán 
                # de entrega real (por un tercero por ejemplo)
                # si va precedido de la palabra ALB.
                numalb = False
                if invoice.origin_invoices_ids and invoice.origin_invoices_ids[0].sale_order_ids:
                    numalb = invoice.origin_invoices_ids[0].sale_order_ids[0].origin
                    if numalb and len(numalb) > 4 and numalb[:4].upper() == 'ALB.':
                        numalb = numalb[4:]
                    else:
                        numalb = False
                if not numalb:
                    if invoice.origin_invoices_ids and invoice.origin_invoices_ids[0].picking_ids:
                        numalb = invoice.origin_invoices_ids[0].picking_ids[0].name
                    else:
                        numalb = invoice.origin
                invoice_data += self.parse_string(numalb, 17)
            else:
                # numero de albaran
                # si en el pedido de venta el campo origin tiene algun valor lo interpretamos como el albarán 
                # de entrega real (por un tercero por ejemplo)
                # si va precedido de la palabra ALB.
                numalb = False
                if invoice.sale_order_ids:
                    numalb = invoice.sale_order_ids[0].origin
                    if numalb and len(numalb) > 4 and numalb[:4].upper() == 'ALB.':
                        numalb = numalb[4:]
                    else:
                        numalb = False
                if not numalb:
                    if invoice.picking_ids:
                        numalb = invoice.picking_ids[0].name
                    else:
                        numalb = invoice.origin
                invoice_data += self.parse_string(numalb, 17)
            if invoice.type == 'out_refund':
                # numero de pedido
                numped = invoice.origin_invoices_ids and invoice.origin_invoices_ids[0].sale_order_ids and invoice.origin_invoices_ids[0].sale_order_ids[0].client_order_ref
                numped = numped or invoice.name
                invoice_data += self.parse_string(numped, 17)
            else:
                # numero de pedido
                numped = invoice.sale_order_ids and invoice.sale_order_ids[0].client_order_ref
                numped = numped or invoice.name
                invoice_data += self.parse_string(numped, 17)

        # si es rectificativa se añade el numero de factura original.
        if invoice.type == 'out_refund':
            invoice_data += self.parse_string(invoice.origin_invoices_ids and invoice.origin_invoices_ids[0].number, 17)
        else:
            invoice_data += u' ' * 17

        # receptor
        invoice_data += parse_address(invoice.partner_id, gln_rf)

        # emisor factura
        address_data = ''
        address_data += self.parse_number(gln_ef, 13, 0)
        address_data += self.parse_string(invoice.company_id.partner_id.name, 35)
        address_data += self.parse_string(invoice.company_id.edi_rm, 35)
        address_data += self.parse_string(invoice.company_id.street, 35)
        address_data += self.parse_string(invoice.company_id.city, 35)
        address_data += self.parse_string(invoice.company_id.zip, 9)
        address_data += self.parse_string(invoice.company_id.vat, 17)
        
        # vendedor
        address_data += self.parse_number(gln_ve, 13, 0)
        address_data += self.parse_string(invoice.company_id.partner_id.name, 35)
        address_data += self.parse_string(invoice.company_id.edi_rm, 35)
        address_data += self.parse_string(invoice.company_id.street, 35)
        address_data += self.parse_string(invoice.company_id.city, 35)
        address_data += self.parse_string(invoice.company_id.zip, 9)
        address_data += self.parse_string(invoice.company_id.vat, 17)
        invoice_data += address_data

        # comprador
        invoice_data += parse_address(invoice.partner_id.commercial_partner_id, gln_co)

        # código de departamento interno
        invoice_data += self.parse_string(invoice.partner_id.commercial_partner_id.department_code_edi, 3)

        # receptor de la mercancia
        invoice_data += parse_address(invoice.picking_ids and invoice.picking_ids[0].partner_id or invoice.partner_id, gln_rm)

        # divisa
        invoice_data += self.parse_string(invoice.currency_id.name or u'EUR', 3)

        # vencimientos
        payments = [x for x in invoice.move_id.line_id if x.date_maturity]
        if len(payments) > 3:
            raise orm.except_orm(_('Payment error'), _('the invoice have %s payments, max 3 payments') % len(payments))
        if len(payments) > 1:
            invoice_data += '21 '
        else:
            invoice_data += '25 '
        for payment in payments:
            if invoice.type == 'out_refund':
                invoice_data += self.parse_short_date(payment.date_maturity) + self.parse_number(payment.credit, 18, 3)
            else:
                invoice_data += self.parse_short_date(payment.date_maturity) + self.parse_number(payment.debit, 18, 3)
        invoice_data += (' ' * 26) * (3 - len(payments))

        # Posiciones no usadas
        invoice_data += (' ' * 12)

        # Envío copia de factura. Ej. Grupo IFA debe recibir copia de la factura enviada a sus asociados para realizar el pago
        if invoice.partner_id.commercial_partner_id.edi_invoice_copy:
            invoice_data += '1'
        else:
            invoice_data += '0'

        f.write(invoice_data)

        # descuentos globales        
        early_discount_amount = 0
        if invoice.global_disc > 0: # descuento comercial
            discount_data = '\r\nDCO'
            discount_data += 'A  TD 1  ' + self.parse_number(invoice.global_disc, 8, 2)
            discount_data += self.parse_number(invoice.total_global_discounted, 18, 3)
            f.write(discount_data)
        if invoice.early_payment_discount: # descuento pronto pago
            for line in invoice.invoice_line:
                if line.product_id.default_code == 'DPP':
                    early_discount_amount += (-1) * line.price_subtotal
            if early_discount_amount:
                discount_data = '\r\nDCO'
                discount_data += 'A  EAB1  ' + self.parse_number(invoice.early_payment_discount, 8, 2)
                discount_data += self.parse_number(early_discount_amount, 18, 3)
                f.write(discount_data)
            
        invoice_number = 0
        total_bruto = 0

        # linea de factura
        for line in invoice.invoice_line:
            if line.product_id.default_code == 'DPP':
                continue
            total_bruto += line.price_unit * line.quantity
            invoice_number += 1
            line_data = '\r\nLIN' + self.parse_number(invoice_number, 4, 0)
            # referencias de producto
            line_data += self.parse_number(line.product_id.ean13, 13, 0)
            line_data += self.parse_string(line.product_id.partner_product_code, 35)
            line_data += self.parse_string(line.product_id.default_code, 35)
            line_data += self.parse_string(line.product_id.with_context(lang=invoice.partner_id.lang).name, 35)
            #line_data += self.parse_string(line.name, 35)

            # cantidades facturada enviada y sin cargo

            #line_qty = line.quantity / (line.product_id.uos_coeff or 1)
            t_uom = self.pool.get('product.uom')
            qty = line.quantity
            uos_id = line.uos_id.id
            uom_id = line.product_id.uom_id.id
            line_qty = t_uom._compute_qty(cr, uid, uos_id, qty, uom_id)
            if line.partner_id.commercial_partner_id.edi_uos_as_uom_on_kgm_required:
                kgm_uom = self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, 'product.product_uom_kgm')
                if uom_id == kgm_uom:
                    line_qty = t_uom._compute_qty(cr, uid, uos_id, qty, (line.product_id.uos_id and line.product_id.uos_id.id or uos_id))
            line_qty = round(line_qty, 0)
            if line.price_unit != 0:
                line_data += self.parse_number(line_qty, 15, 0)
                line_data += self.parse_number(line_qty, 15, 0)
                line_data += self.parse_number(0, 15, 0)
            else:
                line_data += self.parse_number(0, 15, 0)
                line_data += self.parse_number(line_qty, 15, 0)
                line_data += self.parse_number(line_qty, 15, 0)

            line_data += self.parse_string(line.product_id.uom_id.edi_code or u'PCE', 3)
            line_data += self.parse_string('', 70)

            # importe total neto
            line_data += self.parse_number(line.price_subtotal, 18, 3)

            # precios unitarios bruto y neto
            line_price_unit_gross = (line.quantity * line.price_unit) / line_qty
            line_price_unit_net = line.price_subtotal / line_qty
            line_data += self.parse_number(line_price_unit_gross, 18, 3)
            line_data += self.parse_number(line_price_unit_net, 18, 3)

            # numero de pedido
            numped = False
            if line.partner_id.commercial_partner_id.edi_order_ref_required:
                if line.stock_move_id.procurement_id.sale_line_id:
                    numped = line.stock_move_id.procurement_id.sale_line_id.order_id.client_order_ref
                else:
                    numped = invoice.name
            line_data += self.parse_string(numped, 17)

            # numero de albaran
            # si en el pedido de venta el campo origin tiene algun valor lo interpretamos como el albarán 
            # de entrega real (por un tercero por ejemplo)
            # si va precedido de la palabra ALB.
            numalb = False
            if line.stock_move_id.procurement_id.sale_line_id:
                numalb = line.stock_move_id.procurement_id.sale_line_id.order_id.origin
                if numalb and len(numalb) > 4 and numalb[:4].upper() == 'ALB.':
                    numalb = numalb[4:]
                else:
                    numalb = False
            if not numalb:
                if line.stock_move_id.picking_id:
                    numalb = line.stock_move_id.picking_id.name
                else:
                    numalb = line.origin or invoice.origin
            line_data += self.parse_string(numalb, 17)

            # datos de los impuestos, únicamente del primero
            if line.invoice_line_tax_id:
                imp = line.invoice_line_tax_id and int(line.invoice_line_tax_id[0].amount * 100) or int('0')
                imp = round(imp, 2)
                line_data += self.parse_string(line.invoice_line_tax_id[0].edi_code or u'VAT', 3)
                if line.invoice_line_tax_id[0].edi_code and line.invoice_line_tax_id[0].edi_code == 'EXT':
                    line_data += self.parse_number(False, 5, 2)
                    line_data += self.parse_number(False, 18, 3)
                else:
                    line_data += self.parse_number(imp, 5, 2)
                    line_data += self.parse_number((line.price_subtotal * (imp/100.0)), 18, 3)
            else:
            # revisar para coviran portugal, es posible que haya que poner ceros
                line_data += 'EXT' + ' ' * 23

            # fecha de entrega
            if line.partner_id.commercial_partner_id.edi_date_required:
                if line.stock_move_id and (line.stock_move_id.picking_id.effective_date or line.stock_move_id.picking_id.date_done):
                    date = line.stock_move_id.picking_id.effective_date or line.stock_move_id.picking_id.date_done
                else:
                    date = invoice.date_invoice
                line_data += self.parse_short_date(date[:10])
            else:
                line_data += self.parse_string(False, 8)

            # descuentos de linea
            if line.discount:
                line_data += '\r\nDLFA  TD ' + ' ' * 15 + '1  ' + \
                    self.parse_number(line.discount, 8, 2) + '204' + \
                    self.parse_number(((line.quantity * line.price_unit) - line.price_subtotal), 18, 3)
            f.write(line_data)

        # importes totales
        total_data = '\r\nTOT' + self.parse_number(total_bruto, 18, 3)
        total_data += self.parse_number(invoice.amount_untaxed + invoice.total_global_discounted + early_discount_amount, 18, 3)
        total_data += self.parse_number(invoice.amount_untaxed, 18, 3)

        total_data += self.parse_number(invoice.amount_tax or '0', 18, 3)
        total_data += self.parse_number(invoice.total_global_discounted + early_discount_amount, 18, 3)
        total_data += self.parse_number('0', 18, 3)
        total_data += self.parse_number(invoice.amount_total, 18, 3)

        f.write(total_data)

        # impuestos de la factura
        for tax in invoice.tax_line:
            tax_data = '\r\nTAX'
            tax_data += self.parse_string(tax.tax_id.edi_code or u'VAT', 3)
            if tax.tax_id.edi_code and tax.tax_id.edi_code == 'EXT':
                tax_data += self.parse_number(False, 5, 2)
                tax_data += self.parse_number(False, 18, 3)
                tax_data += self.parse_number(False, 18, 3)
            else:
                tax_data += self.parse_number(tax.tax_id.amount * 100, 5, 2)
                tax_data += self.parse_number(tax.amount, 18, 3)
                tax_data += self.parse_number(tax.base, 18, 3)
            f.write(tax_data)

        f.close()

    def check_picking_data(self, picking):
        errors = ''
        gln_ef = picking.company_id.gln_ef
        gln_ve1 = picking.company_id.gln_ve
        gln_ve2 = picking.partner_id.commercial_partner_id.gln_ve
        gln_de = picking.partner_id.gln_de
        gln_rf = picking.partner_id.gln_rf
        gln_co = picking.partner_id.gln_co
        gln_rm = picking.partner_id.gln_rm
        gln_proveedor = picking.supplier_id and \
            (picking.supplier_id.commercial_partner_id.gln_desadv or 
             picking.supplier_id.commercial_partner_id.gln_de)
        gln_desadv = picking.partner_id.commercial_partner_id.gln_desadv or picking.partner_id.gln_de
        if not self.check_ean13(gln_ef) or not self.check_ean13(gln_ve1):
            errors += _('The company %s not have some GLN defined correctly.\n') % \
                picking.company_id.name
        if not self.check_ean13(gln_de) or not self.check_ean13(gln_rf) or \
           not self.check_ean13(gln_co) or not self.check_ean13(gln_rm) or \
           not self.check_ean13(gln_desadv) or \
           (gln_ve2 and not self.check_ean13(gln_ve2)):
            errors += _('The partner %s not have some GLN defined correctly.\n') % \
                picking.partner_id.name
        if picking.supplier_id and not self.check_ean13(gln_proveedor):
            errors += _('The supplier %s not have recipient GLN defined correctly.\n') % \
                picking.supplier_id.commercial_partner_id.name
        if not picking.company_id.gs1:
            errors += _('\nThe company %s not have gs1') % picking.company_id.name
        for move in picking.move_lines.filtered(lambda r: r.state == 'done'):
            if not move.product_id.ean13:
                errors += _('\nThe product %s not have ean13') % move.product_id.name
            if not move.product_id.dun14:
                errors += _('\nThe product %s not have dun14') % move.product_id.name
        if errors:
            raise orm.except_orm(_('Data error'), errors)

    def get_sscc(self, picking, num):
        """Calculo del codigo SSCC y el digito de control"""
        sscc = '1' + picking.company_id.gs1
        pick_num = str(picking.id)
        pick_num = pick_num[len(pick_num)-7:] if len(pick_num) > 7 else pick_num
        pick_num = int(pick_num)
        sscc += self.parse_number(pick_num, 7, 0) + self.parse_number(num, 2, 0)
        # Calculo del digito de control
        pair_num = sum([int(sscc[i:i+1]) for i in range(len(sscc)) if (i+1)%2==0])
        odd_num = sum([int((sscc[i:i+1])) for i in range(len(sscc)) if (i+1)%2!=0])
        total_num = pair_num + odd_num * 3
        # Se busca el multiplo de 12
        aux_num = total_num
        while aux_num % 10 != 0:
            aux_num += 1
        control = aux_num - total_num
        return str(sscc) + str(control)

    def get_gs1_128_barcode_image(self, value, width, barWidth = 0.05 * units.inch, fontSize = 30, humanReadable = True):
        barcode = createBarcodeDrawing('Code128', value = value, barWidth = barWidth, fontSize = fontSize, humanReadable = humanReadable)
        drawing_width = width
        barcode_scale = drawing_width / barcode.width
        drawing_height = barcode.height * barcode_scale
        drawing = Drawing(drawing_width, drawing_height)
        drawing.scale(barcode_scale, barcode_scale)
        drawing.add(barcode, name='barcode')
        data = b64encode(renderPM.drawToString(drawing, fmt = 'PNG'))
        return data

    def get_packing_ids(self, cr, uid, picking, context):
        t_uom = self.pool.get('product.uom')
        packing_ids = {}
        if picking.packing_ids:
            line_ids = picking.packing_ids.sorted(key=lambda a: (a.product_pack, a.product_id, a.lot_id))
            for line in line_ids:
                if line.product_pack not in packing_ids:
                    packing_ids[line.product_pack] = []
                product_qty_uos = t_uom._compute_qty(cr, uid, line.product_uom_id.id, line.product_qty, line.product_id.uos_id.id)
                packing_ids[line.product_pack].append({'product_id': line.product_id,
                                                       'product_uom_id': line.product_uom_id,
                                                       'product_qty': line.product_qty, 
                                                       'product_uos_id': line.product_id.uos_id,
                                                       'product_qty_uos': product_qty_uos, 
                                                       'lot_id': line.lot_id})
        else:
            line_ids = picking.pack_operation_ids.filtered(lambda r: r.product_qty > 0.0)
            line_ids = line_ids.sorted(key=lambda a: (a.product_id, a.lot_id))
            packing_ids[1] = []
            for line in line_ids:
                product_qty_uos = t_uom._compute_qty(cr, uid, line.product_uom_id.id, line.product_qty, line.product_id.uos_id.id)
                packing_ids[1].append({'product_id': line.product_id,
                                       'product_uom_id': line.product_uom_id,
                                       'product_qty': line.product_qty, 
                                       'product_uos_id': line.product_id.uos_id,
                                       'product_qty_uos': product_qty_uos, 
                                       'lot_id': line.lot_id})
        return packing_ids
        
    def parse_picking(self, cr, uid, picking, file_name, context=None):

        def parse_address(address):
            address_data = ''
            address_data += self.parse_string(address.name, 35)
            address_data += self.parse_string(address.street, 35)
            address_data += self.parse_string(address.city, 35)
            address_data += self.parse_string(address.zip, 5)
            return address_data

        user_tz = self.pool['res.users'].browse(cr, uid, uid).tz
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(user_tz)

        self.check_picking_data(picking)
        f = codecs.open(file_name, 'w', 'utf-8')

        gln_ef = picking.company_id.gln_ef
        gln_de = picking.partner_id.gln_de
        gln_rf = picking.partner_id.gln_rf
        gln_co = picking.partner_id.gln_co
        gln_rm = picking.partner_id.gln_rm
        gln_proveedor = picking.supplier_id and \
            (picking.supplier_id.commercial_partner_id.gln_desadv or 
             picking.supplier_id.commercial_partner_id.gln_de)
        gln_desadv = picking.partner_id.commercial_partner_id.gln_desadv or picking.partner_id.gln_de

        if picking.partner_id.commercial_partner_id.edi_picking_numeric:
            picking_name = ''.join(c for c in picking.name if c.isdigit())
        else:
            picking_name = picking.name

        # Identificador de registro - 0
        picking_data = '0'

        # Buzón de destino
        picking_data += self.parse_number(gln_de, 13, 0)
        
        # Número de aviso de expedición
        picking_data += self.parse_string(picking_name, 35)
        
        # Tipo de documento
        picking_data += self.parse_string('351', 3)
        
        # Función del mensaje
        picking_data += self.parse_string('9', 3)
        
        # Fecha de emisión del aviso de expedición
        date = picking.date_done or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
        date = datetime.strftime(date, '%Y-%m-%d')
        picking_data += self.parse_short_date(date) # Hay que enviar fecha corta aunque el campo tenga espacio para fecha larga
        picking_data += self.parse_string('', 4) # Se rellena el resto del campo
        
        # Fecha / hora de entrega de mercancía
        date = picking.requested_date # Esta es fecha corta. Si el cliente requiere la hora hay que leerlo del pedido o redefinir el campo.
        if date: # Hay que enviar fecha larga, aunque el campo no la incluye.
            date = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=from_zone).astimezone(to_zone)
            date = datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        picking_data += self.parse_long_date(date) if date else ' ' * 12
        
        # Fecha de envío 
        date = picking.date_done or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
        date = datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        picking_data += self.parse_long_date(date)
        
        # Número de albarán
        picking_data += self.parse_string(picking_name, 35)
        
        # Número del pedido
        picking_data += self.parse_string(picking.client_order_ref, 35)
        
        # Fecha del pedido (AAAAMMDD)
        date = picking.sale_id.requested_date or picking.sale_id.date_order or picking.date
        picking_data += self.parse_short_date(date[:10]) if date else ' ' * 8
        picking_data += self.parse_string('', 4) # Aunque la fecha es corta, se mantiene el tamaño de la larga

        # Código EAN origen del mensaje (Operador logístico o proveedor)
        picking_data += self.parse_number(gln_ef, 13, 0)
        
        # Código EAN proveedor de la mercancía. El de la compañía si mercancía propia, sino el del proveedor de la mercancía.
        if picking.supplier_id:
            picking_data += self.parse_number(gln_proveedor, 13, 0)
        else:
            picking_data += self.parse_number(gln_ef, 13, 0)

        # Código EAN destino del mensaje
        picking_data += self.parse_number(gln_desadv, 13, 0)

        # Código EAN lugar de entrega mercancía
        picking_data += self.parse_number(gln_rm, 13, 0)

        # Código EAN Comprador
        picking_data += self.parse_number(gln_co, 13, 0)

        # Código EAN punto de recogida
        picking_data += self.parse_number(gln_ef, 13, 0)

        # Código interno proveedor (CIP)
        edi_supplier_cip = picking.partner_id.commercial_partner_id.edi_supplier_cip
        # Hay una excepción para El Corte Inglés. En el desadv enviamos el código departamento interno en lugar del código de proveedor.
        if picking.partner_id.commercial_partner_id.edi_filename == u'ECI':
            # Para El Corte Inglés enviamos el código departamento interno en lugar del código de proveedor.
            edi_supplier_cip = picking.partner_id.commercial_partner_id.department_code_edi
        elif (edi_supplier_cip == u'03072901'
              and gln_rf in (u'8424818010006', u'8424818290002') # FRZ ó VMR
              and gln_rm not in (u'8424818019016', u'8424818299012')): # No es una Plataforma
            # En VQ, para FRZ/VMR debemos indicar un código de proveedor para
            # Tiendas (03072900), otro para Plataforma (03072901) y otro para EMD (03072902).
            # VQ usa un mismo partner con sus direcciones (incluida plataforma) para Tiendas y Plataforma y otro para EMD.
            # Debemos sin embargo diferenciar las Tiendas de la Plataforma y lo haremos mediante código.
            # En el partner (matriz) establecemos el de Plataforma y el de EMD y en código aplicamos la excepción para tiendas,
            # para las cuales podemos enviar el código 03072900 u omitirlo. Es preferible omitirlo ya que
            # lo contrario podría generar rechazos para otros partners del mismo grupo en los cuales no se estaba enviando.
            edi_supplier_cip = False
        picking_data += self.parse_string(edi_supplier_cip, 10)

        # Medio de transporte (30=Transporte por carretera, 20=Trasporte ferroviario)
        picking_data += self.parse_string('30', 3)

        # Código EAN del transportista
        picking_data += self.parse_number('', 13, 0)
        
        # Matrícula del camión
        picking_data += self.parse_string('', 35)
        
        # Espacio reservado para etiqueta si la genera GENERIX
        picking_data += parse_address(picking.company_id)
        picking_data += parse_address(picking.partner_id.commercial_partner_id)
        picking_data += parse_address(picking.partner_id)
        picking_data += self.parse_string('', 8)
        
        f.write(picking_data)
        
        # Identificador de registro - 1
        picking_data = '\r\n1'
        # Número de identificación en la jerarquía de niveles de empaquetamiento
        picking_data += self.parse_number(1, 1, 0)
        if picking.packing_ids:
            picking_data += self.parse_number(len(list(set([x.product_pack for x in picking.packing_ids]))), 12, 0)
            picking_data += self.parse_string(picking.packing_ids[0].pack_id.code, 3)
        # Si no se han configurado los packs se añaden todas las lineas a un palet.
        else:
            picking_data += self.parse_number(1, 12, 0)
            picking_data += self.parse_string('201', 3)
        f.write(picking_data)

        packing_ids = self.get_packing_ids(cr, uid, picking, context)
        for k, val in packing_ids.items():
            num = k
            # Identificador de registro – 2
            picking_data = '\r\n2'
            # Número de identificación en la jerarquía de niveles de empaquetamiento
            picking_data += self.parse_number(num, 12, 0)
            # Nivel jerárquico del que depende el nivel actual
            picking_data += self.parse_number(1, 12, 0)
            # Número de paquetes dentro de esta unidad de embalaje
            total_qty = sum([v['product_qty_uos'] for v in val])
            picking_data += self.parse_number(total_qty, 15, 0)
            # Tipo de embalaje
            picking_data += self.parse_string('CT', 3)
            # Instrucción de manipulación (DDE = Solamente si tiene localizaciones)
            picking_data += self.parse_string('', 3)
            # Instrucción de manipulación (9 = Solamente si tiene localizaciones)
            picking_data += self.parse_string('', 3)
            # Instrucciones de marcaje (33E)
            picking_data += self.parse_string('33E', 3)
            # Código Seriado de Unidad de Envío (BJ)
            picking_data += self.parse_string('BJ', 3)
            # SSCC de la unidad de expedición
            picking_data += self.parse_string(self.get_sscc(picking, num), 35)
            f.write(picking_data)
            # LINEAS
            num_lin = 1
            for v in val:
                # Identificador de registro – 3
                picking_data = '\r\n3'
                # Número de línea
                picking_data += self.parse_number(num_lin, 4, 0)
                # Código EAN del artículo
                picking_data += self.parse_string(v['product_id'].ean13, 17)
                # Número del artículo según comprador
                picking_data += self.parse_string(v['product_id'].partner_product_code, 35)
                # Número del artículo según vendedor
                picking_data += self.parse_string(v['product_id'].default_code, 35)
                # Descripción del artículo
                picking_data += self.parse_string(v['product_id'].with_context(lang=picking.partner_id.lang).name, 35)
                # Descripción del artículo codificada
                picking_data += self.parse_string('', 3)
                # Cantidad enviada total
                picking_data += self.parse_number(v['product_qty'], 15, 3)
                # Cantidad enviada gratuita
                picking_data += self.parse_number('0', 15, 3)
                # Cantidad pedida por el comprador
                picking_data += self.parse_number(v['product_qty'], 15, 3)
                # Número de Unidades de Consumo en la Unidad de Expedición (Unidades x caja)
                qty = round(1 / (v['product_id'].uos_coeff or 1))
                picking_data += self.parse_number(qty, 15, 3)
                # Peso neto total de la linea
                picking_data += self.parse_number(v['product_qty'] * v['product_id'].weight_net, 15, 3)
                # Punto de entrega final
                picking_data += self.parse_string(gln_rm, 25)
                # Marca número de lote / Fecha de caducidad (36E = El corte inglés, 17 = Alcampo)
                picking_data += self.parse_string(picking.partner_id.commercial_partner_id.product_marking_code, 3)
                # Fecha de caducidad
                edi_desadv_lot_date = picking.partner_id.commercial_partner_id.edi_desadv_lot_date or 'best_before'
                use_date = v['lot_id'].use_date or ''
                if use_date:
                    use_date = datetime.strptime(use_date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
                    use_date = datetime.strftime(use_date, '%Y-%m-%d')
                    use_date = self.parse_short_date(use_date) # Enviamos fecha corta
                picking_data += self.parse_string(use_date if edi_desadv_lot_date == 'expiry' else '', 12)
                # Fecha de consumo preferente
                picking_data += self.parse_string(use_date if edi_desadv_lot_date == 'best_before' else '', 12)
                # Fecha de fabricación
                picking_data += self.parse_string('', 12)
                # Fecha de empaquetado
                picking_data += self.parse_string('', 12)
                # Cantidad dividida
                picking_data += self.parse_number('0', 15, 0)
                # Calificador número de lote (BX)
                picking_data += self.parse_string('BX', 3)
                # Número de lote
                picking_data += self.parse_string(v['lot_id'].name, 18)
                # DUN14 Caja
                picking_data += self.parse_number(v['product_id'].dun14, 14, 0)
                f.write(picking_data)
                num_lin += 1
        f.close()

    def check_coacsu_data(self, invoice_ids):
        errors = ''
        gln_ve = invoice_ids[0].partner_id.commercial_partner_id.gln_ve or \
                 invoice_ids[0].company_id.gln_ve
        gln_de_coa = invoice_ids[0].partner_id.commercial_partner_id.gln_de_coa
        gln_rm_coa = invoice_ids[0].partner_id.commercial_partner_id.gln_rm_coa
        for invoice in invoice_ids:
            if invoice.state not in ('open', 'paid'):
                raise orm.except_orm(_('Invoice error'), _('Validate the invoices before.'))
            gln_ve_aux = invoice.partner_id.commercial_partner_id.gln_ve or \
                     invoice.company_id.gln_ve
            gln_de_coa_aux = invoice.partner_id.commercial_partner_id.gln_de_coa
            gln_rm_coa_aux = invoice.partner_id.commercial_partner_id.gln_rm_coa
            if gln_ve != gln_ve_aux:
                errors += _('Se han seleccionado facturas con distintos GLN de vendedor. [gln_ve]\n')
            if gln_de_coa != gln_de_coa_aux:
                errors += _('Se han seleccionado facturas con distintos GLN de destinatario COACSU. [gln_de_coa]\n')
            if gln_rm_coa != gln_rm_coa_aux:
                errors += _('Se han seleccionado facturas con distintos GLN de receptor mensaje COACSU.[gln_rm_coa]\n')
            invoice_part = invoice.partner_id
            picking_part = invoice.picking_ids and invoice.picking_ids[0].partner_id or False
            gln_rf = picking_part and picking_part.gln_rf or invoice_part.gln_rf
            if not self.check_ean13(gln_rf):
                errors += _('The partner %s not have some GLN defined correctly. [gln_rf]\n') % \
                    invoice.partner_id.name
            if not invoice.date_invoice:
                errors += _('The invoice not have date.\n')
        if not self.check_ean13(gln_ve) or not self.check_ean13(gln_de_coa) or not self.check_ean13(gln_rm_coa):
            errors += _('Some partners do not have a GLN defined correctly. [gln_ve / gln_de_coa / gln_rm_coa]\n')
        if errors:
            raise orm.except_orm(_('Data error'), errors)

    def parse_coacsu(self, cr, uid, invoice_ids, file_name, date_due, context=None):
        self.check_coacsu_data(invoice_ids)
        f = codecs.open(file_name, 'w', 'utf-8')
        gln_ve = invoice_ids[0].partner_id.commercial_partner_id.gln_ve or \
                 invoice_ids[0].company_id.gln_ve
        gln_de_coa = invoice_ids[0].partner_id.commercial_partner_id.gln_de_coa
        gln_rm_coa = invoice_ids[0].partner_id.commercial_partner_id.gln_rm_coa

        # Id de registro - CAB
        coacsu_data = 'CAB'
        # EAN buzón de destino
        coacsu_data += self.parse_number(gln_de_coa, 13, 0)
        # Número de relación de factura
        number = file_name.replace('.ASC','').split('/')[-1]
        coacsu_data += self.parse_string(number, 35)
        # Fecha generación mensaje
        coacsu_data += self.parse_long_date(time.strftime('%Y-%m-%d %H:%M:%S'))
        # EAN emisor del mensaje
        coacsu_data += self.parse_number(gln_ve, 13, 0)
        # EAN receptor del mensaje
        coacsu_data += self.parse_number(gln_rm_coa, 13, 0)
        # Divisa de referencia
        coacsu_data += self.parse_string(invoice_ids[0].currency_id.name or u'EUR', 3)
        # Condiciones de pago
        coacsu_data += self.parse_string(u'1', 3)
        # Fecha de vencimiento
        coacsu_data += self.parse_string(self.parse_short_date(date_due), 12)
        # Importe total relación facturas
        imp_total = sum([x.amount_total for x in invoice_ids])
        coacsu_data += self.parse_number(imp_total, 18, 3)
        f.write(coacsu_data)
        
        # RELACION DE FACTURAS
        for invoice in invoice_ids:
            # Id de registro - DOC
            coacsu_data = '\r\nDOC'
            # Número de factura
            coacsu_data += self.parse_string(invoice.number, 35)
            # Fecha factura
            coacsu_data += self.parse_string(self.parse_short_date(invoice.date_invoice), 12)
            # EAN receptor factura
            invoice_part = invoice.partner_id
            picking_part = invoice.picking_ids and invoice.picking_ids[0].partner_id or False
            gln_rf = picking_part and picking_part.gln_rf or invoice_part.gln_rf
            coacsu_data += self.parse_number(gln_rf, 13, 0)
            # Importe factura
            coacsu_data += self.parse_number(invoice.amount_total, 18, 3)
            f.write(coacsu_data)
        f.close()

    def export_files(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0])
        path = wizard.configuration.ftpbox_path + "/out"
        if not (context.get('coacsu', False) and context['active_model'] == u'account.invoice'):
            for obj in self.pool.get(context['active_model']).browse(cr, uid, context['active_ids']):
                if not obj.company_id.edi_code:
                    raise orm.except_orm(_('Company error'), _('Edi code not established in company'))
                if not obj.partner_id.commercial_partner_id.edi_filename:
                    raise orm.except_orm(_('Partner error'), _('Edi filename not established in partner'))
                if context['active_model'] == u'stock.picking':
                    file_name = '%s%sEDI%s%s%s.ASC' % (path, os.sep, obj.company_id.edi_code, obj.name.replace('/','').replace('\\',''), obj.partner_id.commercial_partner_id.edi_filename)
                    self.parse_picking(cr, uid, obj, file_name, context)
                elif context['active_model'] == u'account.invoice':
                    if obj.edi_not_send_invoice:
                        continue
                    if obj.state not in ('open', 'paid'):
                        raise orm.except_orm(_('Invoice error'), _('Validate the invoice before.'))
                    file_name = '%s%sINV%s%s%s.ASC' % (path, os.sep, obj.company_id.edi_code, obj.number.replace('/','').replace('\\',''), obj.partner_id.commercial_partner_id.edi_filename)
                    self.parse_invoice(cr, uid, obj, file_name, context)
                self.create_doc(cr, uid, wizard.id, obj, file_name, context)
        else:
            invoice_ids = self.pool.get(context['active_model']).browse(cr, uid, context['active_ids'])
            invoice_ids = invoice_ids.filtered(lambda x: not x.edi_not_send_coacsu)
            if not invoice_ids:
                raise orm.except_orm(_('Invoice error'), _('No invoices to send in coacsu by EDI'))
            if not invoice_ids[0].company_id.edi_code:
                raise orm.except_orm(_('Company error'), _('Edi code not established in company'))
            if not invoice_ids[0].partner_id.commercial_partner_id.edi_filename:
                raise orm.except_orm(_('Partner error'), _('Edi filename not established in partner'))
            file_name = '%s%sCOA%s%s.ASC' % (path, os.sep, invoice_ids[0].company_id.edi_code, wizard.id)
            self.parse_coacsu(cr, uid, invoice_ids, file_name, wizard.date_due, context)
            self.create_doc(cr, uid, wizard.id, invoice_ids, file_name, context)
        return True
