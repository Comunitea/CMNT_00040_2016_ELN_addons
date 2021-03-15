# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# © 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, exceptions, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    locked_lot = fields.Boolean(
        string='Locked', related='lot_id.locked_lot', default=False,
        store=True)

    @api.model
    def quants_get(self, location, product, qty, domain=None,
                   restrict_lot_id=False, restrict_partner_id=False):
        if domain is None:
            domain = []
        domain += [('locked_lot', '=', False)]
        return super(StockQuant, self).quants_get(
            location, product, qty, domain=domain,
            restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id)

    @api.model
    def quants_move(self, quants, move, location_to, location_from=False,
                    lot_id=False, owner_id=False, src_package_id=False,
                    dest_package_id=False):
        if lot_id:
            lot = self.env['stock.production.lot'].browse(lot_id)
            locked_lot = lot.locked_lot
            if locked_lot:
                location_from_usage = \
                    location_from and location_from.usage or \
                    move and move.location_id.usage or False
                if location_from_usage == 'internal':
                    raise exceptions.ValidationError(
                        _("The following lots/serial number is locked and cannot be moved:\n%s") % lot.name)
        return super(StockQuant, self).quants_move(
            quants, move, location_to, location_from=location_from,
            lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id,
            dest_package_id=dest_package_id)
