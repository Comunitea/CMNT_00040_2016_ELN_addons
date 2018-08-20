# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import ValidationError
from openerp.tools.float_utils import float_compare, float_round


class StockLocationPath(models.Model):

    _inherit = "stock.location.path"

    auto = fields.Selection(selection_add=[("move_dest", "Auto confirm move_dest")])

    def _apply_bis(self, cr, uid, rule, move, context=None):

        if rule.auto == 'move_dest':
            #Tengo que utilizar el usuario intercomañia del movimiento
            move_uid = move.sudo().move_dest_id.get_pda_ic(move.id)
            move.move_dest_id.sudo(move_uid).action_confirm()

            #move.action_done()
        else:
            return super(StockLocationPath, self)._apply(cr=cr, uid=uid, rule=rule, move=move, context=context)

