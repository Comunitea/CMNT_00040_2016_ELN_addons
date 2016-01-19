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

from openerp.osv import fields, orm
import time
from datetime import datetime, date


class work_order_other_services(orm.Model):
    _name = 'work.order.other.services'
    _columns = {
            'code':fields.char('Codigo', size=64, required=False, readonly=False),
            'quantity': fields.float('Quantity'),
            'product_id':fields.many2one('product.product', 'Product'
                                         , required=True),
            'work_order_id':fields.many2one('work.order', 'Work order'
                                            , required=False),
            'employee_id': fields.many2one('hr.employee', 'Employee'
                                           , required=True, select="1"),
                    }

class work_order_time_report(orm.Model):

    def _get_total(self, cr , uid, ids, field_name, args=None, context=None):
        result = {}
        work_order_times = self.pool.get('work.order.time.report').browse(cr,
                                                                          uid,
                                                                          ids,
                                                                          context)
        for work_order_time in work_order_times:
            total = 0.0
            precio_por_defecto = work_order_time.employee_id.product_id.standard_price
            if precio_por_defecto:
                total += work_order_time.horas_normal * precio_por_defecto
                total += work_order_time.horas_nocturnas * (work_order_time.employee_id.producto_hora_nocturna_id.standard_price or precio_por_defecto)
                total += work_order_time.horas_festivas * (work_order_time.employee_id.producto_hora_festiva_id.standard_price or precio_por_defecto)
            result[work_order_time.id] = total
        return result

    _name = "work.order.time.report"
    _columns = {
            'date': fields.date('Fecha'),
            'horas_normal': fields.float('Normal hours'),
            'horas_nocturnas': fields.float('Nightly hours'),
            'horas_festivas': fields.float('Festive hours'),
            'employee_id': fields.many2one('hr.employee', 'Employee'
                                           , required=True, select="1"),
            'work_order_id':fields.many2one('work.order', 'Work order'
                                            , required=False),
            'total': fields.function(_get_total, method=True, type='float'
                                     , string='Total', store=False),
            'element_id': fields.many2one('maintenance.element', 'Element')
                    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

class work_order(orm.Model):

    def _get_planta(self, cr , uid, ids, field_name, args=None, context=None):
        result = {}
        work_orders = self.pool.get('work.order').browse(cr, uid, ids, context)
        for work_order in work_orders:
            result[work_order.id] = work_order.element_ids[0].planta
        return result

    def _get_contrata(self, cr , uid, ids, field_name, args=None, context=None):
        result = {}
        work_orders = self.pool.get('work.order').browse(cr, uid, ids, context)
        for work_order in work_orders:
            result[work_order.id] = ""
            for purchase in work_order.purchase_ids:
                result[work_order.id] += purchase.partner_id.display_name + u", "
            result[work_order.id]=result[work_order.id][:-2]
        return result

    def _get_element_list(self, cr, uid, ids, field_name, args=None, context=None):
        result = {}
        work_orders = self.pool.get('work.order').browse(cr, uid, ids, context)
        for work_order in work_orders:
            result[work_order.id] = ""
            for element in work_order.element_ids:
                result[work_order.id]+=element.codigo + u"\n"
        return result

    def _get_total_other_service(self, cr, uid, ids, field_name, args=None, context=None):
        result = {}
        work_orders = self.pool.get('work.order').browse(cr, uid, ids, context)
        for work_order in work_orders:
            result[work_order.id] = 0
            for service in work_order.other_service_ids:
                result[work_order.id]+=service.quantity*service.product_id.standard_price
        return result


    def _get_total_servicios(self, cr, uid, ids, field_name, args=None, context=None):
        result = {}
        tipo = field_name=="total_servicios_externos"
        work_orders = self.pool.get('work.order').browse(cr, uid, ids, context)
        for work_order in work_orders:
            result[work_order.id] = 0
            for service in work_order.other_service_ids:
                if service.employee_id.externo == tipo:
                    result[work_order.id]+=service.quantity*service.product_id.standard_price

            for hora in work_order.horas_ids:
                if hora.employee_id.externo == tipo:
                    result[work_order.id]+=hora.total
        return result

    _name = 'work.order'
    _inherit = ['mail.thread']
    _columns = {
            'company_id': fields.many2one('res.company', 'Company',
                                          required=True, select=1,
                                          states={'confirmed':[('readonly', True)],
                                            'approved':[('readonly', True)]}),
            'name':fields.char('Name', size=64, required=True, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'request_id':fields.many2one('intervention.request'
                                         , 'Origin request', required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'element_ids':fields.many2many('maintenance.element'
                                           , 'maintenanceelement_work_order_rel'
                                           , 'order_id', 'element_id', 'Maintenance elements'
                                           , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'descripcion': fields.text('Description', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'fecha': fields.date('Request date', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'fecha_inicio': fields.datetime('Initial date', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'assigned_department_id':fields.many2one('hr.department',
                                                     'Assigned department'
                                                     , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'origin_department_id':fields.many2one('hr.department',
                                                   'Origin department'
                                                   , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'stock_moves_ids':fields.one2many('stock.move', 'work_order_id'
                                              , 'Associated movement'
                                              , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'horas_ids':fields.one2many('work.order.time.report'
                                        , 'work_order_id', 'Timesheet'
                                        , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'other_service_ids':fields.one2many('work.order.other.services'
                                                , 'work_order_id', 'Other concepts'
                                                , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'purchase_ids':fields.one2many('purchase.order', 'work_order_id'
                                           , 'Asociated purchases', required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'tipo_parada':fields.selection([
                ('marcha', 'Up'),
                ('parada', 'Stop'),
                 ], 'Operation condition', select=True, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'state':fields.selection([
                ('draft', 'Draft'),
                ('open', 'Open'),
                ('pending', 'Pending approval'),
                ('done', 'Done'),
                ('cancelled', 'Cancelled'),
                 ], 'State', readonly=True),
            'instrucciones': fields.text('Instructions' , states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'maintenance_type_id':fields.many2one('maintenance.type'
                                                  , 'Maintenance type'
                                                  , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'survey_id':fields.many2one('survey.survey', 'Associated survey'
                                        , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'descargo':fields.selection([
                ('bloqueo', 'Block'),
                ('no_descargo', 'Not discharge'),
                ('aviso', 'Warning'),
                 ], 'Discharge', readonly=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'initial_date': fields.date('Initial date', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'final_date': fields.date('Final date', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),

            'responsable_id':fields.many2one('res.users', 'Responsible'
                                             , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'note': fields.text('Report', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'padre_id':fields.many2one('work.order', 'Father order', required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'hijas_ids':fields.one2many('work.order', 'padre_id', 'Ordenes hijas'
                                        , required=False, states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'deteccion':fields.text('Detection', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'sintoma':fields.text('Sign', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'efecto':fields.text('effect', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'planta':fields.function(_get_planta, method=True, type='char'
                                     , string='Floor', store={
                                               'work.order':
                                                (lambda self, cr, uid, ids, c={}: ids, ['element_ids'], 10),
                                               }),
            'contrata':fields.function(_get_contrata, method=True, type='char'
                                       , string='Contractual', store=False),
            'elements_list':fields.function(_get_element_list, method=True, type='char'
                                            , string='Elements string', store=False),
            'total_other_service':fields.function(_get_total_other_service
                                                  , method=True, type='float'
                                                  , string='Other concepts total'
                                                  , store=False),
            'total_servicios_internos':fields.function(_get_total_servicios
                                                       , method=True, type='float'
                                                       , string='Total internal\
                                                                services'
                                                       , store=False),
            'total_servicios_externos':fields.function(_get_total_servicios
                                                       , method=True, type='float'
                                                       , string='Total external\
                                                                services'
                                                       , store=False),
            'action_taken': fields.text('Action taken', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}),
            'picking_type_id': fields.many2one('stock.picking.type', 'Picking type')
                    }
    _defaults = {
        'state':'draft',
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'work.order'),
        'fecha': date.today().strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'work.order', context=c),
        'picking_type_id': lambda obj, cr, uid, context: obj.pool.get('stock.picking.type').search(cr, uid, [('code', '=', 'outgoing')])[0]
    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'work.order'),
            'other_service_ids': None,
            'stock_moves_ids': None,
            'horas_ids': None,
            'purchase_ids':None,
            'hijas_ids': None
        })
        return super(work_order, self).copy(cr, uid, id, default, context)



    def request_validation(self, cr, uid, ids, context=None):
        self.pool.get('work.order').write(cr, uid, ids, {'state':'pending'}
                                          , context)
        return True

    def work_order_cancel(self, cr, uid, ids, context=None):
        self.pool.get('work.order').write(cr, uid, ids, {'state':'cancelled'}
                                          , context)
        return True

    def work_order_open(self, cr , uid, ids, context=None):
        orders = self.pool.get('work.order').browse(cr, uid, ids, context)
        for order in orders:
            if order.initial_date:
                initial_date = order.initial_date
            else:
                initial_date = date.today()
            self.pool.get('work.order').write(cr, uid, order.id
                                              , {'state':'open'
                                                 ,'initial_date':initial_date}, context)
        return True

    def onchange_element_ids(self, cr, uid, ids, element_ids, context=None):
        res = {}
        if element_ids and element_ids[0][2]:
            res['value'] = {
                'descripcion': u", ".join([x.complete_name for x in self.pool.get('maintenance.element').browse(cr, uid, element_ids[0][2])])
            }
        else:
            res['value'] = {
                'descripcion': ""
            }

        return res

    def work_order_done(self, cr, uid, ids, context=None):
        data_obj = self.pool.get('ir.model.data')
        analytic_line_obj = self.pool.get('account.analytic.line')
        order_obj = self.pool.get('work.order')
        picking_out_obj = self.pool.get('stock.picking')
        picking_type_obj = self.pool.get('stock.picking.type')
        ordenes = order_obj.browse(cr, uid, ids, context)

        hours_journal_id = data_obj.get_object_reference(cr, uid, 'hr_timesheet'
                                                         , "analytic_journal")[1]
        services_journal_id = data_obj.get_object_reference(cr, uid, 'maintenance'
                                                            , "maintenance_service_journal")[1]
        materials_journal_id = data_obj.get_object_reference(cr, uid, 'maintenance'
                                                             , "maintenance_materials_journal")[1]
        journals = [hours_journal_id, services_journal_id, materials_journal_id]

        for orden in ordenes:
            # calculo de total de costes para horas, servicios y materiales
            res = {'total': [0, 0, 0]}
            for hora in orden.horas_ids:
                if hora.element_id:
                    if hora.element_id not in orden.element_ids:
                        raise orm.except_orm(u'Error imputación horas', u'El elemento %s está asociado a un reporte de horas de la OT, pero ese equipo no está entre los equipos de la OT' % hora.element_id.name)
                    if not res.get(hora.element_id.id, False):
                        res[hora.element_id.id] = [hora.total, 0, 0]
                    else:
                        res[hora.element_id.id][0] += hora.total
                else:
                    res['total'][0] += hora.total


            res['total'][1]+= orden.total_other_service

            for compra in orden.purchase_ids:
                if compra.state not in ['done', 'approved', 'cancel']:
                    raise orm.except_orm('Compras sin finalizar', 'Compras sin \
                                         finalizar asociadas a la orden')
                for line in compra.order_line:
                    if line.product_id and line.product_id.type == 'service':
                        if line.element_id:
                            if line.element_id not in orden.element_ids:
                                raise orm.except_orm(u'Error imputación compras', u'El elemento %s está asociado a una linea de compra de la OT, pero ese equipo no está entre los equipos de la OT' % line.element_id.name)
                            if not res.get(line.element_id.id, False):
                                res[line.element_id.id] = [0, line.price_subtotal, 0]
                            else:
                                res[line.element_id.id][1] += line.price_subtotal
                        else:
                            res['total'][1] += line.price_subtotal

            for movimiento in orden.stock_moves_ids:
                if movimiento.state not in ['done', 'cancel']:
                    raise orm.except_orm('movimientos sin finalizar',
                                         'Hay movimientos sin finalizar\
                                         asociados a la orden')
                if movimiento.element_id:
                    if movimiento.element_id not in orden.element_ids:
                        raise orm.except_orm(u'Error imputación compras', u'El elemento %s está asociado a un consumo de la OT, pero ese equipo no está entre los equipos de la OT' % movimiento.element_id.name)
                    if not res.get(movimiento.element_id.id, False):
                        res[movimiento.element_id.id] = [0, 0, movimiento.product_qty * movimiento.product_id.standard_price]
                    else:
                        res[movimiento.element_id.id][2] += movimiento.product_qty * movimiento.product_id.standard_price
                else:
                    res['total'][2] += movimiento.product_qty * movimiento.product_id.standard_price

            # calculo de coste proporcional por equipo
            coste_por_equipo = []
            for coste in res['total']:
                coste_por_equipo.append(coste / len(orden.element_ids))

            # creacion de apuntes analiticos para cada equipo
            for equipo in orden.element_ids:
                aux = 0
                for journal in journals:
                    amount = coste_por_equipo[aux] + (res.get(equipo.id, False) and res[equipo.id][aux] or 0.0)
                    if amount:
                        args_analytic_line = {
                                              'account_id':equipo.analytic_account_id.id,
                                              'journal_id':journal,
                                              'amount': -(amount),
                                              'product_id':equipo.product_id.id,
                                              'department_id':orden.origin_department_id.id,
                                              'name':equipo.name,
                                              'date':date.today().strftime('%Y-%m-%d'),
                                              }
                        analytic_line_obj.create(cr, uid, args_analytic_line, context)
                    aux += 1

            if orden.final_date:
                final_date = orden.final_date
            else:
                final_date = date.today()
            order_obj.write(cr, uid, orden.id, {'state': 'done',
                                                'final_date':final_date }
                            , context)
        return True


    def send_email(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid
                                                             , 'maintenance'
                                                             , 'email_template_work_order')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid
                                                                 , 'mail'
                                                                 , 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'work.order',
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
