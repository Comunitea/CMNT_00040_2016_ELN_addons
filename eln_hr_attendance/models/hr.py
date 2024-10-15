# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from datetime import datetime, timedelta
import time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'    

    user_id2 = fields.Many2one('res.users', string='Second User',
        copy=False, help='Related user name for the resource to manage its access.')
    user_id3 = fields.Many2one('res.users', string='Third User',
        copy=False, help='Related user name for the resource to manage its access.')
    state2 = fields.Selection(related='state')

    @api.multi
    def _check_user_ids(self):
        for employee in self:
            employees = self.sudo().search([('id', '!=', employee.id)])
            all_user_ids = employees.mapped('user_id.id') + employees.mapped('user_id2.id') + employees.mapped('user_id3.id')
            if employee.user_id.id in all_user_ids:
                return False
            if employee.user_id2.id in all_user_ids:
                return False
            if employee.user_id3.id in all_user_ids:
                return False
        return True

    _constraints = [
        (_check_user_ids, 'An user can only be assigned to one employee.', ['user_id', 'user_id2', 'user_id3'])
    ]

    @api.multi
    def attendance_action_change(self):
        action_date = self._context.get('action_date', False)
        action = self._context.get('action', False)
        hr_attendance = self.env['hr.attendance']
        if action_date and action:
            return super(HrEmployee, self).attendance_action_change()
        if not action_date:
            action_date = time.strftime('%Y-%m-%d %H:%M:%S')
        for employee in self:
            domain = [
                ('employee_id', '=', employee.id), 
                ('action', 'in', ('sign_in', 'sign_out'))
            ]
            last_atts = hr_attendance.search(domain, limit=1, order='name DESC')
            if last_atts:
                last_action = last_atts[0].action
                last_name = last_atts[0].name
                if last_action == 'sign_in' and last_name[:10] < action_date[:10]:
                    action_reason = self.env['ir.model.data'].get_object_reference('hr_attendance', 'hr_action_reason_to_review')
                    new_last_name = (datetime.strptime(last_name, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
                    default = {
                        'name': new_last_name,
                        'action': 'sign_out',
                        'action_desc': action_reason and action_reason[1] or False,
                    }
                    last_atts[0].copy(default=default)
                    res = super(HrEmployee, employee.sudo()).attendance_action_change()
                else:
                    res = super(HrEmployee, employee).attendance_action_change()
            else:
                res = super(HrEmployee, employee).attendance_action_change()
            return res
