# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-TODAY
#        Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
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

from openerp.osv import orm, fields
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class edi_doc(orm.Model):
    _name = "edi.doc"
    _description = "Documento EDI"
    _columns = {
        'name': fields.char('Referencia', size=255, required=True),
        'file_name':fields.char('Nombre fichero', size=64),
        'type': fields.selection([('orders', 'Pedido'), ('ordrsp', 'Respuesta Pedido'), 
                                  ('desadv', 'Albarán'), ('recadv', 'Confirmación mercancía'), 
                                  ('invoic', 'Factura')], 'Tipo de documento', select=1),
        'date': fields.datetime('Descargado el', size=255),
        'date_process': fields.datetime('Procesado el', size=255),
        'status': fields.selection([('draft', 'Sin procesar'), ('imported', 'Importado'),
                                    ('export', 'Exportado'), ('error', 'Con incidencias')], 'Estado', select=1),
        'sale_order_id': fields.many2one('sale.order','Pedido', ondelete='restrict'),
        'picking_id' : fields.many2one('stock.picking','Albarán', ondelete='restrict'),
        'invoice_id' : fields.many2one('account.invoice','Factura', ondelete='restrict'),
        'send_date': fields.datetime('Fecha del último envío', select=1),
        'message': fields.text('Mensaje'),
        'gln_ef': fields.char('GLN Emisor Factura', size=60, help="GLN (Emisor del documento)"),
        'gln_ve': fields.char('GLN Vendedor', size=60, help="GLN (Vendedor de la mercancía)"),
        'gln_de': fields.char('GLN Destinatario', size=60, help="GLN (Destinatario de la factura / Quien paga)"),
        'gln_rf': fields.char('GLN Receptor Factura', size=60, help="GLN (Receptor de la factura / A quien se factura)"),
        'gln_co': fields.char('GLN Comprador', size=60, help="GLN (Comprador / Quien pide)"),
        'gln_rm': fields.char('GLN Receptor Mercancía', size=60, help="GLN (Receptor de la mercancía / Quien recibe)"),
    }
    _order = 'date desc'


class edi_configuration(orm.Model):
    _name = "edi.configuration"
    _description = "Configuracion EDI"
    _columns = {
        'name':fields.char('Nombre', size=255, required=True),
        'salesman': fields.many2one('res.users', 'Comercial para los pedidos.', help="Seleccione el comercial que será asignado a todos los pedidos."),
        'ftp_host': fields.char('Host', size=255),
        'ftp_port': fields.char('Puerto', size=255),
        'ftp_user': fields.char('Usuario', size=255),
        'ftp_password': fields.char('Password', size=255),
        'local_mode': fields.boolean('Modo local', help='Si es activado, el módulo no realizará conexiones al ftp. Sólo trabajará con los ficheros y documentos pendientes de importación.'),
        'ftpbox_path': fields.char('Ruta ftpbox (Sin / al final)', size=255, required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(edi_configuration, self).default_get(cr, uid, fields, context=context)
        res.update({'local_mode': True})
        return res

    def get_configuration(self, cr, uid, ids):

        ids = self.pool.get('edi.configuration').search(cr, uid, [])
        if not ids:
            raise osv.except_osv(_("No hay una configuración EDI. "),_("Falta configuración"))
        else :
            return pool.get('edi.configuration').browse(cr, uid, ids[0])


# -------------------------- PERSONALIZACIONES CON CAMPOS DE EDI ------------------------------------
'''class sale_order(orm.Model):

    _inherit = 'sale.order'
    _columns = {
        'edi_docs': fields.one2many('edi.doc','sale_order_id','Documento EDI'),
        'order_type': fields.selection(
            [ ('ORI', 'ORI'),('REP', 'REP'),('DEL','DEL') ],
            'Tipo', readonly=True),
        'funcion_mode': fields.selection ([ ('0', 'Aceptación ORDERS'),('1', 'Rechazo ORDERS'),('2', 'Oferta alternativa'),('3', 'Valoración ORDERS')],'Funcion'),
        'top_date':fields.date('Fecha limite'),
        'urgent':fields.boolean('Urgente'),
        'num_contract': fields.char('Contract Number', size=128),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """ sobrescribimos el copy para que no duplique los documentos"""
        if not default:
            default = {}
        default.update({
            'edi_docs': [],
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale = self.pool.get('sale.order').write(cr,uid,ids,{'funcion_mode' : '1'},context=context)
        return super(sale_order, self).action_cancel(cr, uid, ids,context=context)

    def action_ship_create(self, cr, uid, ids, *args):
        sale = self.pool.get('sale.order').write(cr,uid,ids,{'funcion_mode' : '0'})
        return super(sale_order, self).action_ship_create(cr, uid, ids,*args)

    def _prepare_order_picking(self, cr, uid, order, context=None):
        if context is None: context = {}
        res = super(sale_order, self)._prepare_order_picking(cr, uid, order, context=context)
        if order.num_contract:
            res['num_contract'] = order.num_contract

        return res

sale_order()'''


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'section_code': fields.char('Section/Supplier or Branch', size=9,
                                           help="Código de sección/proveedor o sucursal. Ejemplo: para Alcampo se refiere a la Sección/Proveedor(SSS/PPPPP)."),
        'department_code_edi': fields.char('Internal department code', size=3,
                                           help="Internal department code for edi when required by customer. Only El Corte Inglés customer requires this code currently."),
        'product_marking_code': fields.char('Product marking instructions code', size=3,
                                           help="EDI (DESADV). Code specifying product marking instructions. Segment: PCI, Tag: 4233. Example: 36E, 17, ..."),
        'edi_date_required': fields.boolean('EDI lines requires picking date',
                                           help='Check if customer requires the picking date in the EDI lines of invoice.'),
        'edi_filename': fields.char('EDI filename suffix', size=3,
                                           help='Partner suffix for edi filename.'),
        'gln_de': fields.char('GLN Destinatario', size=13, help="GLN (Destinatario de la factura / Quien paga)"),
        'gln_rf': fields.char('GLN Receptor Factura', size=13, help="GLN (Receptor de la factura / A quien se factura)"),
        'gln_co': fields.char('GLN Comprador', size=13, help="GLN (Comprador / Quien pide)"),
        'gln_rm': fields.char('GLN Receptor Mercancía', size=13, help="GLN (Receptor de la mercancía / Quien recibe)"),
    }


class payment_mode(orm.Model):

    _inherit = 'payment.mode'
    _columns = {
        'edi_code': fields.selection([('42', 'A una cuenta bancaria'), ('14E', 'Giro bancario'),
                                      ('10', 'En efectivo'), ('20', 'Cheque'),
                                      ('60', 'Pagaré')], 'Codigo EDI', select=1)
    }

class product_uom(orm.Model):

    _inherit = 'product.uom'
    _columns = {
        'edi_code': fields.selection([('PCE', '[PCE] Unidades'), ('KGM', '[KGM] Kilogramos'),
                                      ('LTR', '[LTR] Litros')], 'Código EDI', 
                                     select=1, help="Código para el tipo de UOM a incluir en el fichero EDI."),
    }

'''class stock_picking(orm.Model):

    _inherit = 'stock.picking'
    _columns = {
        'num_contract': fields.char('Contract Number', size=128),
        'edi_docs': fields.one2many('edi.doc','picking_id','Documentos EDI'),
        'return_picking_id': fields.many2one('stock.picking','Albaran de devolucion', readonly=True),
    }

    def copy(self, cr, uid, id, default=None, context=None):
        """ sobrescribimos el copy para que no duplique los documentos"""
        if not default:
            default = {}
        default.update({
            'edi_docs': [],
            'return_picking_id': False
        })

        return super(stock_picking, self).copy(cr, uid, id, default, context=context)

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,invoice_vals, context=None):
        """Actualizamos la cantidad de la linea a la cantidad aceptada del movimiento"""
        if context == None:
            context={}
        res = super(stock_picking,self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,invoice_vals, context=context)
        # Actualizamos la cantidad si el movimiento no es de devolución.
        res.update({'quantity': (move_line.acepted_qty or move_line.product_qty )})

        if move_line.rejected and not move_line.acepted_qty:
            res = {}
        return res

    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        """Lanzamos excepción al crear la factura si la posición fiscal de los pedidos de las lineas son diferentes"""
        res = super(stock_picking,self).action_invoice_create(cr, uid, ids, journal_id, group, type,context) #res diccionario de la forma {id_del_albaran:id_de_la_factura}
        set_fp = set()
        for inv_id in set(res.values()):  # nos recorremos las facturas diferentes
            inv = self.pool.get('account.invoice').browse(cr,uid,inv_id,context)

            for line in inv.invoice_line:
                if line.sale_line_id:
                    set_fp.add(line.sale_line_id.order_id.fiscal_position.id)

            if len(set_fp) > 1: #hay mas de una posición fiscal
                raise osv.except_osv(_('Error'), _('Las posiciones fiscales de los pedidos son diferentes'))
            elif set_fp:
                inv.write({'fiscal_position' : list(set_fp)[0] })
        return res

stock_picking()'''

'''class stock_move(orm.Model):
    _inherit = 'stock.move'

    _columns = {
        'acepted_qty' : fields.float('Cantidad aceptada', digits_compute=dp.get_precision('Product Unit of Measure'),readonly=True),
        'rejected' : fields.boolean('Rechazado'),
    }

    _order = 'date desc'

stock_move()'''


class account_tax(orm.Model):

    _inherit = "account.tax"

    _columns = {
        'edi_code': fields.selection([('VAT', '[VAT] IVA'), ('ENV', '[ENV] Punto Verde'),
                                    ('EXT', '[EXT] Exento de IVA'), ('ACT', '[ACT] Impuesto de Alcoholes')], 'Código impuesto para EDI', select=1,
                                     help="Código para el tipo de impuesto a incluir en el fichero EDI (si ninguno se usará VAT)."),
    }

class account_invoice_tax(orm.Model):

    _inherit = 'account.invoice.tax'

    _columns = {
        'tax_id': fields.many2one('account.tax', 'Tax'),
    }

    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        #inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        inv = invoice_id
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            discount_line = round(1-(line.discount or 0.0)/100.0, 4)
            discount_global = round(1-(line.invoice_id.global_disc or 0.0)/100.0, 4)
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, ((line.price_unit * discount_line) * discount_global), line.quantity, line.product_id, inv.partner_id)['taxes']:
                #tax['price_unit'] = cur_obj.round(cr, uid, cur, tax['price_unit'])
                val={}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['tax_id'] = tax['id']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['quantity']
                val['base'] = cur_obj.round(cr, uid, cur, val['base'])

                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        #res = super(account_invoice, self)._amount_all(cr, uid, ids, name, args, context)
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'total_global_discounted': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal - (line.price_subtotal * (line.invoice_id.global_disc/100))
                res[invoice.id]['total_global_discounted'] += line.price_subtotal * (line.invoice_id.global_disc/100)
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    _columns = {
        'global_disc': fields.float('Global discount'),
        'total_global_discounted': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='global discount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'num_contract': fields.char('Contract Number', size=128),
        'edi_docs': fields.one2many('edi.doc', 'invoice_id', 'Documentos EDI'),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit', 'invoice_line_tax_id', 'quantity', 'discount', 'invoice_id'], 20),
            },
            multi='all'),
    }

class res_company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'gln_ef': fields.char(string='GLN Emisor Factura',help="GLN (Emisor del documento)"),
        'gln_ve': fields.char(string='GLN Vendedor', help="GLN (Vendedor de la mercancía)"),
        'edi_code': fields.char(string='EDI filename prefix', help='Company prefix for edi filename'),
        'gs1': fields.char(string='GS1 code', help='AECOC GS1 code of the Company. Used to coding GTIN-13, GTIN-14, GS1-128, SSCC, etc. Required for EDI DESADV interchanges.'),
    }
