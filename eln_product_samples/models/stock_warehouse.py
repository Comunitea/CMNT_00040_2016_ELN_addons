# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class StcokWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    samples_loc_id = fields.Many2one('stock.location', 'Samples location')
