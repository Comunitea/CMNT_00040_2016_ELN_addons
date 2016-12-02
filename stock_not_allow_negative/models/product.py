# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2016 QUIVAL, S.A. All Rights Reserved
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
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allow_negative_stock = fields.Boolean(
        'Allow negative stock',
        help='If checked, allows negative stock level for this stockable product. '
             'Otherwise, the validation of the related stock moves will be blocked '
             'if the stock level will be become negative.')
