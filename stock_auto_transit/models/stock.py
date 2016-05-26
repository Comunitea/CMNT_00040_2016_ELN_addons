# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields
from openerp.tools import float_compare as f_c


class StockPicking(models.Model):
    _inherit = "stock.picking"

    auto_transit = fields.Boolean('Auto Transit Picking',
                                  related='picking_type_id.auto_transit',
                                  help="When we do a transfer"
                                  " propose qty and lot based on negative"
                                  " quants to reconciliate.")

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
        user_company_id = self.env['res.users'].browse(self._uid).company_id.id
        for pick in self:
            for move in pick.move_lines:
                if move.location_dest_id.usage == 'transit' and \
                        move.move_dest_id:
                    next_move = move
                    if user_company_id != move.company_id.id:
                        next_move = su_move.browse(move.move_dest_id.id)
                    pick2process_ids.add(next_move.picking_id.id)

        pick2process_ids = list(pick2process_ids)
        for pick_id in pick2process_ids:
            pick = self.browse(pick_id)
            if user_company_id != pick.company_id.id:
                pick = self.sudo().browse(pick_id)
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
        """
        """
        quants_to_unreserve = self.env['stock.quant'].sudo()
        operations = self.env['stock.pack.operation']
        # t_move_su = self.env['stock.move'].sudo()

        customer_loc = self.env.ref('stock.stock_location_customers')
        moves_to_check = self.env['stock.move']
        for move in self:
            # Avoid moves not going to client location
            if move.location_dest_id.id != customer_loc.id:
                continue

            # If quants and move location diferent, wi will unreserve those
            # quants to forze then.
            for q in move.reserved_quant_ids:
                if q.location_id.id != move.location_id.id:
                    quants_to_unreserve += q
                    moves_to_check += move

        # Unreserve Quants
        if quants_to_unreserve:
            quants_to_unreserve.write({'reservation_id': False})
            # move.picking_id.write({'recompute_pack_op': True}) # ???

        # Restore the move origin location in the operation to search quants.
        for move in moves_to_check:
            for link in move.linked_move_operation_ids:
                operations += link.operation_id
            operations.write({'location_id': move.location_id.id})

        # Action done will force the unreserve quants
        res = super(StockMove, self).action_done()
        return res

    @api.multi
    def action_assign(self):
        customer_loc = self.env.ref('stock.stock_location_customers')
        for move in self:
            rec = self
            if move.location_dest_id.id == customer_loc.id and\
                    move.state != 'waiting':
                ctx = self._context.copy()
                ctx.update(special_assign=True)
                rec = self.with_context(ctx).browse(move.id)

            res = super(StockMove, rec).action_assign()
        return res

    @api.model
    def _get_quants_to_transit(self, orig_move, q2transit):
        # Search quants to force the assignament later
        res = []
        t_quant_su = self.env['stock.quant'].sudo()
        prod = orig_move.product_id
        rounding = prod.uom_id.rounding
        for lot_id in q2transit:
            domain = [
                ('product_id', '=', prod.id),
                ('location_id', '=', orig_move.location_id.id),
                ('reservation_id', '=', False),
                ('qty', '>', 0.0)]
            quants_objs = t_quant_su.search(domain)
            assigned_qty = 0
            rst_qty = q2transit[lot_id]
            for q in quants_objs:
                fc2 = f_c(rst_qty, q.qty, precision_rounding=rounding)
                if fc2 != -1:  # quant qty enougth
                    res.append((q, q.qty))
                    assigned_qty += q.qty
                    break
                else:  # quant qty less than needed
                    res.append((q, rst_qty))
                    assigned_qty += rst_qty
                rst_qty -= assigned_qty
                if not rst_qty:
                    break
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

    orig_loc = fields.Selection(_get_location_vals, 'Origin Locartion',
                                help="Set it the final origin location to "
                                "get the products. Needed to do a reserve"
                                " of quants forced when doing a sale "
                                " to reconciliate later")


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def apply_removal_strategy(self, location, product, quantity, domain,
                               removal_strategy):
        """
        """
        # Quants already calculed will be returned
        if self._context.get('forced_quants', []):
            return self._context['forced_quants']
        ctx = self._context.copy()
        ctx.update(force_company=location.company_id.id)
        rec = self.with_context(ctx).browse(self.id)
        res = super(StockQuant, rec).apply_removal_strategy(location,
                                                            product,
                                                            quantity, domain,
                                                            removal_strategy)
        if not self._context.get('special_assign', False):
            return res

        to_check_qty = 0.0
        recs_to_remove = []
        for record in res:
            if record[0] is None:
                to_check_qty += record[1]
                recs_to_remove.append(record)

        t_proc = self.env['procurement.order']
        orig_loc_id = t_proc._get_origin_location_route(product, location)
        if to_check_qty and orig_loc_id:
            for r in recs_to_remove:
                res.remove(r)
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

    @api.multi
    def unlink(self):
        ctx = self._context.copy()
        ctx.update(force_unlink=True)
        rec = self.with_context(ctx)
        res = super(StockQuant, rec).unlink()
        return res

    @api.model
    def _search_negative_quants_qty(self, loc, extra_domain=[]):
        """
        Returns dic with negative qty in absolute value grouped by product and
        lot
        """
        res = {}
        domain = [('qty', '<', 0), ('location_id', '=', loc.id)]
        domain.extend(extra_domain)
        quant_objs = self.env['stock.quant'].search(domain)
        for q in quant_objs:
            if q.product_id not in res:
                res[q.product_id] = {q.lot_id: 0.0}
            if q.lot_id not in res[q.product_id]:
                res[q.product_id][q.lot_id] = 0.0
            res[q.product_id][q.lot_id] += abs(q.qty)
        return res

    @api.multi
    def _mergeable_domain(self):
        """Method from stock quant merge. Adds cost to domain"""
        res = super(StockQuant, self)._mergeable_domain()
        res.append(('cost', '=', self.cost))
        return res


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    auto_transit = fields.Boolean('Auto Transit',
                                  help="When we do a transfer"
                                  " propose qty and lot based on negative"
                                  " quants to reconciliate.")


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    from_negative_quant = fields.Boolean('From negative', readonly=True)
