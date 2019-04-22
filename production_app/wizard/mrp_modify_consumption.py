# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Comunitea All Rights Reserved
#    $Jesús Ventosinos Mayor <jesus@comunitea.com>$
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
from openerp import _, api, exceptions, fields, models
import openerp.addons.decimal_precision as dp


class MrpModifyConsumption(models.TransientModel):
    _inherit = 'mrp.modify.consumption'

    @api.model
    def _get_diff_qty_lot(self, app_reg, product_id):
        qty = 0.0
        lot_id = False        
        line_in = app_reg.line_in_ids.filtered(
            lambda x: x.product_id.id == product_id)
        line_out = app_reg.line_out_ids.filtered(
            lambda x: x.product_id.id == product_id)
        
        if line_in and line_out:
            qty = line_in.product_qty - line_out.product_qty
            lot_id = line_out.lot_id.id
        return qty, lot_id
    
    @api.model
    def default_get(self, fields):
        res = super(MrpModifyConsumption, self).default_get(fields)
        production_id = self._context.get('active_id', False)
        production = self.env['mrp.production'].browse(production_id)
        
        domain = [
            ('production_id', '=', production_id),
            ('state', '=', 'validated')
        ]
        app_reg = self.env['app.registry'].search(domain, limit=1)

        if app_reg and res.get('line_ids', False):
            for dic in res.get('line_ids'):
                product_id = dic['product_id']
                new_qty, new_lot_id = self._get_diff_qty_lot(app_reg, 
                                                             product_id)
                dic['product_qty'] = new_qty if new_qty else dic['product_qty']
                dic['lot_id'] = \
                    new_lot_id if new_lot_id else dic.get('lot_id', False)

        return res

