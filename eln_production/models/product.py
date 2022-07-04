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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    extended_shelf_life_time = fields.Integer('Extended product shelf life time',
        help="When a new a Serial Number is issued, this is the number of "
             "additional days that the shelf life set by the manufacturer can be extended.")
    check_production_lot_date_type = fields.Selection([
        ('no_check', 'No check'),
        ('short_dates', 'Short dates'),
        ('only_expired', 'Only expired dates')], 'Check production lot date',
        default=False,
        help="No check: in case this product is produced, the date of the "
             "production Serial Number/Lot of this product will not be "
             "verified and it will not be locked if it is wrong.\n"
             "Short dates: in case this product is produced, the date of the "
             "production Serial Number/Lot of this product will be verified "
             "and it will be locked if a component with a expired date or a "
             "lower date than the product produced has been used.\n"
             "Only expired dates: in case this product is produced, the date of the "
             "production Serial Number/Lot of this product will be verified "
             "and it will be locked if a component with a expired date has been used.")

