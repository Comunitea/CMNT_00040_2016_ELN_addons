# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class StockQuant(models.Model):
    _inherit = "stock.quant"


    @api.model
    def quants_reserve(self, quants, move, link=False):
        super(StockQuant, self).quants_reserve(quants=quants, move=move, link=link)
        move.get_state_from_pre_move()
