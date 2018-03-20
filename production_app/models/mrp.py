# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields
from .app_registry import APP_STATES


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    registry_id = fields.Many2one('app.registry', 'App Regystry',
                                  readonly=True)

    app_state = fields.Selection(APP_STATES, 'State',
                                 related='registry_id.state', store=True,
                                 readonly=True)
