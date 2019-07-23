# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# © 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    locked_lot = fields.Boolean(
        string='Locked', default=False,
        readonly=True)

    @api.multi
    def lock_lot(self):
        if not self.user_has_groups('stock_lock_by_lot.group_lock_unlock_lot'):
            raise exceptions.AccessError(
                _('You are not allowed to lock Serial Numbers/Lots'))
        domain = [ 
            ('lot_id', 'in', self.ids),
            ('reservation_id', '!=', False),
            ('reservation_id.state', 'not in', ('cancel', 'done')),
        ]
        reserved_quants = self.env['stock.quant'].search(domain)
        reserved_quants.mapped("reservation_id").do_unreserve()
        body = _('Serial Number/Lot locked')
        for lot in self:
            lot.message_post(body=body)
        return self.write({'locked_lot': True})

    @api.multi
    def unlock_lot(self):
        if not self.user_has_groups('stock_lock_by_lot.group_lock_unlock_lot'):
            raise exceptions.AccessError(
                _('You are not allowed to unlock Serial Numbers/Lots'))
        body = _('Serial Number/Lot unlocked')
        for lot in self:
            lot.message_post(body=body)
        return self.write({'locked_lot': False})

    @api.model
    def create(self, vals):
        if not 'locked_lot' in vals:
            product_id = vals.get('product_id', self.env.context.get('product_id', False))
            product_id = self.env['product.product'].browse(product_id)
            locked_lot = product_id.categ_id.default_locked_lot
            categ = product_id.categ_id.parent_id
            while categ and not locked_lot:
                locked_lot = categ.default_locked_lot
                categ = categ.parent_id
            vals['locked_lot'] = locked_lot
        res = super(StockProductionLot, self).create(vals)
        if res.locked_lot:
            body = _('Serial Number/Lot locked')
            res.message_post(body=body)
        return res

