# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'
    _order = 'id desc'

    @api.model
    def _prepare_orderpoint_procurement(self, orderpoint, product_qty):
        """
        Get the uos conversion to create the procurement and propagate it.
        """
        res = super(ProcurementOrder, self).\
            _prepare_orderpoint_procurement(orderpoint, product_qty)

        if orderpoint.product_id.uos_id:
            t_uom = self.env['product.uom']
            uom_id = orderpoint.product_uom.id
            uos_id = orderpoint.product_id.uos_id.id
            uos_qty = t_uom._compute_qty(uom_id, product_qty, uos_id)
            res.update(product_uos_qty=uos_qty, product_uos=uos_id)
        return res

    @api.model
    def _procure_orderpoint_confirm(self, use_new_cursor=False,
                                    company_id=False):
        """
        Calculate orderpoints with SUPERUSER because of intercompany
        procurements
        """
        rec = self
        if self._context.get('use_sudo', False):
            rec = self.sudo()
        res = super(ProcurementOrder, rec).\
            _procure_orderpoint_confirm(use_new_cursor=use_new_cursor,
                                        company_id=company_id)
        return res
