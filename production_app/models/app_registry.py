# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class AppRegistry(models.Model):
    _name = 'app.registry'
    _rec = 'wc_line_id'

    wc_line_id = fields.Many2one('mrp.production.workcenter.line',
                                 readonly=True)
    name = fields.Char('Workcenter Line', related="wc_line_id.name",
                       readonly=True)
    production_id = fields.Many2one('mrp.production', 'Production',
                                    related="wc_line_id.production_id",
                                    readonly=True)

    _sql_constraints = [
        ('wc_line_id_uniq', 'unique(wc_line_id)',
         'The workcenter line must be unique !'),
    ]

    state = fields.Selection([
        ('waiting', 'Waiting Production'),
        ('confirmed', 'Production Confirmed'),
        ('setup', 'Production Set-Up'),
        ('started', 'Production Started'),
        ('stoped', 'Production Stoped'),
        ('finished', 'Production Finished')], 'State', readonly=True)

    @api.multi
    def confirm_production(self):
        self.ensure_one()
        self.state = 'confirmed'

    @api.multi
    def setup_production(self):
        self.ensure_one()
        self.state = 'setup'

    @api.multi
    def start_production(self):
        self.ensure_one()
        self.state = 'started'

    @api.multi
    def stop_production(self):
        self.ensure_one()
        self.state = 'stoped'

    @api.multi
    def restart_production(self):
        self.ensure_one()
        self.state = 'restarted'

    @api.multi
    def finish_production(self):
        self.ensure_one()
        self.state = 'finished'
