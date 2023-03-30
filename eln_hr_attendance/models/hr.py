# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'    

    user_id2 = fields.Many2one('res.users', string='Second User',
        copy=False, help='Related user name for the resource to manage its access.')
    user_id3 = fields.Many2one('res.users', string='Third User',
        copy=False, help='Related user name for the resource to manage its access.')

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
