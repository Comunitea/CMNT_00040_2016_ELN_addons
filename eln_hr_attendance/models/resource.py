# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    @api.multi
    def get_attendances_for_weekdays(self, day_dt):
        if len(self) == 0:
            return []
        return super(ResourceCalendar, self).get_attendances_for_weekdays(day_dt)

