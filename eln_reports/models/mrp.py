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
from openerp import models, fields


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    control_sheet_packing = fields.Boolean('Control sheet packing')
    control_sheet_salted = fields.Boolean('Control sheet salted')
    control_sheet_toasted = fields.Boolean('Control sheet toasted')
    control_sheet_fried = fields.Boolean('Control sheet fried')
    control_sheet_mixed = fields.Boolean('Control sheet mixed')
