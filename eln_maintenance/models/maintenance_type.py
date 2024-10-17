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


MAINTENANCE_TYPES = [
    ('corrective', 'Corrective'),
    ('legal', 'Legal'),
    ('preventive', 'Preventive')
]


class MaintenanceType(models.Model):
    _name = 'maintenance.type'
    _order = 'type'

    name = fields.Char('Name', size=64)
    description = fields.Text('Description')
    type = fields.Selection(MAINTENANCE_TYPES, 'Type',
        required=True)
    element_ids = fields.One2many(
        'maintenance.element.type', 'maintenance_type_id', 'Maintenance type',
        readonly=True)
    applicant_id = fields.Many2one(
        'res.users', 'Applicant',
        default=lambda self: self.env.user)
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True, readonly=True,
        default=lambda self: self.env.user.company_id)

   
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
                        _("You cannot remove maintenance type that is referenced by: %s") % (table))
        return super(MaintenanceType, self).unlink()


