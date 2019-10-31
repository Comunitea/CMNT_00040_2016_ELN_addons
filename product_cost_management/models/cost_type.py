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
from openerp import models, fields


COST_TYPES = [
    ('total', 'Total'),
    ('bom', 'BoM'),
    ('standard_price', 'Cost price'),
    ('ratio', 'Ratio'),
    ('inventory', 'Inventory')
]

DISTRIBUTION_MODES = [
    ('eur', 'By amounting'),
    ('units', 'By units'),
    ('kg', 'By weight net (kg)'),
    ('min', 'By minutes')
]


class CostType(models.Model):
    _name = 'cost.type'

    name = fields.Char('Cost name', size=255, required=True)
    cost_type = fields.Selection(COST_TYPES, string='Cost type',
        required=True, default='total',
        help="This option is used to define how the cost is calculated.\n" \
        "The 'Total' value means that the cost is a totalizing of the preceding lines in the structure sequence.\n" \
        "The 'BoM' value means that the cost is calculated from the product BoM.\n" \
        "The 'Cost price' value means that the cost is the cost price that currently has the product.\n" \
        "The 'Ratio' value means that the cost is calculated based on a ratio.\n" \
        "The 'Inventory' value means that the cost is as total and when update product cost it will be used as the 'Cost price'.")
    cost_ratio = fields.Float('Cost ratio')
    distribution_mode = fields.Selection(DISTRIBUTION_MODES, string='Distribution mode')
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
