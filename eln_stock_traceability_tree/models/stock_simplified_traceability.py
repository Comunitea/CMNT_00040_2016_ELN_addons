# -*- coding: utf-8 -*-
# Copyright 2022 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from datetime import datetime
from dateutil import tz


class ActionSimplifiedTraceability(models.TransientModel):
    _inherit = 'action.simplified.traceability'

    @api.multi
    def action_traceability(self):
        res = super(ActionSimplifiedTraceability, self).action_traceability()

        user_tz = self.env.user.tz
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz(user_tz)
        today = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        today = datetime.strptime(today, '%d-%m-%Y %H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone)
        today = datetime.strftime(today, '%d-%m-%Y %H:%M:%S')

        lot_id = self.env['stock.production.lot'].browse(self.ids)

        name = res.get('name', '')
        name = name + ' / ' + _('Quantity On Hand') + ': ' + str(lot_id and lot_id[0].qty_available or '0.0')
        name = name + ' (' + today + ')'
        res.update(name=name)
        return res
