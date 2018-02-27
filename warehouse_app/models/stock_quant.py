# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields

class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def quants_get_prefered_domain(self, location, product, qty, domain=None,
                                   prefered_domain_list=None,
                                   restrict_lot_id=False,
                                   restrict_partner_id=False):
        if 'new_package_id' in self._context:
            prefered_domain_list = [[('package_id', '=', self._context.get('new_package_id', False))]]
        return super(StockQuant, self).quants_get_prefered_domain(
            location, product, qty, domain, prefered_domain_list,
            restrict_lot_id, restrict_partner_id)

    @api.model
    def quants_move(self, quants, move, location_to, location_from=False,
                    lot_id=False, owner_id=False, src_package_id=False,
                    dest_package_id=False):

        return super(StockQuant, self).quants_move(
            quants, move, location_to, location_from=location_from,
            lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id,
            dest_package_id=self._context.get('result_package_id', dest_package_id))
