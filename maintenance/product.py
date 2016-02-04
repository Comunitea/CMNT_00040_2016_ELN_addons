# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015-2016 Comunitea Servicios Tecnologicos All Rights Reserved
#    $Kiko Sánchez$ <kiko@comunitea.com>
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

from openerp import models, fields




class MaintenanceFaultType(models.Model):
    _name ="fault.type"
    _rec_name = 'fault_type'
    fault_type= fields.Char('Fault Type', help = 'General, Neumatic, Electric ...')

class SparePartProperties(models.Model):
    _name = "part.property"

    property_name = fields.Char('Property')
    property_value = fields.Char('Value')
    fault_type = fields.Many2many('fault.type')

class ProductMaintenanceElement(models.Model):
    _name ="product.maintenance.element"

    product_id = fields.Many2one('product.product')
    name_id = fields.Many2one('maintenance.element', 'complete_name')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    spare_part= fields.Boolean('Spare Part', default=True)
    fault_type = fields.Many2many('fault.type')
    part_property_ids = fields.Many2many('part.property')
    maintenance_element_ids = fields.Many2many('maintenance.element')