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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _


class MaintenaceStop(orm.Model):

    _name = "maintenance.stop"

    _columns = {
        'name': fields.char('Name', size=250, required=True),
        'description': fields.text('Description'),
        'maintenanance_element_ids': fields.many2many('maintenance.element', 'maintenance_stop_element_rel', 'stop_id', 'element_id', 'Elements'),
        'date': fields.date('Stop date', required=True),
        'state': fields.selection([('draft', 'Draft'),('open', 'Open'),('done', 'Done'),('cancel','Cancelled')], 'State', required=True),
        'intervention_request_ids': fields.one2many('intervention.request', 'stop_id', 'Intervention requests')
    }

    _defaults = {
        'state': 'draft'
    }

    def act_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def act_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    def act_compute(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        stop_obj = self.browse(cr, uid, ids[0])
        min_date_to_planify = (datetime.strptime(stop_obj.date, "%Y-%m-%d") + relativedelta(years=-1)).strftime("%Y-%m-%d")
        maintenace_type_ids = set()
        for element in stop_obj.maintenanance_element_ids:
            for maintype in element.maintenance_type_ids:
                maintenace_type_ids.add(maintype.id)

        maintenance_type_obj = self.pool.get('maintenance.type')
        type_ids = maintenance_type_obj.search(cr, uid, [('on_stop', '=', True),('id', 'in', list(maintenace_type_ids)),'|',('ultima_ejecucion', '<', stop_obj.date),('ultima_ejecucion', '=', False)])
        for type_obj in maintenance_type_obj.browse(cr, uid, type_ids, context):
            if type_obj.ultima_ejecucion >= min_date_to_planify:
                element_ids = maintenace_type_ids.intersection(set([x.id for x in type_obj.element_ids]))
                args_request = {
                                'maintenance_type_id': type_obj.id,
                                'element_ids': [(6, 0, list(element_ids))],
                                'fecha_solicitud': stop_obj.date,
                                'department_id': type_obj.department_id and type_obj.department_id.id or False,
                                'executor_department_id': type_obj.department_id and type_obj.department_id.id or False,
                                'stop_id': stop_obj.id
                                }
                self.pool.get('intervention.request').create(cr, uid, args_request, context)

                maintenance_type_obj.write(cr, uid, type_obj.id, {'ultima_ejecucion': stop_obj.date})
        return True

    def act_update_requests(self, cr, uid, ids, context=None):
        for stop_obj in self.browse(cr, uid, ids):
            to_update_request_ids = []
            to_update_maintype_ids = set()
            for request in stop_obj.intervention_request_ids:
                if request.state == "draft":
                    to_update_request_ids.append(request.id)
                    to_update_maintype_ids.add(request.maintenance_type_id.id)

            if to_update_request_ids:
                self.pool.get('intervention.request').write(cr, uid, to_update_request_ids, {'fecha_solicitud': stop_obj.date})
            if to_update_maintype_ids:
                self.pool.get('maintenance.type').write(cr, uid, to_update_maintype_ids, {'ultima_ejecucion': stop_obj.date})

        return True

    def act_cancel(self, cr, uid, ids, context=None):
        for stop_obj in self.browse(cr, uid, ids):
            for request in stop_obj.intervention_request_ids:
                vals = {'stop_id': False}
                if request.state == "draft":
                    vals.update({'state': "cancelled"})
                    request.act_cancel()
                request.write(vals)

        return self.write(cr, uid, ids, {'state': 'cancel'})

    def unlink(self, cr, uid, ids, context=None):
        for stop_obj in self.browse(cr, uid, ids):
            if stop_obj.state != "draft":
                raise orm.except_orm(_('Error !'),_("Only can delete stops in draft state."))
        return super(MaintenaceStop, self).unlink(cr, uid, ids, context=context)
