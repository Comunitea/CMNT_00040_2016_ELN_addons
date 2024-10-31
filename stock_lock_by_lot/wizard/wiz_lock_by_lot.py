# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# © 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class WizLockLotByLot(models.TransientModel):
    _name = 'wiz.lock.by.lot'

   
    def action_lock_by_lots(self):
        active_ids = self._context['active_ids']
        self.env['stock.production.lot'].browse(active_ids).lock_lot()

   
    def action_unlock_by_lots(self):
        active_ids = self._context['active_ids']
        self.env['stock.production.lot'].browse(active_ids).unlock_lot()
