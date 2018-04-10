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
    qc_line_ids = fields.One2many('quality.check.line', 'wc_line_id',
                                  'Quality Checks', readonly=False)
    operator_ids = fields.One2many('operator.line', 'wc_line_id',
                                   'Operators', readonly=False)


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    reason_ids =\
        fields.Many2many('stop.reason', rel='stop_reasons_workcenter_rel',
                         id1="workcenter_id", id2="reason_id",
                         domain=[('reason_type', '=', 'technical')])
