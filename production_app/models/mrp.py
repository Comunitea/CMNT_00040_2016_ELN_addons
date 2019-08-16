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

    @api.multi
    def action_start_working(self):
        res = super(MrpProductionWorkcenterLine, self).action_start_working()
        for pl in self:
            if pl.registry_id.setup_start:
                pl.write({'date_start': pl.registry_id.setup_start})
        return res

    @api.multi
    def action_done(self):
        res = super(MrpProductionWorkcenterLine, self).action_done()
        for pl in self:
            if pl.registry_id.cleaning_end:
                pl.write({'date_finished': pl.registry_id.cleaning_end})
        return res

    @api.multi
    def open_production_app_registry_form(self):
        self.ensure_one()
        registry_id = self.registry_id
        if not registry_id:
            return False
        return {
            'name':"APP Registry",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'production.app.registry',
            'res_id': registry_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': self._context
        }


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    reason_ids = fields.Many2many(
        'stop.reason',
        rel='stop_reasons_workcenter_rel',
        id1="workcenter_id", id2="reason_id",
        domain=[('reason_type', '=', 'technical')]
    )
    process_type = fields.Selection([
        ('packing', 'Packing'),
        ('toasted', 'Toasted'),
        ('fried', 'Fried'),
        ('mixed', 'Mixed'),
        ('seasoned', 'Seasoned'),
        ], string='Process Type')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_cancel(self):
        for prod in self:
            if prod.workcenter_lines.mapped('registry_id'):
                raise exceptions.Warning(
                    _("You cannot cancel because one app registry is linked."))
        return super(MrpProduction, self).action_cancel()

    @api.model
    def action_produce(self, production_id, production_qty, production_mode, wiz=False):
        # Si hay registrados movimientos de scrap de consumos los hacemos primero
        if production_mode in ['consume', 'consume_produce']:
            prod = self.env['mrp.production'].browse(production_id)
            registry_ids = prod.workcenter_lines.mapped('registry_id').filtered(
                lambda r: r.state == 'validated')
            line_scrapped_ids = registry_ids.mapped('line_scrapped_ids')
            for line_scrapped_id in line_scrapped_ids:
                scrapped = False
                for move_line in prod.move_lines:
                    key1 = (move_line.product_id, move_line.restrict_lot_id, move_line.location_id)
                    key2 = (line_scrapped_id.product_id, line_scrapped_id.lot_id, line_scrapped_id.location_id)
                    if key1 == key2:
                        product_qty = line_scrapped_id.product_qty
                        restrict_lot_id = line_scrapped_id.lot_id
                        domain = [
                            ('scrap_location', '=', True),
                            ('usage', '!=', 'view'),
                        ]
                        if line_scrapped_id.scrap_type == 'scrap':
                            domain += [
                                '|',
                                ('name', 'ilike', 'desechado'),
                                ('name', 'ilike', 'scrap'),
                            ]
                        if line_scrapped_id.scrap_type == 'losses':
                            domain += [
                                '|',
                                ('name', 'ilike', 'mermas'),
                                ('name', 'ilike', 'losses'),
                            ]
                        scrap_location_id = self.env['stock.location'].search(domain, limit=1)
                        move_line.action_scrap(
                            product_qty, scrap_location_id.id, restrict_lot_id.id)
                        scrapped = True
                        break
                if not scrapped:
                    raise exceptions.Warning(
                        _("There is no valid consumption line to scrap."))
        return super(MrpProduction, self).action_produce(
            production_id, production_qty, production_mode, wiz=wiz)


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    app_notes = fields.Text(string='Notes for App')


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


class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        mode = res.get('mode', False)
        if mode in ('produce', 'consume_produce'):
            record_id = self._context.get('active_id', False)
            prod = self.env['mrp.production'].browse(record_id)
            registry_ids = prod.workcenter_lines.mapped('registry_id').filtered(
                lambda r: r.lot_id)
            if registry_ids:
                res.update(lot_id=registry_ids[0].lot_id.id)
        return res

