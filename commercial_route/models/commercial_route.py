# -*- coding: utf-8 -*-
# Copyright 2021 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _
from openerp.osv import expression


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
                        _("You cannot remove a commercial route that is referenced by: %s") % (table))
        return super(CommercialRoute, self).unlink()
