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
from openerp.osv import osv, fields
from datetime import *
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *

class maintenance_type(osv.osv):
    _name = 'maintenance.type'
    _columns = {
                'name':fields.char('Name', size=64, required=False, readonly=False),
                'descripcion': fields.text('Description'),
                'type':fields.selection([
                    ('gama', 'gamma'),
                    ('correctivo', 'corrective'),
                    ('legal', 'legal'),
                    ('preventivo', 'preventivo'),
                     ], 'Type', select=True, required=True,readonly=False),
                #'fault_type': fields.many2many('fault.type', string="Fault Type"),
                'survey_id':fields.many2one('survey', 'Associated survey', required=False),
                'planificado':fields.boolean('Planned', required=False),
                'intervalo':fields.selection([
                    ('4', 'After x Days'),
                    ('3', 'Daily'),
                    ('2', 'Weekly'),
                    ('1', 'Monthly'),
                    ('0', 'Yearly'),
                     ], 'Interval', select=True, readonly=False),
                'inicio': fields.date('Initial date'),
                'ultima_ejecucion': fields.date('last execution'),
                'after_x_days' : fields.integer('Days after ...'),
                'lunes':fields.boolean('Monday', required=False),
                'martes':fields.boolean('Tuesday', required=False),
                'miercoles':fields.boolean('Wednesday', required=False),
                'jueves':fields.boolean('Thursday', required=False),
                'viernes':fields.boolean('Friday', required=False),
                'sabado':fields.boolean('Saturday', required=False),
                'domingo':fields.boolean('Sunday', required=False),
                'element_ids':fields.many2many('maintenance.element', 'maintenanceelement_maintenancetype_rel', 'type_id', 'element_id', 'Maintenance element'),
                }
    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        if not context:
            context = {}
        maintenance_type_obj = self.pool.get('maintenance.type')
        type_ids = maintenance_type_obj.search(cr, uid, [('planificado', '=', True)], offset=0, limit=None, order=None, context=context, count=False)
        type_objs = maintenance_type_obj.browse(cr, uid, type_ids, context)
        dias = {
                    'lunes':MO,
                    'martes':TU,
                    'miercoles':WE,
                    'jueves':TH,
                    'viernes':FR,
                    'sabado':SA,
                    'domingo':SU,
                    }
        for type_obj in type_objs:
            if type_obj.planificado:
                ultima_ej = datetime.strptime(type_obj.ultima_ejecucion or type_obj.inicio, "%Y-%m-%d") 
                fin = (datetime.now() + relativedelta(months=+1)) - relativedelta(days=-1)
                fechas_excluidas = []
                for dia in dias.keys():
                    if type_obj[dia] :
                        fechas_excluidas += rrule(int(type_obj.intervalo), byweekday=dias[dia], dtstart=ultima_ej).between(ultima_ej, fin, inc=True)
                
                fechas = rrule(int(type_obj.intervalo), dtstart=ultima_ej).between(ultima_ej, fin, inc=True)
                if fechas:
                    ultima_creacion = ultima_ej
                    for fecha in fechas:
                        crear_solicitud = True
                        if fecha in fechas_excluidas:
                            fecha_cambiada = False
                            
                            nueva_fecha = fecha
                            while not fecha_cambiada:
                                nueva_fecha = nueva_fecha + relativedelta(days=+1)
                                # si el intervalo es diario 
                                if nueva_fecha in fechas or nueva_fecha > fin:
                                    crear_solicitud = False
                                    break
                                if nueva_fecha not in fechas_excluidas:
                                    fecha = nueva_fecha
                                    fecha_cambiada = True
                        if crear_solicitud:
                            ultima_creacion = fecha
                            element_ids = []
                            for obj in type_obj.element_ids:
                                element_ids.append(obj.id)
                            args_request = {
                                            'maintenance_type_id':type_obj.id,
                                            'element_ids':[(6, 0, element_ids)],
                                            'fecha_solicitud':fecha,
                                            }
                            self.pool.get('intervention.request').create(cr, uid, args_request, context)
                    
                    maintenance_type_obj.write(cr, uid, type_obj.id, {'ultima_ejecucion': ultima_creacion}, context)
        return True
maintenance_type()
