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
from openerp import pooler, _
from openerp.addons import jasper_reports
from datetime import datetime

def parser( cr, uid, ids, data, context ):
    parameters = {}
    ids = ids
    name = 'report.stock_picking_out_std_2x'
    model = 'stock.picking'
    data_source = 'model'
    pickings = pooler.get_pool(cr.dbname).get('stock.picking').browse(cr, uid, ids)
    language = pickings and pickings[0].partner_id.lang or False
    context['lang'] = language
    picking_ref_ids = {}
    for picking in pickings:
        picking_ref_ids[str(picking.id)] = picking.partner_id.ref or picking.partner_id.commercial_partner_id.ref or ''
        shop_id = picking.supplier_id and picking.sale_id and picking.sale_id.shop_id or False
        if shop_id:
            partner_shop_ids = picking.partner_id.shop_ref_ids.filtered(lambda r: r.shop_id.id == shop_id.id)
            picking_ref_ids[str(picking.id)] = partner_shop_ids and partner_shop_ids.ref or picking_ref_ids[str(picking.id)]
    parameters['picking_ref_ids'] = picking_ref_ids

    return {
        'ids': ids,
        'name': name,
        'model': model,
        'records': [],
        'data_source': data_source,
        'parameters': parameters,
    }
jasper_reports.report_jasper( 'report.stock_picking_out_std_2x', 'stock.picking', parser )
