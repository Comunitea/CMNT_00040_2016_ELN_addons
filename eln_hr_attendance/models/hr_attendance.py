# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    _order = 'name asc'

    @api.model
    def _get_employee(self):
        domain = [
            '|', '|',
            ('user_id', '=', self._uid),
            ('user_id2', '=', self._uid),
            ('user_id3', '=', self._uid),
        ]
        user_id = self.env['hr.employee'].search(domain)
        return user_id and user_id[0] or False

    employee_id = fields.Many2one('hr.employee', "Employee",
        required=True, select=True,
        default=_get_employee)
    name = fields.Datetime(
        default=fields.Datetime.now)
    old_name = fields.Datetime('Original Date',
        required=True, select=True,
        default=fields.Datetime.now)

    @api.onchange('name')
    def name_change(self):
        if (self.env.ref('base.group_hr_user').id not in self.env.user.groups_id.ids):
            if not self._origin and not self.old_name:
                self.old_name = self.name
            if not self._origin and self.old_name:
                self.name = self.old_name

    @api.multi
    def write(self, vals):
        if (self.env.ref('base.group_hr_user').id not in self.env.user.groups_id.ids):
            raise exceptions.Warning(
                _('Error!'),
                _("You are not authorized to make changes"))
        else:
            if 'name' in vals:
                vals['old_name'] = vals['name']
        return super(HrAttendance, self).write(vals)

    @api.multi
    def unlink(self):
        if (self.env.ref('base.group_hr_user').id not in self.env.user.groups_id.ids):
            raise exceptions.Warning(
                _('Error!'),
                _("You are not authorized to make changes"))
        res = super(HrAttendance, self).unlink()
        return res

    @api.multi
    def _altern_si_so(self):
        if (self.env.ref('base.group_hr_user').id not in self.env.user.groups_id.ids):
            return super(HrAttendance, self)._altern_si_so()
        else:
            return True

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    state2 = fields.Selection(related='state')


