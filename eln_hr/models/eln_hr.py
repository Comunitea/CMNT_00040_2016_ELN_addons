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
from openerp import models, fields, api, exceptions, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'    

    dni_id = fields.Char('DNI No', size=64)
    tipo_contrato_id = fields.Many2one('hr.employee_tipo_contrato', string='Type of Contract')
    fecha_alta_empresa = fields.Date('Entry Date')
    fecha_fijo_empresa = fields.Date('Permanent Staff Date')
    fecha_baja_empresa = fields.Date('Leaving Date')
    motivo_baja_empresa = fields.Char('Reason for leaving', size=64)
    grupo_cotizacion = fields.Integer('Contribution Group', size=2)
    numero_hijos = fields.Integer('Number of Children', size=2)

    personal_street1 = fields.Char('Street 1', size=64)
    personal_street2 = fields.Char('Street 2', size=64)
    personal_zip = fields.Char('Zip', size=10)
    personal_city = fields.Char('City', size=32)
    personal_state = fields.Char('State', size=32)
    personal_country = fields.Char('Country', size=32)
    personal_phone = fields.Char('Phone', size=16)
    personal_mobile = fields.Char('Mobile', size=16)
    personal_email = fields.Char('Email', size=64)

    persona_aviso_emergencia_1 = fields.Char('Person 1', size=64, help="Person to notify in case of emergency.")
    telefono_aviso_emergencia_1 = fields.Char('Phone 1', size=32, help="Phone to contact in case of emergency.")
    persona_aviso_emergencia_2 = fields.Char('Person 2', size=64, help="Person to notify in case of emergency.")
    telefono_aviso_emergencia_2 = fields.Char('Phone 2', size=32, help="Phone to contact in case of emergency.")
    persona_aviso_emergencia_3 = fields.Char('Person 3', size=64, help="Person to notify in case of emergency.")
    telefono_aviso_emergencia_3 = fields.Char('Phone 3', size=32, help="Phone to contact in case of emergency.")

    contrataciones_anteriores_ids = fields.One2many('hr.employee_contrataciones_anteriores', 'employee_id', string='Human Resources - Previous Recruitments')
    formacion_academica_ids = fields.One2many('hr.employee_formacion_academica', 'employee_id', string="Human Resources - Academic Background")
    experiencia_laboral_ids = fields.One2many('hr.employee_experiencia_laboral', 'employee_id', string='Human Resources - Work Experience')
    formacion_en_la_empresa_ids = fields.One2many('hr.employee_formacion_en_la_empresa', 'employee_id', string="Human Resources - Company Training")
    carnet_conducir_b = fields.Boolean('Driving License B')
    carnet_conducir_c = fields.Boolean('Driving License C')
    carnet_conducir_c1 = fields.Boolean('Driving License C1')
    observaciones = fields.Text('Observations')

    @api.multi
    def unlink(self):
        employee_ids = self._ids
        if employee_ids:
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
                self._cr.execute(sql, [employee_ids])
                exist_record = self._cr.fetchall()
                if exist_record[0][0]:
                    raise exceptions.Warning(
                        _("You cannot remove employee that is referenced by: %s") % (table))
        return super(HrEmployee, self).unlink()


class HrEmployeeTipoContrato(models.Model):
    _name = "hr.employee_tipo_contrato"
    _description = "Human Resources - Type of Contract"

    name = fields.Char('Type of Contract', size=64, required=True, translate=True)
    active = fields.Boolean('Active', default=True)


class HrEmployeeContratacionesAnteriores(models.Model):
    _name = "hr.employee_contrataciones_anteriores"
    _description = "Human Resources - Previous Recruitments"
    _order = 'fecha_inicio'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    empresa = fields.Char('Company', size=64)
    fecha_inicio = fields.Date('Start Date')
    fecha_fin = fields.Date('End Date')


class HrEmployeeFormacionAcademica(models.Model):
    _name = "hr.employee_formacion_academica"
    _description = "Human Resources - Academic Background"
    _order = 'final_year'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    estudios = fields.Char('Studies', size=64)
    centro = fields.Char('Study Centre', size=64)
    final_year = fields.Char('Final Year', size=4)


class HrEmployeeExperienciaLaboral(models.Model):
    _name = "hr.employee_experiencia_laboral"
    _description = "Human Resources - Work Experience"
    _order = 'fecha_inicio'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    empresa = fields.Char('Company', size=64)
    actividad = fields.Char('Activity Carried Out', size=64)
    fecha_inicio = fields.Char('Start Date', size=10)
    fecha_fin = fields.Char('End Date', size=10)


class HrEmployeeFormacionEnLaEmpresa(models.Model):
    _name = "hr.employee_formacion_en_la_empresa"
    _description = "Human Resources - Company Training"
    _order = 'fecha_curso'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    curso_documentacion = fields.Char('Course/Documentation', size=64)
    tipo_certificacion = fields.Char('Type of Certification', size=64)
    fecha_curso = fields.Char('Date', size=10)
    valoracion = fields.Char('Valuation', size=64)
    fecha_valoracion = fields.Char('Valued on Date', size=10)

