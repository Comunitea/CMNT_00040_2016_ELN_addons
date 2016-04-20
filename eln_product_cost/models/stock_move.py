# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def attribute_price(self, cr, uid, move, context=None):
        """
        Avoid calculation of cost when confirm the production order
        """
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['skip_costs'] = True
        super(StockMove, self).attribute_price(cr, uid, move, context=ctx)
