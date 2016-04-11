# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
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
##############################################################################
from openerp import models, fields


class stock_move(models.Model):
    _inherit = 'stock.move'

    reworked = fields.Boolean('Reworked',
                              related="location_dest_id.reworks_location",
                              readonly=True)


class stock_production_lot(models.Model):
    _inherit = 'stock.production.lot'

    recovery = fields.Boolean('Recovery')


class stock_location(models.Model):
    _inherit = 'stock.location'
    reworks_location = fields.Boolean('Reworks location',
                                      help='Check this box to generate reworks when create a scrap move to this location. Should also mark the check box "Scrap Location".')
