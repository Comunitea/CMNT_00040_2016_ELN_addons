# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _

from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round

class ProcurementOrder(models.Model):
    _inherit = "procurement.order"


    @api.multi
    def run(self, autocommit=False):
        res = super(ProcurementOrder, self).run(autocommit=autocommit)

        #return res

        ##TODO ESCRIBIR WAVE Y RUTA SI YA VIENE POR DEFECTO EN EL PICKING

        domain = [('state','!=', 'cancel'), ('group_id', 'in', self.mapped('group_id').ids)]
        picking_ids = self.env['stock.picking'].sudo().search(domain, order='id asc')
        if picking_ids:

            wave_id = picking_ids[0].wave_id
            route_id = picking_ids[0].route_id
            picks = picking_ids - picking_ids[0]
            if picks:
                picks.write({'wave_id': wave_id.id, 'route_id': route_id.id})

        return res

