# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


APP_STATES = [
    ('waiting', 'Waiting Production'),
    ('confirmed', 'Production Confirmed'),
    ('setup', 'Production Set-Up'),
    ('started', 'Production Started'),
    ('stoped', 'Production Stoped'),
    ('cleaning', 'Production Cleaning'),
    ('finished', 'Production Finished'),
    ('validated', 'Validated')]


class AppRegistry(models.Model):
    _name = 'app.registry'

    wc_line_id = fields.Many2one('mrp.production.workcenter.line',
                                 'Work Order', readonly=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center',
                                    readonly=False)
    state = fields.Selection(APP_STATES, 'State', default='waiting',
                             readonly=True)
    setup_start = fields.Datetime('Setup Start')
    setup_end = fields.Datetime('Setup End')
    setup_duration = fields.Float('Setup Duration',
                                  compute="_get_durations")
    production_start = fields.Datetime('Production Start')
    production_end = fields.Datetime('Production End')
    production_duration = fields.Float('Production Duration',
                                       compute="_get_durations")
    cleaning_start = fields.Datetime('Cleaning Start')
    cleaning_end = fields.Datetime('Cleaning End')
    cleaning_duration = fields.Float('Cleaning Duration',
                                     compute="_get_durations")

    # RELATED FIELDS
    name = fields.Char('Workcenter Line', related="wc_line_id.name",
                       readonly=True)
    production_id = fields.Many2one('mrp.production', 'Production',
                                    related="wc_line_id.production_id",
                                    readonly=True)
    product_id = fields.Many2one('product.product', 'Product',
                                 related="production_id.product_id",
                                 readonly=True)
    _sql_constraints = [
        ('wc_line_id_uniq', 'unique(wc_line_id)',
         'The workcenter line must be unique !'),
    ]

    @api.multi
    @api.depends('setup_start', 'setup_end')
    def _get_durations(self):
        for r in self:
            if r.setup_start and r.setup_end:
                setup_start = fields.Datetime.from_string(r.setup_start)
                setup_end = fields.Datetime.from_string(r.setup_end)
                td = setup_end - setup_start
                r.setup_duration = td.total_seconds() / 3600
            if r.production_start and r.production_end:
                production_start = fields.Datetime.\
                    from_string(r.production_start)
                production_end = fields.Datetime.from_string(r.production_end)
                td = production_end - production_start
                r.production_duration = td.total_seconds() / 3600
            if r.cleaning_start and r.cleaning_end:
                cleaning_start = fields.Datetime.from_string(r.cleaning_start)
                cleaning_end = fields.Datetime.from_string(r.cleaning_end)
                td = cleaning_end - cleaning_start
                r.cleaning_duration = td.total_seconds() / 3600

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
                  ('state', '!=', 'done'),
                  ('production_state', 'in',
                  ('ready', 'confirmed', 'in_production')),
                  ('registry_id', '=', False)]
        wcl = self.env['mrp.production.workcenter.line']
        wcl_obj = wcl.search(domain, order='sequence', limit=1)
        if not wcl_obj:
            return False

        vals = {
            'workcenter_id': workcenter_id,
            'wc_line_id': wcl_obj.id
        }
        res = self.create(vals)
        wcl_obj.write({'registry_id': res.id})
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
            reg.write({
                'state': 'confirmed',
            })
            res = reg.read()[0]
        return res

    @api.model
    def setup_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.write({
                'state': 'setup',
                'setup_start': fields.Datetime.now()
            })
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
            reg.write({
                'state': 'started',
                'setup_end': fields.Datetime.now(),
                'production_start': fields.Datetime.now()
            })
            res = reg.read()[0]
        return res

    @api.model
    def stop_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.write({
                'state': 'stoped',
            })
            res = reg.read()[0]
        return res

    @api.model
    def restart_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.write({
                'state': 'started',
            })
            res = reg.read()[0]
        return res

    @api.model
    def clean_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.write({
                'state': 'cleaning',
                'production_end': fields.Datetime.now(),
                'cleaning_start': fields.Datetime.now()
            })
            res = reg.read()[0]
        return res

    @api.model
    def finish_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.write({
                'state': 'finished',
                'cleaning_end': fields.Datetime.now()
            })
            res = reg.read()[0]
        return res

    @api.model
    def get_quality_checks(self, values):
        product_id = values.get('product_id', False)
        quality_type = values.get('quality_type', False)
        product = self.env['product.product'].browse(product_id)
        domain = [('quality_type', '=', quality_type)]
        fields = ['id', 'name', 'value_type']
        res = product.quality_check_ids.search_read(domain, fields)
        res2 = []
        for dic in res:
            dic.update({'value': False})
            res2.append(dic)
        return res2


class QualityCheckLine(models.Model):
    _name = 'quality.check.line'

    name = fields.Char('Name')
    pqc_id = fields.Many2one('product.quality.check', 'Quality Check')
    check = fields.Boolean('Check')
