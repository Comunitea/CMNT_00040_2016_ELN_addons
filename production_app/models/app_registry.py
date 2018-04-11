# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields
from datetime import datetime, timedelta

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
    _order = 'id desc'

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
    qc_line_ids = fields.One2many('quality.check.line', 'registry_id',
                                  'Quality Checks', readonly=False)
    stop_line_ids = fields.One2many('stop.line', 'registry_id',
                                    'Production Stops', readonly=False)
    operator_ids = fields.One2many('operator.line', 'registry_id',
                                   'Operators', readonly=False)
    qty = fields.Float('Quantity', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', readonly=True)

    # RELATED FIELDS
    name = fields.Char('Workcenter Line', related="wc_line_id.name",
                       readonly=True)
    production_id = fields.Many2one('mrp.production', 'Production',
                                    related="wc_line_id.production_id",
                                    readonly=True)
    product_id = fields.Many2one('product.product', 'Product',
                                 related="production_id.product_id",
                                 readonly=True)
    workorder_id = fields.Many2one('work.order', 'Related Maintance Order')
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
                  ('state', 'not in', ('finished', 'validated'))]
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

        allowed_operators = []
        if op.wc_line_id:
            for op in reg.wc_line_id.operators_ids:
                allowed_operators.append({'id': op.id, 'name': op.name})

        use_time = reg.wc_line_id.production_id.product_id.use_time
        use_date = (datetime.now() + timedelta(use_time)).strftime("%Y-%m-%d")
        res.update(allowed_operators=allowed_operators,
                   product_use_date=use_date)
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
        date = fields.Datetime.now()
        if values.get('setup_start', False):
            date = values['setup_start']
        if reg:
            reg.write({
                'state': 'setup',
                'setup_start': date
            })
            res = reg.read()[0]
        return res

    @api.model
    def get_lot(self, values, reg):
        lot_id = False
        spl = self.env['stock.production.lot']
        product_id = reg.product_id.id
        lot_name = values.get('lot_name', '')
        lot_date = values.get('lot_date', '')
        lot_date = lot_date if lot_date else False
        if product_id and lot_name:
            domain = [('name', '=', lot_name), ('product_id', '=', product_id)]
            lot_obj = spl.search(domain, limit=1)
            if not lot_obj:
                vals = {'name': lot_name,
                        'product_id': product_id,
                        'use_date': lot_date}
                lot_obj = spl.create(vals)
            lot_id = lot_obj.id
        return lot_id

    @api.model
    def start_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        date = fields.Datetime.now()
        if values.get('setup_end', False):
            date = values['setup_end']
        if reg:
            lot_id = self.get_lot(values, reg)
            reg.state = 'started'
            reg.write({
                'state': 'started',
                'setup_end': date,
                'production_start': date,
                'lot_id': lot_id,
            })
            res = reg.read()[0]
        return res

    @api.model
    def create_maintenance_order(self, reg):
        mt = self.env['maintenance.type'].\
            search([('type', '=', 'correctivo')], limit=1)
        wo = self.env['work.order'].create({'maintenance_type_id': mt.id})
        reg.write({'workorder_id': wo.id})
        return True

    @api.model
    def stop_production(self, values):
        res = {}
        reg = False
        operator_id = False
        if values.get('active_operator_id', False):  # Can be 0
            operator_id = values['active_operator_id']
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        if reg:
            reg.write({
                'state': 'stoped',
            })
            date = fields.Datetime.now()
            if values.get('stop_start', False):
                date = values['stop_start']
            stop_obj = reg.create_stop(values.get('reason_id', False),
                                       operator_id, date)
            create_mo = values.get('create_mo', False)
            if create_mo:
                self.create_maintenance_order(reg)
            res = reg.read()[0]
            res.update({'stop_id': stop_obj.id})
        return res

    @api.model
    def restart_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        date = fields.Datetime.now()
        if values.get('stop_end', False):
            date = values['stop_end']
        if reg:
            reg.write({
                'state': 'started',
            })
            stop_id = values.get('stop_id', False)
            if stop_id:
                self.env['stop.line'].browse(stop_id).write({
                    'stop_end': date})
            res = reg.read()[0]
        return res

    @api.model
    def restart_and_clean_production(self, values):
        self.restart_production(values)
        res = self.clean_production(values)
        return res

    @api.model
    def clean_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        date = fields.Datetime.now()
        if values.get('cleaning_start', False):
            date = values['cleaning_start']
        if reg:
            reg.write({
                'state': 'cleaning',
                'production_end': date,
                'cleaning_start': date
            })
            res = reg.read()[0]
        return res

    @api.model
    def finish_production(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        date = fields.Datetime.now()
        if values.get('stop_start', False):
            date = values['cleaning_end']
        if reg:
            reg.write({
                'state': 'finished',
                'cleaning_end': date,
                'qty': values.get('qty', 0.00),
            })
            operators_loged = self.env['operator.line']
            for op in reg.operator_ids:
                if not op.date_out:
                    operators_loged += op
            if operators_loged:
                operators_loged.write({'date_out': date})
            res = reg.read()[0]
        return res

    @api.model
    def get_quality_checks(self, values):
        product_id = values.get('product_id', False)
        product = self.env['product.product'].browse(product_id)
        domain = [('id', 'in', product.quality_check_ids.ids)]
        fields = ['id', 'name', 'value_type', 'quality_type', 'repeat',
                  'required_text', 'max_value', 'min_value']
        res = product.quality_check_ids.search_read(domain, fields)
        res2 = []
        for dic in res:
            dic.update({'value': ''})
            res2.append(dic)
        return res2

    @api.model
    def app_save_quality_checks(self, values):
        registry_id = values.get('registry_id', False)
        lines = values.get('lines', [])
        operator_id = False
        if values.get('active_operator_id', False):  # Can be 0
            operator_id = values['active_operator_id']
        date = fields.Datetime.now()
        if values.get('qc_date', False):
            date = values['qc_date']
        for dic in lines:
            vals = {
                'registry_id': registry_id,
                'pqc_id': dic.get('id', False),
                'date': date,
                'value': str(dic.get('value', False)),
                'operator_id': operator_id
            }
            self.env['quality.check.line'].create(vals)
        return True

    @api.multi
    def validate(self):
        wc_line = self.wc_line_id
        stop_values = []
        for stop in self.stop_line_ids:
            val = {'name': stop.operator_id.name,
                   'reason': stop.reason_id.name,
                   'time': stop.stop_duration}
            stop_values.append((0, 0, val))

        vals = {
            'date_start': self.setup_start,
            'date_finidhed': self.cleaning_end,
            'real_time': self.production_duration,
            'time_start': self.setup_duration,
            'time_stop': self.cleaning_duration,
            'production_stops_ids': stop_values or False
        }
        wc_line.write(vals)
        self.qc_line_ids.write({'wc_line_id': wc_line.id})
        self.operator_ids.write({'wc_line_id': wc_line.id})
        self.write({'state': 'validated'})
        return

    @api.multi
    def create_stop(self, reason_id, operator_id, date_stop):
        self.ensure_one()
        vals = {
            'registry_id': self.id,
            'stop_start': date_stop,
            'reason_id': reason_id,
            'operator_id': operator_id
        }
        res = self.env['stop.line'].create(vals)
        return res

    @api.multi
    def create_operator_line(self, operator_id, date_in):
        self.ensure_one()
        vals = {
            'registry_id': self.id,
            'operator_id': operator_id,
            'date_in': date_in
        }
        res = self.env['operator.line'].create(vals)
        return res

    @api.model
    def log_in_operator(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        date = fields.Datetime.now()
        if values.get('date_in', False):
            date = values['date_in']
        if reg and values.get('operator_id', False):
            op_obj = reg.create_operator_line(values['operator_id'], date)
            res = {'operator_line_id': op_obj.id}
        return res

    @api.model
    def log_out_operator(self, values):
        res = {}
        reg = False
        if values.get('registry_id', False):
            reg = self.browse(values['registry_id'])
        date = fields.Datetime.now()
        if values.get('date_out', False):
            date = values['date_out']
        operator_line_id = values.get('operator_line_id', False)
        if reg and operator_line_id:
                self.env['operator.line'].browse(operator_line_id).write({
                    'date_out': date})
        return res


class QualityCheckLine(models.Model):
    _name = 'quality.check.line'

    registry_id = fields.Many2one('app.registry', 'Registry', readonly=True)
    pqc_id = fields.Many2one('product.quality.check', 'Quality Check',
                             readonly=False)
    date = fields.Datetime('Date', readonly=False)
    value = fields.Text('Value', readonly=False)
    operator_id = fields.Many2one('hr.employee', 'Operator')
    wc_line_id = fields.Many2one('mrp.production.workcenter.line', 
                                 'Workcenter Line', readonly=True)


class StopLines(models.Model):
    _name = 'stop.line'

    registry_id = fields.Many2one('app.registry', 'Registry', readonly=True)
    reason_id = fields.Many2one('stop.reason', 'Reason')
    stop_start = fields.Datetime('Stop Start', readonly=False)
    stop_end = fields.Datetime('Stop End', readonly=False)
    stop_duration = fields.Float('Stop Duration',
                                 compute="_get_duration")
    operator_id = fields.Many2one('hr.employee', 'Operator')

    @api.multi
    @api.depends('stop_start', 'stop_end')
    def _get_duration(self):
        for r in self:
            if r.stop_start and r.stop_end:
                stop_start = fields.Datetime.from_string(r.stop_start)
                stop_end = fields.Datetime.from_string(r.stop_end)
                td = stop_end - stop_start
                r.stop_duration = td.total_seconds() / 3600


class OperatorLines(models.Model):
    _name = 'operator.line'

    registry_id = fields.Many2one('app.registry', 'Registry', readonly=True)
    operator_id = fields.Many2one('hr.employee', 'Operator')
    date_in = fields.Datetime('Date Int', readonly=False)
    date_out = fields.Datetime('Date Out', readonly=False)
    stop_duration = fields.Float('Hours',
                                 compute="_get_duration")
    wc_line_id = fields.Many2one('mrp.production.workcenter.line', 
                                 'Workcenter Line', readonly=True)

    @api.multi
    @api.depends('date_in', 'date_out')
    def _get_duration(self):
        for r in self:
            if r.date_in and r.date_out:
                date_in = fields.Datetime.from_string(r.date_in)
                date_out = fields.Datetime.from_string(r.date_out)
                td = date_out - date_in
                r.stop_duration = td.total_seconds() / 3600
