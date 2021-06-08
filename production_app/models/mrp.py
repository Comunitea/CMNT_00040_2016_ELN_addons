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
    quality_check_ids = fields.Many2many(
        'product.quality.check',
        rel='product_quality_check_workcenter_rel',
        id1='workcenter_id', id2='quality_id'
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
        if production_mode in ['consume', 'consume_produce']:
            prod = self.env['mrp.production'].browse(production_id)
            registry_ids = prod.workcenter_lines.mapped('registry_id')
            # No se permite hacer consumos de producciones con registros de app no validados
            if not all(x.state == 'validated' for x in registry_ids):
                raise exceptions.except_orm(_('Error'),
                    _("At least one app registry associated with this production is not validated."))
            # Si hay registrados movimientos de scrap de consumos los hacemos primero
            line_scrapped_ids = registry_ids.mapped('line_scrapped_ids')
            for line_scrapped_id in line_scrapped_ids:
                product_id = line_scrapped_id.product_id
                if product_id.type == 'service':
                    continue
                product_qty = line_scrapped_id.product_qty
                if product_qty <= 0:
                    raise exceptions.Warning(
                        _('Please provide a positive quantity to scrap.'))
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
                if not scrap_location_id:
                    raise exceptions.Warning(
                        _("There is no valid scrap location."))
                source_location_id = line_scrapped_id.location_id.id
                destination_location_id = scrap_location_id.id
                restrict_lot_id = line_scrapped_id.lot_id
                if not restrict_lot_id and (product_id.track_production or product_id.track_all):
                    raise exceptions.Warning(
                        _('You must assign a serial number for the scrapped product'),
                        _('%s') % (product_id.name))
                procure_method = self._get_raw_material_procure_method(
                    product_id, location_id=source_location_id, location_dest_id=destination_location_id)
                warehouse_id = self.env['stock.location'].get_warehouse(prod.location_src_id)
                vals = {
                    'name': prod.name,
                    'date': prod.date_planned,
                    'date_expected': prod.date_planned,
                    'product_id': product_id.id,
                    'product_uom_qty': product_qty,
                    'product_uom': product_id.uom_id.id,
                    'product_uos_qty': False,
                    'product_uos': False,
                    'location_id': source_location_id,
                    'location_dest_id': destination_location_id,
                    'restrict_lot_id': restrict_lot_id.id,
                    'company_id': prod.company_id.id,
                    'procure_method': procure_method,
                    'raw_material_production_id': prod.id,
                    'price_unit': product_id.standard_price,
                    'origin': prod.name,
                    'warehouse_id': warehouse_id,
                    'group_id': prod.move_prod_id.group_id.id,
                } 
                move_id = self.env['stock.move'].create(vals)
                move_id.action_done()
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

