# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class AppRegistry(models.Model):
    _name = 'app.registry'
    _rec = 'wc_line_id'

    workcenter_id = fields.Many2one('mrp.workcenter', 'Line',
                                    readonly=True)
    wc_line_id = fields.Many2one('mrp.production.workcenter.line',
                                 readonly=True)
    # RELATED FIELDS
    name = fields.Char('Workcenter Line', related="wc_line_id.name",
                       readonly=True)
    production_id = fields.Many2one('mrp.production', 'Production',
                                    related="wc_line_id.production_id",
                                    readonly=True)
    state = fields.Selection([
        ('waiting', 'Waiting Production'),
        ('confirmed', 'Production Confirmed'),
        ('setup', 'Production Set-Up'),
        ('started', 'Production Started'),
        ('stoped', 'Production Stoped'),
        ('finished', 'Production Finished')], 'State',
        default='waiting',
        readonly=True)

    _sql_constraints = [
        ('wc_line_id_uniq', 'unique(wc_line_id)',
         'The workcenter line must be unique !'),
    ]

    @api.model
    def get_existing_registry(self, workcenter_id):
        res = False
        domain = [('workcenter_id', '=', workcenter_id),
                  ('state', '!=', 'finished')]
        reg_obj = self.search(domain, limit=1)
        if reg_obj:
            res = reg_obj
        return res

    @api.model
    def create_new_registry(self, workcenter_id):
        domain = [('workcenter_id', '=', workcenter_id),
                  ('state', '!=', 'done')]
        wcl = self.env['mrp.production.workcenter.line']
        wcl_obj = wcl.search(domain, limit=1, order='sequence')
        if not wcl_obj:
            return False

        vals = {
            'workcenter_id': workcenter_id,
            'wc_line_id': wcl_obj.id
        }
        res = self.create(vals)
        return res

    @api.model
    def app_get_registry(self, vals):
        """
        Obtiene el registro que actua de controlador
        para las ordenes de trabajo
        """
        res = {}
        workcenter_id = vals.get('workcenter_id')

        reg = self.get_existing_registry(workcenter_id)
        if not reg:
            reg = self.create_new_registry(workcenter_id)
        if reg:
            res.update(reg.read()[0])
        return res

    @api.model
    def confirm_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.state = 'confirmed'
            res = reg.read()[0]
        return res

    @api.model
    def setup_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.state = 'setup'
            res = reg.read()[0]
        return res

    @api.model
    def start_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.state = 'started'
            res = reg.read()[0]
        return res

    @api.model
    def stop_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.state = 'stoped'
            res = reg.read()[0]
        return res

    @api.model
    def restart_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.state = 'restarted'
            res = reg.read()[0]
        return res

    @api.model
    def finish_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.state = 'finished'
            res = reg.read()[0]
        return res
