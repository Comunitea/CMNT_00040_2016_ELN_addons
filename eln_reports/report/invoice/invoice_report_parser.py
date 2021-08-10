# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import registry
from openerp.addons import jasper_reports


def parser(cr, uid, ids, data, context):
    parameters = {}
    name = 'report.invoice_report_jasper'
    model = 'account.invoice'
    data_source = 'model'
    uom_obj = registry(cr.dbname).get('product.uom')
    invoice_obj = registry(cr.dbname).get('account.invoice')
    invoice_ids = invoice_obj.browse(cr, uid, ids, context)
    language = list(set(invoice_ids.mapped('partner_id.lang')))
    if len(language) == 1:
        context['lang'] = language[0]
    invoice_lines_ids = {}
    for invoice_id in invoice_ids:
        language = invoice_id.partner_id.lang or 'es_ES'
        invoice_lines_ids[str(invoice_id.id)] = []
        for line in invoice_id.invoice_line:
            product_id = line.product_id.with_context(lang=language)
            uom_id = product_id.uom_id
            uos_id = line.uos_id.with_context(lang=language)
            uos_qty = line.quantity
            uom_qty = uom_obj._compute_qty(cr, uid, uos_id.id, uos_qty, uom_id.id)
            price_unit = line.price_unit
            if uos_id and uos_id != uom_id:
                price_unit = line.price_unit * uos_qty / uom_qty
            vals = {
                'invoice_id': invoice_id.id,
                'prod_code': product_id.default_code or '',
                'prod_ean13': product_id.ean13 or '',
                'prod_name': line.name or product_id.name or '',
                'origin': line.origin or '',
                'client_order_ref': line.stock_move_id.picking_id.client_order_ref or '',
                'uom_qty': uom_qty,
                'uos_qty': uos_qty,
                'uom_name': uom_id.name or '',
                'uos_name': uos_id.name or uom_id.name or '',
                'price_unit': price_unit or 0.0,
                'discount': line.discount or 0.0,
                'price_subtotal': line.price_subtotal,
                'taxes': line.tax_str or '',
            }
            invoice_lines_ids[str(invoice_id.id)].append(vals)
    parameters['invoice_lines_ids'] = invoice_lines_ids
    return {
        'ids': ids,
        'name': name,
        'model': model,
        'records': [],
        'data_source': data_source,
        'parameters': parameters,
    }


jasper_reports.report_jasper('report.invoice_report_jasper', 'account.invoice', parser)
