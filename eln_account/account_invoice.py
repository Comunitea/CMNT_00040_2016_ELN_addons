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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import api, fields as fields2


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    # POST-MIGRATION: nUEVA FUNCIONALIDAD ABAJO, ARRASTRA EL MANY2ONE EN LUGAR DEL BOOLEAN
    # def _received_check(self, cr, uid, ids, name, args, context=None):
    #     res = {}
    #     for inv in self.browse(cr, uid, ids, context=context):
    #         res[inv.id] = False
    #         if inv.move_id and inv.move_id.line_id:
    #             for line in inv.move_id.line_id:
    #                 if line.received_check:
    #                     res[inv.id] = True
    #     return res

    def _received_check(self, cr, uid, ids, name, args, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            res[inv.id] = False
            for payment in inv.payment_ids:
                # if line.received_check:  comentado POST_MIGRATION, no existe campo, se metía en account payment_extension
                if payment.check_deposit_id:
                    res[inv.id] = payment.check_deposit_id.id
        return res

    @api.model
    def _default_journal(self):
        if self._context.get('no_journal', False):
            return False
        return super(account_invoice, self)._default_journal()

    @api.model
    def _default_currency(self):
        if self._context.get('no_journal', False):
            return self.env.user.company_id.currency_id
        return super(account_invoice, self)._default_currency()

    @api.multi
    def onchange_company_id(self, company_id, part_id, type, invoice_line, currency_id):
        res = super(account_invoice, self).onchange_company_id(company_id, part_id, type, invoice_line, currency_id)
        if self._context.get('no_journal', False) and res.get('value', {}).get('journal_id', False):
            res['value']['journal_id'] = False
        return res

    _columns = {
        # 'received_check': fields.function(_received_check, method=True, store=False, type='boolean', string='Received check', help="To write down that a check in paper support has been received, for example."),
        'received_check': fields.function(_received_check, method=True, store=False, type='many2one', relation='account.check.deposit',
                                          string='Received check', help="To write down that a check in paper support has been received, for example."),
        'journal_id': fields.many2one(
            'account.journal', string='Journal', required=True, readonly=True,
            states={'draft': [('readonly', False)]}, default=_default_journal,
            domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale_refund'], 'in_refund': ['purchase_refund'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]"),
        'currency_id': fields.many2one(
            'res.currency', string='Currency', required=True, readonly=True,
            states={'draft': [('readonly', False)]},
            default=_default_currency, track_visibility='always'),
    }


class account_invoice_line(orm.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('quantity')
    def _get_uom_qty(self):
        if self.quantity:
            uom_qty = self.env['product.uom']._compute_qty(self.uos_id.id,
                                                           self.quantity,
                                                           self.product_id.
                                                           uom_id.id)
            self.uom_qty = uom_qty

    @api.multi
    @api.depends('quantity', 'product_id', 'uos_id', 'invoice_id.date_invoice', 'invoice_id.currency_id')
    def _get_cost_subtotal(self):
        product_tmpl_obj = self.env['product.template']
        t_uom = self.env['product.uom']
        for line in self:
            if line.invoice_id.type not in ('out_invoice', 'out_refund'):
                line.cost_subtotal = 0.0
                continue
            price_unit = 0
            quant_qty = 0
            if line.product_id.type != 'service':
                for picking_id in line.invoice_id.picking_ids:
                    for move_line in picking_id.move_lines.filtered(lambda r: r.product_id == line.product_id):
                        for quant in move_line.quant_ids.filtered(lambda r: r.qty > 0):
                            price_unit += quant.cost * quant.qty
                            quant_qty += quant.qty
            if quant_qty:
                price_unit = price_unit / quant_qty
            if not price_unit:
                date = line.invoice_id.date_invoice or fields2.Date.context_today(self)
                price_unit = product_tmpl_obj.get_history_price(line.product_id.product_tmpl_id.id,
                                                                line.company_id.id,
                                                                date=date)
            price_unit = price_unit or line.with_context(force_company=line.company_id.id).product_id.standard_price
            from_unit = line.uos_id.id
            to_unit = line.product_id.uom_id.id
            uom_qty = line.quantity
            if from_unit != to_unit:
                uom_qty = t_uom._compute_qty(from_unit, line.quantity, to_unit)
            sign = -1 if line.price_subtotal < 0 else 1
            line.cost_subtotal = abs(price_unit * uom_qty) * sign
            if line.invoice_id:
                line.cost_subtotal = line.invoice_id.currency_id.round(line.cost_subtotal)

    uom_qty = fields2.Float('Uom Qty', compute=_get_uom_qty)
    cost_subtotal = fields2.Float('Cost Subtotal', compute=_get_cost_subtotal, store=True)

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False,
                      fposition_id=False, price_unit=False, address_invoice_id=False, currency_id=False, context=None, company_id=None):
        """
        Modificamos para no permitir poner cualquier tipo de unidad en la linea de factura.
        Ahora solo aceptará alguna que pertenezca a la misma categoria que la unidad de medida por defecto del producto.
        """
        if context is None:
            context = {}

        update_res = False

        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                update_res = True
                uom = (prod.uos_id and prod.uos_id.id) or (prod.uom_id and prod.uom_id.id) or False

        res = super(account_invoice_line, self).uos_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id,
                                                              fposition_id, price_unit, address_invoice_id, currency_id, context, company_id)

        if update_res:
            res['value']['uos_id'] = uom or False

        return res

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          currency_id=False, company_id=None):
        res = super(account_invoice_line, self).\
            product_id_change(product, uom_id, qty=qty, name=name, type=type,
                              partner_id=partner_id, fposition_id=fposition_id,
                              price_unit=price_unit, currency_id=currency_id,
                              company_id=company_id)

        t_part = self.env["res.partner"]
        if partner_id and product:
            part = t_part.browse(partner_id)
            pricelist = False
            if type in ['in_invoice', 'in_refund']:
                pricelist = part.property_product_pricelist_purchase
            if type in ['out_invoice', 'out_refund']:
                pricelist = part.property_product_pricelist
            price = False
            if pricelist:
                price = pricelist.price_get(product, 1,
                                            partner_id)[pricelist.id]
                if price:
                    res['value']['price_unit'] = price

        return res


class AccountInvoiceRefund(orm.TransientModel):

    _inherit = "account.invoice.refund"


    @api.multi
    def compute_refund(self, mode='refund'):
        res = super(AccountInvoiceRefund, self).compute_refund(mode)
        new_ids = res['domain'][1][2]
        for invoice in self.env['account.invoice'].browse(new_ids):
            orig = invoice.origin_invoices_ids
            if not orig:
                continue
            invoice.payment_mode_id = orig[0].payment_mode_id
        return res
