# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_validated(self, cr, uid, ids, context=None):
        t_move = self.pool.get('stock.move')
        for production in self.browse(cr, uid, ids, context=context):
            moves = [x.id for x in production.move_created_ids2]
            t_move.get_price_from_cost_structure(cr, uid, moves, context)
        res = super(MrpProduction, self).action_validated(cr, uid, ids,
                                                          context=context)
        return res
