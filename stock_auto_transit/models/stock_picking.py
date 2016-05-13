# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


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
        for pick_id in pick2process_ids:
            pick = self.sudo().browse(pick_id)  # Because of multicompany
            if self.env['res.users'].browse(self._uid).company_id.id ==\
                    pick.company_id.id:
                pick = self.browse(pick_id)  # same company
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
         """
        When the move belongs to other company, make it with sudo.
        """
        res = False
        for move in self:
            rec = move
            if self.env['res.users'].browse(self._uid).company_id.id !=\
                    move.company_id.id:
                rec = self.env['stock.move'].sudo().browse(move.id)
            res = super(StockMove, rec).action_cancel()
        return res

    @api.multi
    def action_done(self):
        # import ipdb; ipdb.set_trace()
        quants_to_unreserve = self.env['stock.quant'].sudo()
        moves_to_check = []
        operations = self.env['stock.pack.operation']
        for move in self:
            for q in move.reserved_quant_ids:
                if q.location_id.id != move.location_id.id:
                    quants_to_unreserve += q
                    moves_to_check.append(move)
        if quants_to_unreserve:
            quants_to_unreserve.write({'reservation_id': False})
            move.picking_id.write({'recompute_pack_op': True})
        for move in moves_to_check:
            for link in move.linked_move_operation_ids:
                operations += link.operation_id
            operations.write({'location_id': move.location_id.id})
        res = super(StockMove, self).action_done()
        import ipdb; ipdb.set_trace()
        if quants_to_unreserve:
            print "BUSCAR O CREAR ABASTECIMIENTO Y RESERVAR LOS NEGATIVOS"
        return res


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    def _get_location_vals(self):
        res = []
        t_loc = self.env['stock.location'].sudo()
        domain = [('usage', '=', 'internal')]
        locs = t_loc.search(domain)
        for l in locs:

            res.append((str(l.id), l.display_name))
        return res

    orig_loc = fields.Selection(_get_location_vals, 'Origin Locartion')


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_origin_location_route(self, product, location):
        """
        MEJOR BUSCAR EMULANDO LA BUSQUEDA DE REGLA PARA EL ABASTECIMIENTO
        """
        res = False
        routes = product.route_ids + product.categ_id.total_route_ids
        for r in routes:
            if r.orig_loc:
                res = int(r.orig_loc)
        return res

    @api.model
    def apply_removal_strategy(self, location, product, quantity, domain,
                               removal_strategy):
        """
        """
        res = super(StockQuant, self).apply_removal_strategy(location,
                                                             product,
                                                             quantity, domain,
                                                             removal_strategy)
        # import ipdb; ipdb.set_trace()
        if not self._context.get('special_assign', False):
            return res

        to_check_qty = 0.0
        for record in res:
            if record[0] is None:
                to_check_qty += record[1]
                res.remove(record)

        orig_loc_id = self._get_origin_location_route(product, location)
        # import ipdb;ipdb.set_trace()
        if to_check_qty and orig_loc_id:

            orig_loc = self.env['stock.location'].sudo().browse(orig_loc_id)
            self_su = \
                self.sudo().with_context(force_company=orig_loc.company_id.id)
            domain = [('reservation_id', '=', False),
                      ('qty', '>', 0),
                      ('product_id', '=', product.id)]
            res2 = self_su._quants_get_order(orig_loc, product, to_check_qty,
                                             domain)
            res.extend(res2)
        return res
