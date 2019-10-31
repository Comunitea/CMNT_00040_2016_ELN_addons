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
from openerp import models, fields, api, _
from .cost_type import COST_TYPES, DISTRIBUTION_MODES


class CostStructure(models.Model):
    _name = 'cost.structure'

    name = fields.Char('Name', size=255, required=True, default='/')
    elements = fields.One2many('cost.structure.elements', 'structure_id',
        string='Elements', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)

    @api.multi
    def _check_elements_required(self):
        for cost_str in self:
            total_type = inventory_type = False
            for e in cost_str.elements:
                if e.cost_type == 'total':
                    total_type = True
                if e.cost_type == 'inventory':
                    inventory_type = True
            return (total_type and inventory_type)

    _constraints = [
        (_check_elements_required,
        _('You must define a element with total cost type and another of inventory cost type.'),
        ['elements'])
    ]


class CostStructureElements(models.Model):
    _name = 'cost.structure.elements'
    _order = 'sequence, id'

    name = fields.Char('Name', size=255, required=True, default='/')
    sequence = fields.Integer('Sequence', required=True, default=10)
    structure_id = fields.Many2one('cost.structure', string='Structure',
        required=True, ondelete='cascade')
    cost_type_id = fields.Many2one('cost.type', string='Cost name',
        required=True)
    cost_type = fields.Selection(COST_TYPES, string='Cost type',
        related='cost_type_id.cost_type', store=False,
        readonly=True)
    cost_ratio = fields.Float('Cost ratio',
        related='cost_type_id.cost_ratio', store=False,
        readonly=True)
    distribution_mode = fields.Selection(DISTRIBUTION_MODES, string='Distribution mode',
        related='cost_type_id.distribution_mode', store=False,
        readonly=True)
    company_id = fields.Many2one('res.company', string='Company',
        related='structure_id.company_id', store=True,
        readonly=True)
