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

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_journal(self):
        if self._context.get('no_journal', False):
            return False
        return super(AccountInvoice, self)._default_journal()

    @api.model
    def _default_currency(self):
        if self._context.get('no_journal', False):
            return self.env.user.company_id.currency_id
        return super(AccountInvoice, self)._default_currency()

    journal_id = fields.Many2one(
        string='Journal',
        comodel_name='account.journal',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale_refund'], 'in_refund': ['purchase_refund'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]",
        default=_default_journal)
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='always',
        default=_default_currency)
    origin_invoices_ids = fields.Many2many(copy=False)
    refund_invoice_ids = fields.Many2many(copy=False)

    @api.multi
    def onchange_company_id(self, company_id, part_id, type, invoice_line, currency_id):
        res = super(AccountInvoice, self).onchange_company_id(company_id, part_id, type, invoice_line, currency_id)
        if self._context.get('no_journal', False) and res.get('value', {}).get('journal_id', False):
            res['value']['journal_id'] = False
        return res

    @api.multi
    def _get_cost_subtotal(self):
        product_tmpl_obj = self.env['product.template']
        t_uom = self.env['product.uom']
        invoices = self.filtered(
            lambda r: r.type in ('out_invoice', 'out_refund'))
        for invoice in invoices:
            picking_ids = invoice.mapped('picking_ids')
            if invoice.type  == 'out_refund':
                picking_ids |= invoice.origin_invoices_ids.mapped('picking_ids')
            move_lines = picking_ids.mapped('move_lines')
            for line in invoice.invoice_line:
                price_unit = quant_qty = 0.0
                if move_lines and line.product_id.type != 'service':
                    for move_line in move_lines.filtered(lambda r: r.product_id == line.product_id):
                        for quant in move_line.quant_ids.filtered(lambda r: r.qty > 0):
                            price_unit += quant.cost * quant.qty
                            quant_qty += quant.qty
                if quant_qty:
                    price_unit = price_unit / quant_qty
                if not price_unit:
                    date = invoice.date_invoice or fields.Date.context_today(self)
                    price_unit = product_tmpl_obj.get_history_price(
                        line.product_id.product_tmpl_id.id, line.company_id.id, date=date)
                price_unit = price_unit or line.with_context(force_company=line.company_id.id).product_id.standard_price
                from_unit = line.uos_id.id
                to_unit = line.product_id.uom_id.id
                uom_qty = line.quantity
                if from_unit != to_unit:
                    uom_qty = t_uom._compute_qty(from_unit, line.quantity, to_unit)
                sign = -1 if line.price_subtotal < 0 else 1
                cost_subtotal = invoice.currency_id.round(abs(price_unit * uom_qty) * sign)
                line.cost_subtotal = cost_subtotal

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        invoices = self.filtered(
            lambda r: r.type in ('out_invoice', 'out_refund'))
        invoices._get_cost_subtotal()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        if 'picking_ids' in vals or 'origin_invoices_ids' in vals:
            invoices = self.filtered(
                lambda r: r.type in ('out_invoice', 'out_refund'))
            invoices._get_cost_subtotal()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    uom_qty = fields.Float('Uom Qty', compute='_get_uom_qty')
    cost_subtotal = fields.Float('Cost Subtotal')
    origin_line_ids = fields.Many2many(copy=False)
    refund_line_ids = fields.Many2many(copy=False)

    @api.one
    @api.depends('quantity')
    def _get_uom_qty(self):
        if self.quantity:
            uom_qty = self.env['product.uom']._compute_qty(
               self.uos_id.id, self.quantity, self.product_id.uom_id.id)
            self.uom_qty = uom_qty

    @api.multi
    def uos_id_change(self, product, uom, qty=0, name='', type='out_invoice', partner_id=False,
            fposition_id=False, price_unit=False, currency_id=False, company_id=None):
        """
        Modificamos para no permitir poner cualquier tipo de unidad en la linea de factura.
        Ahora solo aceptará alguna que pertenezca a la misma categoria que la unidad de medida por defecto del producto.
        """
        update_res = False

        if product and uom:
            prod = self.env['product.product'].browse(product)
            prod_uom = self.env['product.uom'].browse(uom)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                update_res = True
                uom = prod.uos_id.id or prod.uom_id.id or False

        res = super(AccountInvoiceLine, self).uos_id_change(
            product, uom, qty=qty, name=name, type=type, partner_id=partner_id,
            fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, company_id=company_id)

        if update_res:
            res['value']['uos_id'] = uom or False

        return res

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id,
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
                price = pricelist.price_get(
                    product, 1, partner_id)[pricelist.id]
                if price:
                    res['value']['price_unit'] = price

        return res


class AccountInvoiceRefund(models.TransientModel):
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
