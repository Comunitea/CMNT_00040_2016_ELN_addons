# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import registry
from datetime import datetime


def parser(cr, uid, ids, data, context):
    parameters = {}
    name = ''
    model = 'stock.picking'
    data_source = 'model'
    uom_obj = registry(cr.dbname).get('product.uom')
    picking_obj = registry(cr.dbname).get('stock.picking')
    pickings = picking_obj.browse(cr, uid, ids, context)
    picking_ref_ids = {}
    picking_lines_ids = {}
    out_report_lines = pickings.compute_out_report_lines()
    for picking in pickings:
        language = picking.partner_id.lang or 'es_ES'
        picking_ref_ids[str(picking.id)] = picking.partner_id.ref or picking.partner_id.commercial_partner_id.ref or ''
        shop_id = picking.supplier_id and picking.sale_id and picking.sale_id.shop_id or False
        if shop_id:
            partner_shop_ids = picking.partner_id.shop_ref_ids.filtered(lambda r: r.shop_id.id == shop_id.id)
            picking_ref_ids[str(picking.id)] = partner_shop_ids and partner_shop_ids.ref or picking_ref_ids[str(picking.id)]
        picking_lines_ids[str(picking.id)] = []
        for line in out_report_lines[picking.id]:
            product_id = line['product_id'].with_context(lang=language)
            lot_id = line['lot_id']
            move_id = line['move_id'].with_context(lang=language)
            use_date = lot_id.use_date and datetime.strptime(lot_id.use_date[:10], "%Y-%m-%d").strftime('%d/%m/%Y') or ''
            uom_qty = line['product_qty']
            uos_qty = uom_obj._compute_qty(cr, uid, product_id.uom_id.id, uom_qty, move_id.product_uos.id)
            vals = {
                'picking_id': picking.id,
                'prod_code': product_id.default_code or '',
                'prod_ean13': product_id.ean13 or '',
                'prod_name': move_id.name or product_id.name or '',
                'lot_name': lot_id.name or '',
                'lot_date': use_date,
                'uom_qty': uom_qty,
                'uos_qty': uos_qty,
                'uom_name': product_id.uom_id.name or '',
                'uos_name': move_id.product_uos.name or product_id.uom_id.name or '',
                'price_unit': move_id.procurement_id.sale_line_id.price_unit or 0.0,
                'discount': move_id.procurement_id.sale_line_id.discount or 0.0,
                'price_subtotal': line['total'],
                'taxes': line['tax_str'],
                'valued_picking': picking.valued_picking,
            }
            picking_lines_ids[str(picking.id)].append(vals)
    parameters['picking_ref_ids'] = picking_ref_ids
    parameters['picking_lines_ids'] = picking_lines_ids
    return {
        'ids': ids,
        'name': name,
        'model': model,
        'records': [],
        'data_source': data_source,
        'parameters': parameters,
    }
