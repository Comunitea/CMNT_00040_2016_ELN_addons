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

from openerp import models, fields, api, exceptions, _
from datetime import datetime
from .maintenance_type import MAINTENANCE_TYPES


READONLY_STATES = {'confirmed': [('readonly', True)], 'cancel': [('readonly', True)]}


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Maintenance request'
    _inherit = ['mail.thread']
    _order = 'request_date desc, name desc'

    name = fields.Char('Name', size=64, required=True,
        states=READONLY_STATES,
        default=lambda self: self.env['ir.sequence'].get('maintenance.request'))
    applicant_id = fields.Many2one(
        'res.users', 'Applicant',
        required=True, select=True,
        states=READONLY_STATES,
        default=lambda self: self.env.user)
    department_id = fields.Many2one(
        'hr.department', 'Department',
        states=READONLY_STATES)
    estimated_date = fields.Datetime('Estimated date',
        states=READONLY_STATES)
    request_date = fields.Datetime('Request date',
        required=True,
        states=READONLY_STATES,
        default=fields.Datetime.now)
    symptom = fields.Text('Symptom',
        states=READONLY_STATES)
    maintenance_type_id = fields.Many2one(
        'maintenance.type', 'Maintenance type',
        states=READONLY_STATES)
    element_id = fields.Many2one(
        'maintenance.element', 'Maintenance element',
        states=READONLY_STATES)
    type = fields.Selection(MAINTENANCE_TYPES, 'Type',
        related='maintenance_type_id.type',
        readonly=True, store=True, select=True)
    maintenance_order_ids = fields.One2many(
        'maintenance.order', 'request_id', 'Maintenance order',
        readonly=True)
    note = fields.Text('Notes',
        states=READONLY_STATES)
    cancel_reason = fields.Text('Reason for cancellation',
        states=READONLY_STATES)
    survey_id = fields.Binary('Survey',
        states=READONLY_STATES)
    ttr = fields.Float('TTR',
        compute='_get_ttr', readonly=True,
        group_operator='avg',
        help='Time to repair in hours')
    tbf = fields.Float('TBF',
        compute='_get_tbf', readonly=True,
        group_operator='avg',
        help='Time between fails in hours')
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('confirmed', 'Confirmed'), 
        ('cancel', 'Cancelled'),
        ], string='State', default='draft',
        track_visibility='onchange', select=True,
        states=READONLY_STATES)
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True, readonly=True,
        default=lambda self: self.env.user.company_id)

    @api.multi
    def _get_ttr(self):
        for request in self:
            if not request.maintenance_type_id:
                request.ttr = 0.0
                continue
            if request.maintenance_type_id.type != 'corrective':
                request.ttr = 0.0
                continue
            # Time to repair (TTR)
            create_date = datetime.strptime(request.request_date, '%Y-%m-%d %H:%M:%S')
            final_date = request.maintenance_order_ids.mapped('final_date')
            date_finished = final_date and all(final_date) and datetime.strptime(max(final_date), '%Y-%m-%d %H:%M:%S')
            if date_finished and create_date:
                ttr = date_finished - create_date
                ttr = ttr and round(ttr.total_seconds() / 3600, 2) or 0.0
            else:
                ttr = 0.0
            request.ttr = ttr

    @api.multi
    def _get_tbf(self):
        for request in self:
            if not request.maintenance_type_id:
                request.tbf = 0.0
                continue
            if request.maintenance_type_id.type != 'corrective':
                request.tbf = 0.0
                continue
            # Time between fails (TBF)
            create_date = datetime.strptime(request.request_date, '%Y-%m-%d %H:%M:%S')
            domain = [
                ('maintenance_type_id.type', '=', 'corrective'),
                ('request_date', '>', request.request_date),
                ('id', '!=', request.id)
            ]
            next_maintenance = self.search(domain, order='request_date', limit=1)
            if next_maintenance:
                date_finished = datetime.strptime(next_maintenance.request_date, '%Y-%m-%d %H:%M:%S')
                if date_finished and create_date:
                    tbf = date_finished - create_date
                    tbf = tbf and round(tbf.total_seconds() / 3600, 2) or 0.0
                else:
                    tbf = 0.0
            else:
                tbf = 0.0
            request.tbf = tbf

    @api.multi    
    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = self.env['ir.sequence'].get('maintenance.request')
        return super(MaintenanceRequest, self).copy(default=default)

    @api.multi
    def cancel(self):
        for wzd in self:
            wizard_id = self.env['cancel.maintenance.request.wizard'].create({'maintenance_request_id': wzd.id})
            return {
                'name': 'Request cancel',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'cancel.maintenance.request.wizard',
                'res_id': wizard_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': self._context
            }

    @api.multi
    def confirm(self):
        self.write({'state': 'confirmed'})

    @api.multi
    def open_maintenance_order(self, order_id):
        data_pool = self.env['ir.model.data']
        if order_id:
            action_model, action_id = data_pool.get_object_reference('maintenance', 'action_maintenance_order_tree')
            action_pool = self.env[action_model]
            action = action_pool.browse(action_id).read()[0]
            action['domain'] = "[('id', '=', " + str(order_id.id) + ")]"
            return action

    @api.multi
    def create_maintenance_order(self):
        for request in self:
            vals = {
                'request_id': request.id,
                'element_id': request.element_id.id,
                'origin_department_id': request.department_id.id,
                'maintenance_type_id': request.maintenance_type_id.id,
                #'survey_id': request.survey_id,
                'symptom': request.symptom,
                'company_id': request.company_id.id,
                'request_date': request.request_date,
                'note': request.note,
            }
            order_id = self.env['maintenance.order'].create(vals)
            request.write({'state': 'confirmed'})
            if len(self) == 1:
                return self.open_maintenance_order(order_id)    

    @api.multi
    def set_to_draft(self):
        for request in self:
            mos = request.maintenance_order_ids.mapped('state')
            if 'open' in mos or 'pending' in mos or 'done' in mos:
                raise exceptions.except_orm(_('Error'),
                    _('You cannot set as draft a maintenance request with maintenance orders not in draft.'))
            else:
                request.maintenance_order_ids.unlink()
                request.write({'state': 'draft'})

    @api.multi
    def send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(self._context)
        ctx.update({
            'default_model': 'maintenance.request',
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

    @api.multi
    def unlink(self):
        if any(x.state == 'confirmed' for x in self):
            raise exceptions.except_orm(_('Error'),
                _('You cannot delete a confirmed maintenance request.'))
        return super(MaintenanceRequest, self).unlink()

