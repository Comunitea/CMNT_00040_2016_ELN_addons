# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from openerp.osv import expression
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule


class DeliveryRoute(models.Model):
    _name = 'delivery.route'
    _description = 'Delivery route'
    _order = 'sequence'

    code = fields.Char('Code', size=32)
    name = fields.Char('Name', size=255)
    sequence = fields.Integer('Sequence', default=1)
    carrier_id = fields.Many2one('res.partner', 'Carrier')
    delivery_delay = fields.Float('Delivery Lead Time', required=True,
        help="The average delay in days between the picking transfer and the delivery of the products to customer.")
    show_always = fields.Boolean('Show always')
    next_loading_date = fields.Date(
        string='Next loading date',
        compute='_get_next_loading_date',
        help="Next date on which a delivery order will be loaded.")
    planned = fields.Boolean('Planned')
    interval = fields.Integer('Interval', default=1)
    initial_date = fields.Date('Initial date')
    monday = fields.Boolean('Monday')
    tuesday = fields.Boolean('Tuesday')
    wednesday = fields.Boolean('Wednesday')
    thursday = fields.Boolean('Thursday')
    friday = fields.Boolean('Friday')
    saturday = fields.Boolean('Saturday')
    sunday = fields.Boolean('Sunday')

    @api.multi
    def _get_next_loading_date(self):
        week_days = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6,
        }
        today = datetime.strptime(fields.Date.context_today(self), "%Y-%m-%d")
        for route_id in self:
            if not route_id.planned:
                route_id.next_loading_date = False
                continue
            if route_id.interval < 1:
                route_id.next_loading_date = fields.Date.context_today(self)
                continue
            initial_date = datetime.strptime(route_id.initial_date, "%Y-%m-%d") 
            end_date = (today + relativedelta(months=route_id.interval))
            valid_dates = []
            for week_day in week_days.keys():
                if route_id[week_day]:
                    valid_dates += (rrule(
                        freq=int(2), # Weekly
                        byweekday=week_days[week_day],
                        wkst=0,
                        dtstart=initial_date,
                        until=end_date,
                        interval=route_id.interval or 1)
                        .between(today, end_date, inc=True)
                    )
            valid_dates.sort()
            route_id.next_loading_date = valid_dates and valid_dates[0] or today

    @api.multi
    def name_get(self):
        return [
            (route.id, (route.code and
            (route.code + ' - ') or '') + route.name)
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
                        _("You cannot remove a delivery route that is referenced by: %s") % (table))
        return super(DeliveryRoute, self).unlink()
