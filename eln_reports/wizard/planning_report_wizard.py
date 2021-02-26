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


class PlanningReportWizard(models.TransientModel):
    _name = 'planning.report.wizard'
    
    delivery_route_id = fields.Many2one(
        'delivery.route', 'Delivery Route')
    group_by_route = fields.Boolean('Group By Delivery Route')
    date = fields.Date('Date')
    all_companies = fields.Boolean('Include all companies',
        default=True)
    kanban_state = fields.Selection([
        ('normal', 'Pending'),
        ('in_progress', 'In progress'),
        ('done', 'Ready to load'),
        ], string='State of readiness',
        default=False)

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = self.read()[0]
        datas = {
            'ids': self._context.get('active_ids', []),
            'model': 'planning.report.wizard',
            'form': data,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'planning_report',
            'datas': datas,
        }
