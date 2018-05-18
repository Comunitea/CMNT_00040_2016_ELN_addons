# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def do_transfer(self):
        """
        When we finish a picking that takes the goods to a transit location
        The system will process automatically the chained picking to take the
        goods from the transit location to the destination location
        """
        res = super(StockPicking, self).do_transfer()
        pick2process_ids = set()
        su_move = self.env['stock.move'].sudo()  # Because of multicompany
        for pick in self:
            for move in pick.move_lines:
                if move.location_dest_id.usage == 'transit' and \
                        move.move_dest_id:
                    next_move = su_move.browse(move.move_dest_id.id)
                    pick2process_ids.add(next_move.picking_id.id)

        pick2process_ids = list(pick2process_ids)
        """
        Evito sudo y hago sudo usuario y con force company
        """
        for pick_id in pick2process_ids:
            pick = self.sudo().browse(pick_id)  # Because of multicompany
            ctx = self._context.copy()
            ctx.update(force_company=pick.company_id.id)
            if self.env['res.users'].browse(self._uid).company_id.id !=\
                    pick.company_id.id:
                user_id = pick.ic_user_id.id
                pick = self.sudo(user_id).with_context(ctx).browse(pick_id)  # same company
            else:
                pick.browse(pick_id)
            pick.do_prepare_partial()
            if pick.state != 'done':
                pick.do_transfer()
        return res


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def split(self, move, qty, restrict_lot_id=False,
              restrict_partner_id=False):
        """
        When the move belongs to other company, make it with sudo.
        Because of partial transfer from one company to another.
        """
        rec = self
        if self.env['res.users'].browse(self._uid).company_id.id !=\
                move.company_id.id:
            rec = self.env['stock.move'].sudo().browse(move.id)
        res = super(StockMove, rec).\
            split(move, qty, restrict_lot_id=restrict_lot_id,
                  restrict_partner_id=restrict_partner_id)
        return res

    @api.multi
    def action_cancel(self):
        res = False
        for move in self:
            rec = move
            if self.env['res.users'].browse(self._uid).company_id.id !=\
                    move.company_id.id:
                rec = self.env['stock.move'].sudo().browse(move.id)
            res = super(StockMove, rec).action_cancel()
        return res


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.multi
    def _mergeable_domain(self):
        """Method from stock quant merge. Adds cost to domain"""
        res = super(StockQuant, self)._mergeable_domain()
        res.append(('cost', '=', self.cost))
        return res
