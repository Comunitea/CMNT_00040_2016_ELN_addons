# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2017 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import registry
from openerp.addons import jasper_reports
from datetime import datetime


def parser(cr, uid, ids, data, context):
    parameters = {}
    name = 'report.stock_picking_out_std_2x'
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
            move_id = line['move_id']
            use_date = lot_id.use_date and datetime.strptime(lot_id.use_date[:10], "%Y-%m-%d").strftime('%d/%m/%Y') or ''
            uom_qty = line['product_qty']
            uos_qty = uom_obj._compute_qty(cr, uid, product_id.uom_id.id, uom_qty, move_id.product_uos.id)
            vals = {
                'picking_id': picking.id,
                'prod_code': product_id.default_code,
                'prod_ean13': product_id.ean13 or '',
                'prod_name': product_id.name,
                'lot_name': lot_id.name,
                'lot_date': use_date,
                'uom_qty': uom_qty,
                'uos_qty': uos_qty,
                'uom_name': product_id.uom_id.name,
                'uos_name': move_id.product_uos.name or product_id.uom_id.name,
                'price_unit': move_id.procurement_id.sale_line_id.price_unit,
                'discount': move_id.procurement_id.sale_line_id.discount,
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


jasper_reports.report_jasper('report.stock_picking_out_std_2x', 'stock.picking', parser)
