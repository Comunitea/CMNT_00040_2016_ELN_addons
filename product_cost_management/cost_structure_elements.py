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
from osv import osv, fields

COST_THEORIC_TYPES = [('none', 'None'),
                      ('ldm', 'LdM'),
                      ('analytic_account', 'Analytic Account')]
COST_REAL_TYPES = [('none', 'None'),
                   ('ldm', 'LdM'),
                   ('analytic_account', 'Analytic Account'),
                   ('based_productions', 'Based on Production Orders')]
FIELD_THEORIC_COST = [('fixed_price', 'Fixed Price'),
                      ('theoric_cost', 'Theoric cost')]
FIELD_REAL_COST = [('fixed_price', 'Fixed Price'),
                   ('pmp', 'PMP')]
TIME = [('current_year', 'Current Year'),
        ('last_twelve_months', 'Last 12 months')]


class cost_structure(osv.osv):
    _name = 'cost.structure'
    _description = ''
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'elements': fields.one2many('cost.structure.elements',
                                    'structure_id',
                                    'Elements',
                                    required=True)
    }
    _defaults = {
        'name': '/',
    }
cost_structure()


class cost_structure_elements(osv.osv):
    _name = 'cost.structure.elements'
    _description = ''
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'sequence': fields.integer('Sequence', required=True),
        'structure_id': fields.many2one('cost.structure',
                                        'Structure',
                                        required=True),
        'cost_type_id': fields.many2one('cost.type',
                                        'Cost Type',
                                        required=True),
        'cost_theoric_type': fields.selection(COST_THEORIC_TYPES,
                                              'Cost theoric types',
                                              required=True),
        'field_theoric_cost': fields.selection(FIELD_THEORIC_COST,
                                               'Field theoric cost'),
        'fixed_theoric_cost': fields.float('Fixed theoric cost'),
        'cost_real_type': fields.selection(COST_REAL_TYPES,
                                           string='Cost real types',
                                           required=True),
        'field_real_cost': fields.selection(FIELD_REAL_COST,
                                            'Field real cost'),
        'fixed_real_cost': fields.float('Fixed real cost'),
        'time': fields.selection(TIME,
                                 string="Time",
                                 required=True)
    }
    _defaults = {
        'name': '/',
        'sequence': 1
    }
cost_structure_elements()
