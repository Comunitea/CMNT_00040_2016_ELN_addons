# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'
    _order = 'id desc'

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        res = super(ProcurementOrder, self).\
            _prepare_orderpoint_procurement(orderpoint, product_qty)

        if orderpoint.product_id.uos_id:
            t_uom = self.env['product.uom']
            uom_id = orderpoint.product_uom.id
            uos_id = orderpoint.product_id.uos_id.id
            uos_qty = t_uom._compute_qty(uom_id, product_qty, uos_id)
            res.update(product_uos_qty=uos_qty, product_uos=uos_id)
        return res
