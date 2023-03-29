# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, exceptions, _


class HrAttendanceReport(models.AbstractModel):
    _inherit = 'report.hr_attendance_report.print_attendance'

    @api.multi
    def render_html(self, data=None):
        if (self.env.ref('base.group_hr_user').id not in self.env.user.groups_id.ids):
            domain = [
                '|', '|',
                ('user_id', '=', self._uid),
                ('user_id2', '=', self._uid),
                ('user_id3', '=', self._uid),
            ]
            user_id = self.env['hr.employee'].search(domain)
            user_id = user_id and user_id[0] or False
            if user_id and user_id.id in data['ids']:
                data['ids'] = [user_id.id]
            else:
                raise exceptions.Warning(
                    _('Error!'),
                    _("You are not authorized to print this data"))
        return super(HrAttendanceReport, self).render_html(data)
