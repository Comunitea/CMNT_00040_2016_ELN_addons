# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
import logging
import addons

class hr_employee(osv.osv):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = 'hr.employee'    
    _columns = {
        'name_employee': fields.related('resource_id', 'name', type='char', string='Name', readonly=True, store=True),

        'dni_id':fields.char('DNI No', size=64),
        'identification_id': fields.char('Identification No', size=32, help="Employee registration number"),
        'tipo_contrato_id': fields.many2one('hr.employee_tipo_contrato', 'Tipo de contrato', select=True),
        'fecha_alta_empresa': fields.date("Fecha alta", help="Fecha de alta en la empresa"),
        'fecha_fijo_empresa': fields.date("Fijo plantilla", help="Fecha desde la que es fijo en la empresa"),
        'fecha_baja_empresa': fields.date("Fecha baja", help="Fecha de baja en la empresa"),
        'motivo_baja_empresa': fields.char('Motivo/Causa baja', size=64, help="Motivo o causa de la baja en la empresa"),
        'grupo_cotizacion': fields.integer('Grupo cotización', size=2, help="Grupo de cotización"),
        'numero_hijos': fields.integer('Número de hijos', size=2, help="Número de hijos"),

        'persona_aviso_emergencia_1': fields.char('Persona 1', size=64, help="Persona a quien avisar en caso de emergencia"),
        'telefono_aviso_emergencia_1': fields.char('Teléfono 1', size=32, help="Teléfono en el que avisar en caso de emergencia"),
        'persona_aviso_emergencia_2': fields.char('Persona 2', size=64, help="Persona a quien avisar en caso de emergencia"),
        'telefono_aviso_emergencia_2': fields.char('Teléfono 2', size=32, help="Teléfono en el que avisar en caso de emergencia"),
        'persona_aviso_emergencia_3': fields.char('Persona 3', size=64, help="Persona a quien avisar en caso de emergencia"),
        'telefono_aviso_emergencia_3': fields.char('Teléfono 3', size=32, help="Teléfono en el que avisar en caso de emergencia"),
        
        'contrataciones_anteriores_ids': fields.one2many('hr.employee_contrataciones_anteriores', 'employee_id', string="Recursos Humanos - Contrataciones anteriores"),
        'formacion_academica_ids': fields.one2many('hr.employee_formacion_academica', 'employee_id', string="Recursos Humanos - Formación Académica"),
        'experiencia_laboral_ids': fields.one2many('hr.employee_experiencia_laboral', 'employee_id', string="Recursos Humanos - Experiencia Laboral"),
        'formacion_en_la_empresa_ids': fields.one2many('hr.employee_formacion_en_la_empresa', 'employee_id', string="Recursos Humanos - Formación en la empresa"),
        'carnet_conducir_b': fields.boolean('Carnet de conducir B'),
        'carnet_conducir_c': fields.boolean('Carnet de conducir C'),
        'carnet_conducir_c1': fields.boolean('Carnet de conducir C1'),
        'observaciones': fields.char('Observaciones', size=255),
    }

    _defaults = {
        'active': True
    }
    _order = 'name_employee'
#    def unlink(self, cr, uid, ids, context=None):
#        resource_obj = self.pool.get('resource.resource')
#        resource_ids = []
#        unlink_status = False
#        for employee in self.browse(cr, uid, ids, context=context):
#            resource = employee.resource_id
#            if resource:
#                resource_ids.append(resource.id)
#        unlink_status = super(hr_employee, self).unlink(cr, uid, ids, context=context)
#        if resource_ids:
#            resource_obj.unlink(cr, uid, resource_ids, context=context)
#        return unlink_status

hr_employee()

class hr_employee_tipo_contrato(osv.osv):
    _name = "hr.employee_tipo_contrato"
    _description = "Recursos Humanos - Tipo de contrato"
    _columns = {
        'name': fields.char('Tipo Contrato', size=64, required=True, translate=True),
        'active': fields.boolean('Active'),
    }
    
    _defaults = {
        'active': True
    }

hr_employee_tipo_contrato()

class hr_employee_contrataciones_anteriores(osv.osv):
    _name = "hr.employee_contrataciones_anteriores"
    _description = "Recursos Humanos - Contrataciones anteriores"
    _order = 'fecha_inicio'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado', required=True, select="1"),
        'empresa': fields.char('Empresa', size=64),
        'fecha_inicio': fields.date("Fecha inicio"),
        'fecha_fin': fields.date("Fecha fin"),
    }

hr_employee_contrataciones_anteriores()

class hr_employee_formacion_academica(osv.osv):
    _name = "hr.employee_formacion_academica"
    _description = "Recursos Humanos - Experiencia Laboral"
    _order = 'final_year'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado', required=True, select="1"),
        'estudios': fields.char('Estudios', size=64),
        'centro': fields.char('Centro', size=64, help='Centro en el que se realizaron los estudios'),
        'final_year': fields.char('Año final', size=4),
    }

hr_employee_formacion_academica()

class hr_employee_experiencia_laboral(osv.osv):
    _name = "hr.employee_experiencia_laboral"
    _description = "Recursos Humanos - Experiencia Laboral"
    _order = 'fecha_inicio'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado', required=True, select="1"),
        'empresa': fields.char('Nombre de la empresa', size=64),
        'actividad': fields.char('Actividad desempeñada', size=64, help='Actividad desempeñada en la empresa'),
        'fecha_inicio': fields.char("Fecha inicio", size=10),
        'fecha_fin': fields.char("Fecha fin", size=10),
    }

hr_employee_experiencia_laboral()

class hr_employee_formacion_en_la_empresa(osv.osv):
    _name = "hr.employee_formacion_en_la_empresa"
    _description = "Recursos Humanos - Formación en la empresa"
    _order = 'fecha_curso'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Empleado', required=True, select="1"),
        'curso_documentacion': fields.char('Curso/Documentación', size=64),
        'tipo_certificacion': fields.char('Tipo de certificación', size=64),
        'fecha_curso': fields.char("Fecha", size=10),
        'valoracion': fields.char('Valoración', size=64),
        'fecha_valoracion': fields.char("Valorado en fecha", size=10),
    }

hr_employee_formacion_en_la_empresa()

class hr_job(osv.osv):
    _name = "hr.job"
    _description = "Job Description"
    _inherit = 'hr.job'    
    _columns = {
        'name': fields.char('Job Name', size=128, required=True, select=True, translate=True),
    }

hr_job()


