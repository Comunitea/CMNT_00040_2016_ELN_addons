# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# © 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    default_locked_lot = fields.Boolean(
        string='Lock new Serial Numbers/Lots',
        help='If checked, new Serial Numbers/lots will be created locked by default')

