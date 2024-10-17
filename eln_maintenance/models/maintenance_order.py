# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2014 Pexego Sistemas Informáticos All Rights Reserved
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
#############################################################################
from odoo import models, fields, api, exceptions, _
from datetime import datetime


READONLY_STATES = {'done': [('readonly', True)], 'cancel': [('readonly', True)]}


class MaintenanceOrder(models.Model):
    _name = 'maintenance.order'
    _description = 'Maintenance order'
    _inherit = ['mail.thread']
    _order = 'request_date desc, name desc'

    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True, readonly=True,
        default=lambda self: self.env.user.company_id)
    name = fields.Char('Name', size=64, required=True,
        states=READONLY_STATES,
        default=lambda self: self.env['ir.sequence'].get('maintenance.order'))
    request_id = fields.Many2one(
        'maintenance.request', 'Maintenance request',
        states=READONLY_STATES)
    element_id = fields.Many2one(
        'maintenance.element', 'Maintenance element',
        states=READONLY_STATES)
    request_date = fields.Datetime('Request date',
        default=fields.Datetime.now,
        states=READONLY_STATES)
    assigned_department_id = fields.Many2one(
        'hr.department', 'Assigned department',
        select=True,
        states=READONLY_STATES)
    origin_department_id = fields.Many2one(
        'hr.department', 'Origin department',
        states=READONLY_STATES)
    hour_ids = fields.One2many(
        'maintenance.order.time.report', 'maintenance_order_id', 'Timesheet',
        states=READONLY_STATES)
    stop_type = fields.Selection([
        ('running', 'Running'), 
        ('stop', 'Stop'), 
        ], string='Stop type',
        states=READONLY_STATES)
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('open', 'Started'), 
        ('pending', 'Pending approval'), 
        ('done', 'Done'), 
        ('cancel', 'Cancelled'),
        ], string='State', default='draft',
        track_visibility='onchange',
        select=True,
        states=READONLY_STATES)
    maintenance_type_id = fields.Many2one(
        'maintenance.type', 'Maintenance type',
        select=True,
        states=READONLY_STATES)
    survey_id = fields.Binary('Survey',
        related='request_id.survey_id',
        readonly=True)
    initial_date = fields.Datetime('Initial date',
        states=READONLY_STATES)
    final_date = fields.Datetime('Final date',
        states=READONLY_STATES)
    manager_id = fields.Many2one(
        'res.users', 'Manager',
        select=True,
        states=READONLY_STATES)
    approved_by = fields.Many2one(
        'res.users', 'Revised and approved suitability by',
        readonly=True)
    approved_date = fields.Datetime('Revised and approved date',
        readonly=True)
    note = fields.Text('Notes',
        states=READONLY_STATES)
    parent_id = fields.Many2one(
        'maintenance.order', 'Parent order',
        states=READONLY_STATES)
    child_ids = fields.One2many(
        'maintenance.order', 'parent_id', 'Child orders',
        states=READONLY_STATES)
    symptom = fields.Text('Symptom',
        states=READONLY_STATES)

   
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({
            'name': self.env['ir.sequence'].get('maintenance.order'),
            'hour_ids': None,
            'child_ids': None
        })
        return super(MaintenanceOrder, self).copy(default=default)

   
    def request_validation(self):
        for order in self:
            final_date = order.final_date or datetime.today()
            vals = {
                'state': 'pending',
                'final_date': final_date
            }
            order.write(vals)
        return True

   
    def maintenance_order_cancel(self):
        for order in self:
            order.write({'state': 'cancel'})
        return True

   
    def maintenance_order_open(self):
        for order in self:
            initial_date = order.initial_date or datetime.today()
            vals = {
                'state': 'open',
                'initial_date': initial_date,
                'final_date': False
            }
            order.write(vals)
        return True

   
    def maintenance_order_done(self):
        for order in self:
            final_date = order.final_date or datetime.today()
            vals = {
                'state': 'done',
                'final_date': final_date
            }
            if not order.approved_by:
                vals = dict(vals, approved_by=self.env.user.id)
            if not order.approved_date:
                vals = dict(vals, approved_date=datetime.today())
            order.write(vals)
        return True

   
    def request_validation_to_open(self):
        for order in self:
            vals = {
                'state': 'open',
                'final_date': False
            }
            order.write(vals)
        return True

   
    def maintenance_order_set_to_draft(self):
        for order in self:
            vals = {
                'state': 'draft',
                'initial_date': False,
                'approved_by': False,
                'approved_date': False
            }
            order.write(vals)
        return True

   
    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('maintenance', 'email_template_maintenance_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self._context)
        ctx.update({
            'default_model': 'maintenance.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

   
    def unlink(self):
        if any(x.state == 'done' for x in self):
            raise exceptions.except_orm(_('Error'),
                _('You cannot delete a done maintenance order.'))
        return super(MaintenanceOrder, self).unlink()


class MaintenanceOrderTimeReport(models.Model):
    _name = "maintenance.order.time.report"

    @api.model
    def _get_employee(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return employee_id and employee_id.id

    date = fields.Date('Date',
        default=fields.Datetime.now)
    start_time = fields.Float('Start time')
    end_time = fields.Float('End time')
    employee_id = fields.Many2one(
        'hr.employee', 'Employee',
        required=True,
        default=_get_employee)
    maintenance_order_id = fields.Many2one(
        'maintenance.order', 'Maintenance order', ondelete='cascade')
    total = fields.Float('Total',
        compute='_get_total', readonly=True)

   
    def _get_total(self):
        for r in self:
            r.total = abs(r.end_time - r.start_time)

