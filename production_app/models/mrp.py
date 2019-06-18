# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields, _
from .production_app import APP_STATES
from openerp import exceptions


class MrpProductionWorkcenterLine(models.Model):
    _inherit = 'mrp.production.workcenter.line'

    registry_id = fields.Many2one(
        'production.app.registry', 'App Registry', readonly=True)
    app_state = fields.Selection(APP_STATES, 'State',
        related='registry_id.state', store=True, readonly=True)
    qc_line_ids = fields.One2many(
        'quality.check.line', 'wc_line_id', 'Quality Checks', readonly=False)
    operator_ids = fields.One2many(
        'operator.line', 'wc_line_id', 'Operators', readonly=False)

    @api.multi
    def action_cancel(self):
        for pl in self:
            if pl.registry_id:
                raise exceptions.Warning(
                    _("You cannot cancel because one app registry is linked."))
        return super(MrpProductionWorkcenterLine, self).action_cancel()

    @api.multi
    def unlink(self):
        for pl in self:
            if pl.registry_id:
                raise exceptions.Warning(
                    _("You cannot remove because one app registry is linked."))
        return super(MrpProductionWorkcenterLine, self).unlink()


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    reason_ids = fields.Many2many(
        'stop.reason',
        rel='stop_reasons_workcenter_rel',
        id1="workcenter_id", id2="reason_id",
        domain=[('reason_type', '=', 'technical')]
    )


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_cancel(self):
        for prod in self:
            if prod.workcenter_lines.mapped('registry_id'):
                raise exceptions.Warning(
                    _("You cannot cancel because one app registry is linked."))
        return super(MrpProduction, self).action_cancel()


class ChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        record_id = self._context.get('active_id', False)
        assert record_id, _('Active Id not found')
        prod = self.env['mrp.production'].browse(record_id)
        if prod.workcenter_lines.mapped('registry_id'):
            raise exceptions.Warning(
                _("You cannot change qty because one app registry is linked."))
        return super(ChangeProductionQty, self).change_prod_qty()

