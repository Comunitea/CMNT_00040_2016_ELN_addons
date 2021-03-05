# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from openerp.osv import expression
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule


class CommercialRoute(models.Model):
    _name = 'commercial.route'
    _description = 'Commercial route'
    _order = 'user_id, sequence, code'

    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code', size=32)
    name = fields.Char('Name', size=255)
    user_id = fields.Many2one('res.users', 'Salesperson')
    sequence = fields.Integer('Sequence', default=1)
    partner_ids = fields.One2many(
        'res.partner', 'commercial_route_id', 'Partners',
        readonly=True)
    planned = fields.Boolean('Planned')
    interval = fields.Integer('Interval', default=1)
    initial_date_from = fields.Date('Initial date (from)')
    initial_date_to = fields.Date('Initial date (to)')
    next_date_from = fields.Date(
        string='Next visit date (from)',
        compute='_get_next_date', store=True)
    next_date_to = fields.Date(
        string='Next visit date (to)',
        compute='_get_next_date', store=True)
    duration = fields.Integer('Duration', # For gantt view
        compute='_get_next_date', store=True)

    @api.multi
    @api.depends('initial_date_from', 'initial_date_to', 'planned', 'interval')
    def _get_next_date(self):
        today = datetime.strptime(fields.Date.context_today(self), "%Y-%m-%d")
        for route_id in self:
            if not route_id.planned:
                route_id.next_date_from = False
                route_id.next_date_to = False
                continue
            if route_id.interval < 1:
                route_id.next_date_from = fields.Date.context_today(self)
                route_id.next_date_to = fields.Date.context_today(self)
                continue
            if not route_id.initial_date_from or not route_id.initial_date_to:
                route_id.next_date_from = False
                route_id.next_date_to = False
                continue
            initial_date_from = datetime.strptime(min(route_id.initial_date_from, route_id.initial_date_to), "%Y-%m-%d")
            initial_date_to = datetime.strptime(max(route_id.initial_date_from, route_id.initial_date_to), "%Y-%m-%d")
            end_date = today + relativedelta(weeks=route_id.interval)
            valid_dates_to = (rrule(
                freq=2, # Weekly
                dtstart=initial_date_to,
                until=end_date,
                interval=route_id.interval or 1)
                .between(today, end_date, inc=True)
            )
            next_date_to = valid_dates_to and valid_dates_to[0] or today
            next_date_from = next_date_to  - (initial_date_to - initial_date_from)
            route_id.next_date_from = next_date_from
            route_id.next_date_to = next_date_to
            route_id.duration = ((next_date_to - next_date_from).days + 1) * 8

    @api.multi
    def name_get(self):
        return [
            (route.id, (route.code and
            (route.code + ' - ') or '') + (route.name or ''))
            for route in self
        ]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = [
            '&' if operator in expression.NEGATIVE_TERM_OPERATORS else '|',
            ('code', operator, name),
            ('name', operator, name),
        ]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    @api.multi
    def unlink(self):
        type_ids = self._ids
        if type_ids:
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
                self._cr.execute(sql, [type_ids])
                exist_record = self._cr.fetchall()
                if exist_record[0][0]:
                    raise exceptions.Warning(
                        _("You cannot remove a commercial route that is referenced by: %s") % (table))
        return super(CommercialRoute, self).unlink()

    @api.multi
    def update_commercial_route_dates(self):
        #route_ids = self or self.search([])
        route_ids = self.search([])
        for route_id in route_ids:
            route_id._get_next_date()
        return True
