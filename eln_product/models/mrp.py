# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
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
from openerp import models, fields, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_qty_percent = fields.Integer(string='Qty(%)',
        compute='_get_product_qty_percent', readonly=True)

    @api.multi
    def _get_product_qty_percent(self):
        qty_total = sum(line.product_qty for line in self)
        if qty_total == 0:
            for line in self:
                line.product_qty_percent = 0
        else:
            qty_percent_acc = 0
            line_ids = self.sorted(key=lambda r: r.product_qty, reverse=True)
            for line in line_ids[1:]:
                qty_percent = int(round((line.product_qty * 100) / qty_total))
                qty_percent_acc += qty_percent
                line.product_qty_percent = qty_percent
            line_ids[0].product_qty_percent = 100 - qty_percent_acc

