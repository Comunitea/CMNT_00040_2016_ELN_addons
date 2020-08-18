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

from openerp import models, fields, api, exceptions
from .maintenance_type import MAINTENANCE_TYPES
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule


class MaintenanceElement(models.Model):
    _name = 'maintenance.element'
    _order = 'complete_name'
    _rec_name = 'complete_name'
    _constraints = [
        (models.Model._check_recursion, 'Error ! You cannot create recursive elements.', ['parent_id'])
    ]

    name = fields.Char('Name', size=64,
        required=True, select=True)
    description = fields.Text('Description')
    type = fields.Selection([
        ('linea', 'Line'), 
        ('facility', 'Facility'), 
        ('equipment', 'Equipment'), 
        ], string='Type')
    parent_id = fields.Many2one(
        'maintenance.element', 'Parent element')
    child_ids = fields.One2many(
        'maintenance.element', 'parent_id', 'Child elements')
    complete_name = fields.Char('Complete name', size=256,
        compute='_get_complete_name',
        select=True, store=True)
    code = fields.Char('Code', size=64,
        select=True)
    maintenance_type_ids = fields.One2many(
        'maintenance.element.type', 'element_id', 'Maintenance type')
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True, readonly=True,
        default=lambda self: self.env.user.company_id)

    @api.multi
    @api.depends('name', 'parent_id')
    def _get_complete_name(self):
        for element in self:
            child_ids = element.child_ids
            while child_ids:
                next_level_ids = self.env['maintenance.element']
                for child_id in child_ids:
                    if child_id not in self:
                        next_level_ids |= child_id.child_ids
                        child_id.write({'complete_name': child_id._complete_name()})
                child_ids = next_level_ids
            element.complete_name = element._complete_name()

    @api.multi
    def _complete_name(self):
        self.ensure_one()
        names = [self.name or '']
        parent = self.parent_id
        while parent:
            names.append(parent.name or '')
            parent = parent.parent_id
        return u' / '.join(reversed(names))

    @api.multi
    def unlink(self):
        element_ids = self._ids
        if element_ids:
            sql = """
                SELECT cl1.relname as table, att1.attname as column
                FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                    pg_attribute as att1, pg_attribute as att2
                WHERE con.conrelid = cl1.oid
                    AND con.confrelid = cl2.oid
                    AND array_lower(con.conkey, 1) = 1
                    AND con.conkey[1] = att1.attnum
                    AND att1.attrelid = cl1.oid
                    AND cl2.relname = %s
                    AND att2.attname = 'id'
                    AND array_lower(con.confkey, 1) = 1
                    AND con.confkey[1] = att2.attnum
                    AND att2.attrelid = cl2.oid
                    AND con.contype = 'f'
                    AND con.confdeltype <> 'c'
            """
            self._cr.execute(sql, [self._table])
            records = self._cr.fetchall()
            for record in records:
                table = record[0]
                column = record[1]
                sql = """SELECT EXISTS(SELECT 1 FROM "%s" WHERE %s in %%s LIMIT 1)""" % (table, column)
                self._cr.execute(sql, [element_ids])
                exist_record = self._cr.fetchall()
                if exist_record[0][0]:
                    raise exceptions.Warning(
                        _("You cannot remove maintenance element that is referenced by: %s") % (table))
        return super(MaintenanceElement, self).unlink()


class MaintenanceElementType(models.Model):
    _name = 'maintenance.element.type'
    _rec_name = 'maintenance_type_id'
    _order = 'last_run'

    element_id = fields.Many2one(
        'maintenance.element', 'Maintenance element',
        required=True,
        ondelete='cascade')
    maintenance_type_id = fields.Many2one(
        'maintenance.type', 'Maintenance type',
        required=True)
    type = fields.Selection(MAINTENANCE_TYPES, 'Type',
        related='maintenance_type_id.type',
        readonly=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High')
        ], string='Priority',
        default='0')
    survey_id = fields.Binary('Survey')
    planned = fields.Boolean('Planned')
    frequency = fields.Selection([
        ('3', 'Daily'),
        ('2', 'Weekly'),
        ('1', 'Monthly'),
        ('0', 'Yearly'),
        ], string='Frequency')
    interval = fields.Integer('Interval', default=1)
    initial_date = fields.Date('Initial date')
    last_run = fields.Date('Last run')
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('Saturday', default=True)
    sunday = fields.Boolean('Sunday', default=True)
    applicant_id = fields.Many2one(
        'res.users', 'Applicant',
        default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company', 'Company',
        related='element_id.company_id',
        readonly=True, store=True)

    @api.model
    def run_scheduler(self):
        element_type_ids = self.search([('planned', '=', True)])
        week_days = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6,
        }
        for type_id in element_type_ids:
            if not type_id.frequency:
                continue
            last_run = datetime.strptime(max(type_id.last_run, type_id.initial_date), "%Y-%m-%d") 
            end_date = (datetime.now() + relativedelta(months=+1)) - relativedelta(days=-1)
            excluded_dates = []
            for week_day in week_days.keys():
                if type_id[week_day]:
                    excluded_dates += (rrule(
                        freq=3, # Daily
                        byweekday=week_days[week_day],
                        wkst=0,
                        dtstart=last_run,
                        interval=1)
                        .between(last_run, end_date, inc=True)
                    )
            all_dates = (rrule(
                freq=int(type_id.frequency),
                wkst=0,
                dtstart=last_run,
                interval=type_id.interval or 1)
                .between(last_run, end_date, inc=True)
            )
            if all_dates:
                for date in all_dates:
                    create_request = True
                    if date in excluded_dates:
                        new_date = date
                        new_date_flag = False
                        while not new_date_flag:
                            new_date = new_date + relativedelta(days=+1)
                            if new_date in all_dates or new_date > end_date:
                                create_request = False
                                break
                            if new_date not in excluded_dates:
                                date = new_date
                                new_date_flag = True
                    if create_request and type_id.element_id:
                        last_run = date
                        vals = {
                            'maintenance_type_id': type_id.id,
                            'element_id': type_id.element_id.id,
                            'request_date': date,
                            'company_id': type_id.company_id.id,
                        }
                        if type_id.applicant_id:
                            vals = dict(vals, applicant_id=type_id.applicant_id.id)
                        if type_id.survey_id:
                            vals = dict(vals, survey_id=type_id.survey_id)
                        self.env['maintenance.request'].with_context(force_company=type_id.company_id.id).create(vals)
                type_id.write({'last_run': last_run})
        return True

