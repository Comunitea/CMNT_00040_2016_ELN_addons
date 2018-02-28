# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    @api.model
    def app_get_production(self, vals):
        print "AQQUI ESTAMOS"
        print vals.get('line_id', 'ERROR')
        return vals.get('line_id', 'ERROR')
