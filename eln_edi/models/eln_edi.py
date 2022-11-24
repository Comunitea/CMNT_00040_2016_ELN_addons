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

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class EdiDoc(models.Model):
    _name = 'edi.doc'
    _description = 'EDI Document'
    _order = 'date desc'

    name = fields.Char('Reference', size=256, required=True)
    file_name = fields.Char('File name', size=64)
    type = fields.Selection([
        ('orders', 'Order'),
        ('ordrsp', 'Purchase order response'),
        ('desadv', 'Despatch advice'),
        ('recadv','Receiving advice'),
        ('invoic','Invoice'),
        ('coacsu','Commercial account summary'),
        ], string='Document type', select=1)
    date = fields.Datetime('Downloaded on')
    date_process = fields.Datetime('Processed on')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('imported', 'Imported'),
        ('exported', 'Exported'),
        ('error','With errors'),
        ], string='Status', select=1)
    sale_order_id = fields.Many2one('sale.order', 'Sale order', ondelete='restrict')
    picking_id = fields.Many2one('stock.picking', 'Picking', ondelete='restrict')
    invoice_id = fields.Many2one('account.invoice', 'Invoice', ondelete='restrict')
    coacsu_invoice_ids = fields.Many2many(
        'account.invoice', string='COACSU',
        rel='account_invoice_coacsu_rel',
        id1='invoice_id', id2='edi_doc_id'
    )
    send_date = fields.Datetime('Last sending date', select=1)
    message = fields.Text('Message')
    gln_ef = fields.Char('GLN Invoice Issuer', size=13,
        help="GLN (Document issuer)")
    gln_ve = fields.Char('GLN Seller', size=13,
        help="GLN (Seller of the goods)")
    gln_de = fields.Char('GLN Recipient', size=13,
        help="GLN (Invoice recipient / Who pays)")
    gln_rf = fields.Char('GLN Invoice receiver', size=13,
        help="GLN (Invoice receiver / Who is billed)")
    gln_co = fields.Char('GLN Buyer', size=13,
        help="GLN (Buyer / Who order)")
    gln_rm = fields.Char('GLN Goods receiver', size=13,
        help="GLN (Receiver of the goods / Who receives)")
    gln_supplier = fields.Char('GLN Picking supplier', size=13) # DESADV
    gln_desadv = fields.Char('GLN Picking receiver', size=13) # DESADV


class EdiConfiguration(models.Model):
    _name = 'edi.configuration'
    _description = 'EDI Configuration'

    name = fields.Char('Name', size=256,
        required=True)
    salesman = fields.Many2one('res.users', 'Commercial for orders',
        help="Commercial that will be assigned to all orders")
    ftp_host = fields.Char('Host', size=256)
    ftp_port = fields.Char('Port', size=256)
    ftp_user = fields.Char('User', size=256)
    ftp_password = fields.Char('Password', size=256)
    local_mode = fields.Boolean('Local mode',
        help="If enabled, the module will not make connections to ftp. It will only work with files and documents pending import.")
    ftpbox_path = fields.Char('Ftpbox path (without / at the end)', size=256,
        required=True)

    @api.model
    def default_get(self, fields):
        res = super(EdiConfiguration, self).default_get(fields)
        res.update({'local_mode': True})
        return res

    @api.model
    def get_configuration(self):
        conf_ids = self.search([], limit=1)
        if not conf_ids:
            raise exceptions.Warning(_('Warning!'), _('No EDI Configurations'))
        return conf_ids


class ResPartner(models.Model):
    _inherit = 'res.partner'

    section_code = fields.Char('Section/Supplier or Branch', size=9,
        company_dependent=True,
        help="Section/Supplier or Branch code. Example: for Alcampo it refers to the Section/Supplier (SSS/PPPPP).")
    edi_supplier_cip = fields.Char('CIP (EDI)', size=9,
        company_dependent=True,
        help="Internal supplier code")
    department_code_edi = fields.Char('Internal department code', size=3,
        help="Internal department code for edi when required by customer. Only El Corte Inglés customer requires this code currently.")
    product_marking_code = fields.Char('Product marking instructions code', size=3,
        help="EDI (DESADV). Code specifying product marking instructions. Segment: PCI, Tag: 4233. Example: 36E, 17, ...")
    edi_date_required = fields.Boolean('EDI lines requires picking date',
        help="Check if customer requires the picking date in the EDI lines of invoice. It is usually not required.")
    edi_order_ref_required = fields.Boolean('EDI lines requires order ref', default=True,
        help="Check if customer requires the order ref in the EDI lines of invoice. Usually it is always required.")
    edi_uos_as_uom_on_kgm_required = fields.Boolean('Use UoS as UoM if UoM is kg',
        help="Check if customer requires invoicing products with UoM kg interpreting UoM = UoS. (1 bag of 5 kg is 1 bag, not 5 kg).")
    edi_filename = fields.Char('EDI filename suffix', size=3,
        help="Partner suffix for edi filename.")
    gln_ve = fields.Char('GLN Seller', size=13,
        help="GLN (Seller of the goods). If set, this will be used instead of the one defined in the Company.")
    gln_de = fields.Char('GLN Recipient', size=13,
        help="GLN (Invoice recipient / Who pays)")
    gln_rf = fields.Char('GLN Invoice receiver', size=13,
        help="GLN (Invoice receiver / Who is billed)")
    gln_co = fields.Char('GLN Buyer', size=13,
        help="GLN (Buyer / Who order)")
    gln_rm = fields.Char('GLN Goods receiver', size=13,
        help="GLN (Receiver of the goods / Who receives)")
    gln_desadv = fields.Char('GLN Picking receiver (DESADV)', size=13,
        help="GLN (Logistic picking receiver (DESADV))")
    gln_de_coa = fields.Char('GLN COA Recipient', size=13,
        help="GLN (Commercial account summary recipient)")
    gln_rm_coa = fields.Char('GLN Message receiver', size=13,
        help="GLN (Message receiver of the commercial account summary)")
    gln_rf_coa = fields.Char('GLN COA Invoice receiver', size=13,
        help="GLN (Invoice receiver / Who is billed)")
    edi_picking_numeric = fields.Boolean('Only numeric picking name (DESADV)',
        help="Check if customer requires the picking name as numeric in DESADV documents. Ex. AS/X00123->00123")
    edi_desadv_lot_date = fields.Selection([
        ('best_before', 'Best before date'),
        ('expiry', 'Expiry date'),
        ], string='Send lot date as', select=1,
        help="Set how the 'best before date' of the lot will be translated in the edi file. If none is selected, it will be sent as 'best before date'.")
    edi_invoice_copy = fields.Boolean('Send invoice copy to payer',
        help="Check if customer requires send invoice copy to payer. For example IFA GROUP requires a copy of the invoice sent to its associates.")
    edi_test_mode = fields.Boolean('Test mode',
        help="Check if customer requires send the edi messages to the test environment before working in real mode.")
    edi_invoic_active = fields.Boolean('Invoic active', default=False)
    edi_desadv_active = fields.Boolean('Desadv active', default=False)
    edi_coacsu_active = fields.Boolean('Coacsu active', default=False)
    edi_note = fields.Text('Notes')


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    edi_code = fields.Selection([
        ('42', 'To a bank account'),
        ('14E', 'Bank draft'),
        ('10', 'Cash payment'),
        ('20', 'Check'),
        ('60', 'Promissory note'),
        ], string='EDI code', select=1)


class ProductUom(models.Model):
    _inherit = 'product.uom'

    edi_code = fields.Selection([
        ('PCE', '[PCE] Units'),
        ('KGM', '[KGM] Kilograms'),
        ('LTR', '[LTR] Liters'),
        ], string='EDI code', select=1,
        help="Code for the type of UdM to include in the EDI file. If not set, [PCE] will be used.")


class AccountTax(models.Model):
    _inherit = "account.tax"

    edi_code = fields.Selection([
        ('VAT', '[VAT] VAT'),
        ('ENV', '[ENV] Green Dot'),
        ('EXT', '[EXT] Exempt from VAT'),
        ('ACT', '[ACT] Alcohol tax'),
        ], string='EDI code', select=1,
        help="Code for the type of tax to include in the EDI file (if none, VAT will be used).")


class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'

    tax_id = fields.Many2one('account.tax', 'Tax')

    @api.v8
    def compute(self, invoice):
        tax_grouped = super(AccountInvoiceTax, self).compute(invoice)
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {}
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if key in tax_grouped:
                    tax_grouped[key]['tax_id'] = tax['id']
        return tax_grouped


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    num_contract = fields.Char('Contract Number', size=128)
    edi_docs = fields.One2many(
        'edi.doc', 'invoice_id', 'EDI Documents',
        readonly=True)
    invoice_coacsu_ids = fields.Many2many(
        'edi.doc', string='COACSU',
        rel='account_invoice_coacsu_rel',
        id1='edi_doc_id', id2='invoice_id'
    )
    edi_not_send_invoice = fields.Boolean('Not send invoice by EDI',
        default=False)
    edi_not_send_coacsu = fields.Boolean('Not send invoice in COACSU by EDI',
        default=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    gln_ef = fields.Char('GLN Invoice Issuer', size=13,
        help="GLN (Document issuer)")
    gln_ve = fields.Char('GLN Seller', size=13,
        help="GLN (Seller of the goods)")
    edi_code = fields.Char('EDI filename prefix', size=3,
        help="Company prefix for EDI filename")
    edi_rm = fields.Char('Commercial Registry',
        help="Commercial Registry of the issuer of the invoice and the seller")


class ProductUl(models.Model):
    _inherit = 'product.ul'

    edi_code = fields.Char('EDI code', size=3,
        help="According to recommendation UN/ECE No. 21")

    @api.multi
    def name_get(self):
        return [(ul.id,
                (ul.edi_code or '000') + (ul.name and (' - ' + ul.name) or ''))
                for ul in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('edi_code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search(['|', ('edi_code', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    edi_docs = fields.One2many(
        'edi.doc', 'picking_id', 'EDI Documents')

    @api.multi
    def action_print_desadv_label(self):
        p_dic = {}
        for picking in self:
            packing_ids = picking.get_packing_ids()
            for k, val in packing_ids.items():
                if picking.id not in p_dic:
                    p_dic[picking.id] = []
                pack_sscc = picking.get_sscc(k)
                pack_gs1_128 = picking.get_gs1_128_barcode_image(str('\xf100') + pack_sscc, width=600, humanReadable=False)
                p_dic[picking.id].append({
                    'product_pack': k,
                    'total_pack': len(packing_ids),
                    'pack_sscc': pack_sscc,
                    'pack_gs1_128': pack_gs1_128
                })
        custom_data = {'lines_dic': p_dic}
        rep_name = 'eln_edi.desadv_report_x1'
        if self._context.get('num_labels', 1) == 2:
            rep_name = 'eln_edi.desadv_report_x2'
        rep_action = self.env['report'].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action

