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


class intervention_request(orm.Model):
    _name = "intervention.request"
    _inherit = ['mail.thread']
    _columns = {
            'company_id': fields.many2one('res.company','Company',required=True,select=1, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)]}),
            'maintenance_type_id':fields.many2one('maintenance.type', 'maintenance type', required=False, states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'name':fields.char('Nombre', size=64, readonly=True, required=False),
            'solicitante_id':fields.many2one('res.users', 'Applicant ', required=True, states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'element_ids':fields.many2many('maintenance.element', 'maintenanceelement_interventionrequest_rel', 'intervention_id', 'element_id', 'Maintenance elements', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'department_id':fields.many2one('hr.department', 'Department', required=False, states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'executor_department_id': fields.many2one('hr.department', 'Executor department', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'fecha_estimada': fields.date('Estimated date', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'motivo_cancelacion' : fields.text('Reason for cancellation', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'fecha_solicitud': fields.date('Request date', required=True, states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'instrucciones': fields.text('Instructions', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'state':fields.selection([
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),
                ('cancelled', 'Cancelled'),
                 ], 'State', select=True, readonly=False),
            'note': fields.text('Notes', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'deteccion':fields.text('Detection', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'sintoma':fields.text('Sign', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'efecto':fields.text('effect', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'stop_id': fields.many2one('maintenance.stop', 'Stop', states={'confirmed': [('readonly', True)], 'cancelled': [('readonly', True)]})
    }
    _defaults = {
        'state': 'draft',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'intervention.request'),
        'fecha_solicitud':fields.date.context_today,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'intervention.request', context=c),
        'solicitante_id': lambda obj, cr, uid, context: uid,
        }
    _order = "fecha_solicitud asc"

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'intervention.request'),
        })
        return super(intervention_request, self).copy(cr, uid, id, default, context)

    def cancel(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if not ids:
            return False
        wizard_id = self.pool.get('cancel.intervention.request.wizard').create(cr, uid, {'intervention_request_id':ids[0]}, context)
        return {
            'name':"Cancelar solicitud",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'cancel.intervention.request.wizard',
            'res_id':wizard_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }

    def act_cancel(self, cr, uid, ids, context=None):
        for request in self.browse(cr, uid, ids, context=context):
            if request.maintenance_type_id:
                future_request_ids = self.search(cr, uid, [('state', 'in', ['confirmed','draft']),('fecha_solicitud', '>=', request.fecha_solicitud),('id', '!=', request.id),('maintenance_type_id', '=', request.maintenance_type_id.id)])
                if not future_request_ids:
                    last_request_id = self.search(cr, uid, [('state', 'in', ['confirmed','draft']),('fecha_solicitud', '<=', request.fecha_solicitud),('id', '!=', request.id),('maintenance_type_id', '=', request.maintenance_type_id.id)], order="fecha_solicitud desc", limit=1)
                    if last_request_id:
                        last_request_obj = self.browse(cr, uid, last_request_id[0])
                        request.maintenance_type_id.write({'ultima_ejecucion': last_request_obj.fecha_solicitud})
                    else:
                        request.maintenance_type_id.write({'ultima_ejecucion': False})

        return True

    def confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'confirmed'})
        for request in self.browse(cr, uid, ids):
            if request.maintenance_type_id:
                future_request_ids = self.search(cr, uid, [('state', 'in', ['confirmed','draft']),('fecha_solicitud', '>=', request.fecha_solicitud),('id', '!=', request.id),('maintenance_type_id', '=', request.maintenance_type_id.id)])
                if not future_request_ids and request.maintenance_type_id.ultima_ejecucion != request.fecha_solicitud:
                    request.maintenance_type_id.write({'ultima_ejecucion': request.fecha_solicitud})

        return True

    def open_work_order(self, cr, uid, order_id, context=None):
        data_pool = self.pool.get('ir.model.data')
        if not context:
            context = {}
        if order_id:
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'maintenance', "action_work_order_tree")
        action_pool = self.pool.get(action_model)
        action = action_pool.read(cr, uid, action_id, context=context)
        action['domain'] = "[('id','=', "+str(order_id)+")]"
        action['context'] = "{}"
        return action

    def create_work_order(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        intervention_requests = self.pool.get('intervention.request').browse(cr, uid, ids, context)
        for intervention in intervention_requests:
            element_ids = []
            for obj in intervention.element_ids:
                element_ids.append(obj.id)
            if intervention.maintenance_type_id:
                survey = intervention.maintenance_type_id.survey_id.id
            else:
                survey = None

            vals_order = {
                          'request_id':intervention.id,
                          'element_ids' : [(6, 0, [x.id for x in intervention.element_ids])],
                          'origin_department_id': intervention.department_id.id,
                          'instrucciones':intervention.instrucciones,
                          'maintenance_type_id':intervention.maintenance_type_id.id,
                          'survey_id':survey,
                          'deteccion':intervention.deteccion,
                          'sintoma':intervention.sintoma,
                          'efecto':intervention.efecto,
                          'company_id':intervention.company_id.id,
                          'fecha':intervention.fecha_solicitud,
                          'assigned_department_id': intervention.executor_department_id.id,
                          'descripcion': u", ".join([x.complete_name for x in intervention.element_ids])
                          }
            order_id = self.pool.get('work.order').create(cr, uid, vals_order, context)
            self.pool.get('intervention.request').confirm(cr, uid, ids, context)
            return self.open_work_order(cr, uid, order_id, context)


    def send_email(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'intervention.request',
            'default_res_id': ids[0],
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


intervention_request()

