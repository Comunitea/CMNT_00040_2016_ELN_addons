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
from openerp.osv import orm, fields

class hr_employee(orm.Model):
    def _get_categories(self, cr , uid, ids, field_name, args=None, context=None):
        result = {}
        employees = self.pool.get('hr.employee').browse(cr, uid, ids, context)
        for employee in employees:
            result[employee.id]=""
            for category in employee.category_ids:
                result[employee.id]+=category.name+","
            result[employee.id]=result[employee.id][:-1]
        return result

    _inherit = 'hr.employee'
    _columns = {
            'producto_hora_nocturna_id':fields.many2one('product.product', 'product night hour', required=False),
            'producto_hora_festiva_id':fields.many2one('product.product', 'product festive hour', required=False),
            'externo':fields.boolean('External employee', required=False),
            'categories':fields.function(_get_categories, method=True, type='char', string='Categories', store=False),
                    }
