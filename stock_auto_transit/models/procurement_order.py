# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _create_temp_procurement(self, product, location):
        """
        """
        vals = {
            'product_id': product.id,
            'warehouse_id': self.env['stock.location'].get_warehouse(location),
            'location_id': location.id,
            'product_id': product.id,
            'company_id': location.company_id.id,
            'name': 'temp procurement',
            'product_uom': product.uom_id.id,
            'product_qty': 1.0
        }
        return self.create(vals)

    def _get_origin_location_route(self, product, location):
        """
        """
        res = False
        t_proc = self.env['procurement.order'].sudo()
        proc_tmp = t_proc._create_temp_procurement(product, location)
        rule_id = t_proc._find_suitable_rule(proc_tmp)
        if rule_id:
            rule = self.env['procurement.rule'].browse(rule_id)
            if rule.route_id and rule.route_id.orig_loc:
                res = int(rule.route_id.orig_loc)
        proc_tmp.cancel()
        proc_tmp.unlink()
        return res
