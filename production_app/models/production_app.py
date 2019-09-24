# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields, _
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
from openerp import exceptions


APP_STATES = [
    ('waiting', 'Waiting'),
    ('confirmed', 'Confirmed'),
    ('setup', 'Set-Up'),
    ('started', 'Started'),
    ('stopped', 'Stopped'),
    ('cleaning', 'Cleaning'),
    ('finished', 'Finished'),
    ('validated', 'Validated')
]

PRODUCTION_STATES = [
    ('draft', 'New'),
    ('confirmed', 'Waiting Goods'),
    ('ready', 'Ready to Produce'),
    ('in_production', 'Production Started'),
    ('finished', 'Finished'),
    ('validated', 'Validated'),
    ('closed', 'Closed'),
    ('cancel', 'Cancelled'),
    ('done','Done')
]

class ProductionAppRegistry(models.Model):
    _name = 'production.app.registry'
    _order = 'id desc'

    wc_line_id = fields.Many2one(
        'mrp.production.workcenter.line', 'Work Order', readonly=True)
    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Work Center', readonly=False)
    state = fields.Selection(APP_STATES, 'State',
        default='waiting', readonly=True)
    setup_start = fields.Datetime('Setup Start')
    setup_end = fields.Datetime('Setup End')
    setup_duration = fields.Float('Setup Duration',
        compute='_get_durations')
    production_start = fields.Datetime('Production Start')
    production_end = fields.Datetime('Production End')
    production_duration = fields.Float('Production Duration',
        compute='_get_durations')
    cleaning_start = fields.Datetime('Cleaning Start')
    cleaning_end = fields.Datetime('Cleaning End')
    cleaning_duration = fields.Float('Cleaning Duration',
        compute='_get_durations')
    qc_line_ids = fields.One2many(
        'quality.check.line', 'registry_id', 'Quality Checks',
        readonly=False)
    stop_line_ids = fields.One2many(
        'stop.line', 'registry_id', 'Production Stops',
        readonly=False)
    operator_ids = fields.One2many(
        'operator.line', 'registry_id', 'Operators',
        readonly=False)
    qty = fields.Float('Quantity', readonly=False,
        states={'validated': [('readonly', True)]})
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot', readonly=True)
    line_scheduled_ids = fields.One2many(
        'consumption.line', 'registry_id', 'Scheduled Products',
        domain=[('type', '=', 'scheduled')], readonly=False)
    line_in_ids = fields.One2many(
        'consumption.line', 'registry_id', 'Incomings',
        domain=[('type', '=', 'in')], readonly=False)
    line_out_ids = fields.One2many(
        'consumption.line', 'registry_id', 'Outgoings',
        domain=[('type', '=', 'out')], readonly=False)
    line_scrapped_ids = fields.One2many(
        'consumption.line', 'registry_id', 'Scrapped',
        domain=[('type', '=', 'scrapped')], readonly=False)
    line_finished_ids = fields.One2many(
        'consumption.line', 'registry_id', 'Finished Products',
        domain=[('type', '=', 'finished')], readonly=False)
    consumptions_done = fields.Boolean('Consumptions Done')
    # RELATED FIELDS
    name = fields.Char('Workcenter Line',
        related="wc_line_id.name", readonly=True)
    production_id = fields.Many2one(
        'mrp.production', 'Production',
        related="wc_line_id.production_id", readonly=True)
    product_id = fields.Many2one(
        'product.product', 'Product',
        related="production_id.product_id", readonly=True)
    production_state = fields.Selection(PRODUCTION_STATES, 'Production Status',
        related='production_id.state', readonly=True)
    workorder_id = fields.Many2one(
        'work.order', 'Related Maintenance Order')
    note = fields.Text(string='Notes')

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
    def get_next_planned_wc_line(self, workcenter_id):
        if not workcenter_id:
            return False
        domain = [
            ('workcenter_id', '=', workcenter_id),
            ('state', '!=', 'done'),
            ('production_state', 'in', ('ready', 'confirmed', 'in_production')),
             '|',
            ('registry_id', '=', False),
            ('app_state', 'not in', ('finished', 'validated')),
            ('workorder_planned_state', '=', '1'),
        ]
        order = 'sequence ASC, priority DESC, id ASC'
        wcl_obj = self.env['mrp.production.workcenter.line']
        wcl_id = wcl_obj.search(domain, order=order, limit=1)
        return wcl_id.id

    @api.model
    def get_registry(self, workcenter_id=None, wc_line_id=None, registry_id=None):
        res = False
        wcl_id = wc_line_id or self.get_next_planned_wc_line(workcenter_id)
        if registry_id:
            domain = [('id', '=', registry_id)]
        elif wcl_id:
            domain = [('wc_line_id', '=', wcl_id)]
        else:
            return False
        reg_id = self.search(domain, limit=1)
        if not reg_id and not registry_id:
            reg_id = self.create_new_registry(wcl_id)
        if reg_id:
            res = reg_id
        return res

    @api.model
    def create_new_registry(self, wc_line_id):
        wcl_obj = self.env['mrp.production.workcenter.line']
        wcl_id = wcl_obj.browse(wc_line_id)
        if not wcl_id:
            return False
        # Scheduled products
        scheduled_vals = []
        for product_line in wcl_id.production_id.product_lines:
            vals = {
                'product_id': product_line.product_id.id,
                'product_uom': product_line.product_uom.id,
                'product_qty': product_line.product_qty,
                'location_id': wcl_id.production_id.location_src_id.id,
                'type': 'scheduled',
            }
            scheduled_vals.append((0, 0, vals))
        vals = {
            'workcenter_id': wcl_id.workcenter_id.id,
            'wc_line_id': wcl_id.id,
            'line_scheduled_ids': scheduled_vals or False,
        }
        res = self.create(vals)
        wcl_id.write({'registry_id': res.id})
        return res

    @api.multi
    def get_allowed_operators(self):
        self.ensure_one()
        res = []
        mrp_workcenter = self.env['mrp.workcenter']
        operators_ids = mrp_workcenter.search([]).mapped('operators_ids')
        department_ids = operators_ids.mapped('department_id')
        domain = [
            ('fecha_baja_empresa', '=', False),
            '|',
            ('department_id', 'in', department_ids.ids),
            ('id', 'in', operators_ids.ids)
        ]
        operators = self.env['hr.employee'].search(domain)
        # Buscamos el operario activo
        active_op_id = False
        op_line_ids = self.operator_ids.filtered(
            lambda r: (
                not r.date_out and
                r.operator_id in self.workcenter_id.operators_ids
            )
        )
        # Si hay quality checks nos quedamos con el operario que haya validado alguno
        op_qc_ids = self.qc_line_ids.mapped('operator_id')
        for op_qc_id in op_qc_ids:
            if op_qc_id in op_line_ids.mapped('operator_id'):
                active_op_id = op_qc_id.id
        # Si no hemos encontrado ninguno elegimos el primero de los logueados
        if not active_op_id:
            active_op_id = op_line_ids and op_line_ids[0].operator_id.id or False
        # Creamos la lista de operadores permitidos
        for op in operators:
            op_line_ids = self.operator_ids.filtered(
                lambda r: not r.date_out and r.operator_id == op)
            op_line_id = op_line_ids and op_line_ids[0].id or False
            let_active = op.id in self.workcenter_id.operators_ids.ids
            active = (active_op_id == op.id)
            vals = {
                'id': op.id,
                'name': op.name,
                'let_active': let_active,
                'operator_line_id': op_line_id,
                'active': active,
                'log': op_line_id and 'in' or 'out',
            }
            res.append(vals)
        return res

    @api.model
    def app_get_registry(self, vals):
        """
        Obtiene el registro que actua de controlador
        para las órdenes de trabajo
        """
        res = {}
        workcenter_id = vals.get('workcenter_id')
        wc_line_id = False

        if vals.get('workline_id', False):  # Alimentator mode only
            wc_line_id = vals.get('workline_id')

        reg = self.get_registry(workcenter_id, wc_line_id)
        if reg:
            res.update(reg.read()[0])

            allowed_operators = reg.get_allowed_operators()

            use_time = reg.production_id.product_id.use_time
            use_date = (datetime.now() + timedelta(use_time + 31))
            use_date = datetime(year=use_date.year, month=use_date.month, day=1)
            use_date = (use_date - timedelta(days=1)).strftime("%Y-%m-%d")

            uom_id = reg.product_id.uom_id
            uos_id = reg.product_id.uos_id
            uos_coeff = reg.product_id.uos_coeff
            change_lot_qc_id = self.env.ref('production_app.change_lot_qc').id

            product_ids = [reg.product_id.id]
            consume_ids1 = reg.line_in_ids.mapped('product_id')
            consume_ids2 = reg.line_out_ids.mapped('product_id')
            consume_ids3 = reg.line_scheduled_ids.mapped('product_id')
            consume_ids = list(set(consume_ids1.ids + consume_ids2.ids + consume_ids3.ids))
            production_qty = reg.production_id.product_qty
            production_uos_qty = reg.production_id.product_uos_qty
            bom_app_notes = reg.production_id.bom_id.app_notes or ''
            process_type = reg.production_id.workcenter_lines.filtered(
                lambda r: r.workcenter_id.process_type).mapped('workcenter_id.process_type')
            if 'toasted' in process_type and 'fried' in process_type:
                process_type = False
            elif 'toasted' in process_type: # Proceso prioritario
                process_type = u'toasted'
            elif 'fried' in process_type: # Proceso prioritario
                process_type = u'fried'
            else:
                process_type = process_type and process_type[0] or False
            res.update(
                allowed_operators=allowed_operators,
                product_use_date=use_date,
                change_lot_qc_id=change_lot_qc_id,
                product_ids=product_ids,
                consume_ids=consume_ids,
                production_qty=production_qty,
                production_uos_qty=production_uos_qty,
                workline_name=vals.get('workline_name', '') or '',
                uom=uom_id.name, uos=uos_id.name, uos_coeff=uos_coeff,
                uom_id=uom_id.id, uos_id=uos_id.id,
                location_src_id=reg.production_id.location_src_id.id,
                location_dest_id=reg.production_id.location_dest_id.id,
                bom_app_notes=bom_app_notes,
                process_type=process_type,
            )
        return res

    @api.model
    def confirm_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            reg.write({
                'state': 'confirmed',
            })
            res = reg.read()[0]
        return res

    @api.model
    def setup_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
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
        lot_name = lot_name if lot_name else 'input error from app'
        if product_id:
            domain = [
                ('name', '=', lot_name),
                ('product_id', '=', product_id)
            ]
            lot_obj = spl.search(domain, limit=1)
            if not lot_obj:
                lot_date = values.get('lot_date', '')
                try:
                    lot_date = lot_date[:7] + '-01 02:00:00'
                    lot_date = fields.Datetime.from_string(lot_date)
                    lot_date = (lot_date + timedelta(31))
                    lot_date = datetime(year=lot_date.year, month=lot_date.month, day=1, hour=2)
                    lot_date = (lot_date - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    lot_date = False
                lot_date = lot_date if lot_date else False
                vals = {
                    'name': lot_name,
                    'product_id': product_id,
                    'use_date': lot_date
                }
                lot_obj = spl.create(vals)
            lot_id = lot_obj.id
        return lot_id

    @api.model
    def get_available_lot(self, vals):
        product_ids = vals.get('product_ids', [])
        if len(product_ids) == 0:
            return False
        if len(product_ids) == 1:
            product_ids = '(' + str(product_ids[0]) + ')'
        else:
            product_ids = str(tuple(product_ids))
        sql = "select spl.id, spl.name, spl.use_date, pp.id as product_id, sl.id as location_id, sum(sq.qty) as qty_available " \
              "from stock_quant sq " \
              "join stock_production_lot spl on spl.id = sq.lot_id " \
              "join stock_location sl on sl.id = sq.location_id " \
              "join product_product pp on pp.id = sq.product_id " \
              "where sl.usage = 'internal' and pp.id in %s and spl.locked_lot = False " \
              "group by spl.id, pp.id, sl.id " \
              "having sum(sq.qty) > 0.00 " \
              "order by use_date" % (product_ids)
        self._cr.execute(sql)
        records = self._cr.fetchall()
        lots = []
        for lot_id in records:
            vals = {
                'id': lot_id[0] or 0,
                'name': lot_id[1] or '',
                'use_date': lot_id[2] or False,
                'product_id': lot_id[3] or False,
                'location_id': lot_id[4] or False,
                'qty_available': lot_id[5] or False,
            }
            lots.append(vals)
        return lots

    @api.model
    def start_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
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
    def set_consumptions_done(self, values):
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            reg.write({
                'consumptions_done': True,
            })
        return True

    @api.model
    def unset_consumptions_done(self, values):
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            reg.write({
                'consumptions_done': False,
            })
        return True

    @api.model
    def create_maintenance_order(self, reg, reason_id):
        mt = self.env['maintenance.type'].\
            search([('type', '=', 'correctivo')], limit=1)

        note = 'Creado por app.'
        if reason_id:
            reason_name = self.env['stop.reason'].browse(reason_id).name
            note += '\n' + reason_name
        if reg.workcenter_id:
            note += '\n' + u'Centro de producción: ' + reg.workcenter_id.name
        if reg.production_id:
            note += '\n' + u'Orden de producción: ' + reg.production_id.name
        wo = self.env['work.order'].create({'maintenance_type_id': mt.id,
                                            'note': note})
        reg.write({
            'workorder_id': wo.id,
        })
        return True

    @api.model
    def stop_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            # Si hay paradas sin cerrar, tenemos que finalizarlas antes de iniciar otra.
            domain = [
                ('registry_id', '=', reg.id),
                ('stop_end', '=', False),
            ]
            stop_obj = self.env['stop.line']
            stop_ids = stop_obj.search(domain)
            for stop_id in stop_ids:
                stop_id.write({
                    'stop_end': stop_id.stop_start,
                })
            from_state = reg.state
            if not from_state or from_state == 'stopped':
                from_state = 'setup'
                if reg.setup_end:
                    from_state = 'started'
                if reg.production_end:
                    from_state = 'cleaning'
            operator_id = False
            reason_id = values.get('reason_id', False)
            if values.get('active_operator_id', False):  # Can be 0
                operator_id = values['active_operator_id']
            date = fields.Datetime.now()
            if values.get('stop_start', False):
                date = values['stop_start']
            stop_obj = reg.create_stop(reason_id, operator_id, date, from_state)
            create_mo = values.get('create_mo', False)
            if create_mo:
                self.create_maintenance_order(reg, reason_id)
            reg.write({
                'state': 'stopped',
            })
            res = reg.read()[0]
            res.update({
                'stop_from_state': from_state,
            })
        return res

    @api.model
    def restart_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            date = fields.Datetime.now()
            if values.get('stop_end', False):
                date = values['stop_end']
            domain = [
                ('registry_id', '=', reg.id),
                ('stop_end', '=', False),
            ]
            stop_obj = self.env['stop.line']
            stop_id = stop_obj.search(domain, order='stop_start DESC', limit=1)
            stop_id.write({'stop_end': date})
            # Si hay paradas sin cerrar, tenemos que finalizarlas
            stop_ids = stop_obj.search(domain)
            for stop_id in stop_ids:
                stop_id.write({
                    'stop_end': stop_id.stop_start,
                })
            from_state = stop_id.from_state
            if not from_state or from_state == 'stopped':
                from_state = 'setup'
                if reg.setup_end:
                    from_state = 'started'
                if reg.production_end:
                    from_state = 'cleaning'
            reg.write({
                'state': from_state,
            })
            res = reg.read()[0]
            res.update({
                'stop_from_state': from_state,
            })
        return res

    @api.model
    def restart_and_clean_production(self, values):
        self.restart_production(values)
        res = self.clean_production(values)
        return res

    @api.model
    def clean_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            date = fields.Datetime.now()
            if values.get('cleaning_start', False):
                date = values['cleaning_start']
            reg.write({
                'state': 'cleaning',
                'production_end': date,
                'cleaning_start': date,
            })
            # Si pasamos directamente a limpieza desde una parada cuando estamos en setup
            # los tiempos de setup_end y de production_start no se grabaron.
            if not (reg.setup_end or reg.production_start):
                reg.write({
                    'setup_end': date,
                    'production_start': date,
                })
            res = reg.read()[0]
        return res

    @api.model
    def finish_production(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            date = fields.Datetime.now()
            if values.get('stop_start', False):
                date = values['cleaning_end']
            qty = values.get('qty', 0)
            try:
                qty = float(qty)
            except:
                qty = 0 
            qty = qty >= 0 and qty or 0
            reg.write({
                'state': 'finished',
                'cleaning_end': date,
                'qty': qty,
            })
            operators_logged = self.env['operator.line']
            for op in reg.operator_ids:
                if not op.date_out:
                    operators_logged += op
            if operators_logged:
                operators_logged.write({
                    'date_out': date,
                })
            res = reg.read()[0]
        return res

    @api.model
    def scrap_production(self, values):
        reason_id = values.get('scrap_reason_id', False)
        qty = values.get('scrap_qty', 0)
        try:
            qty = float(qty)
        except:
            qty = 0 
        if qty <= 0:
            return True
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if not reg or not reg.production_id.move_created_ids:
            return True
        domain = [
            '|',
            ('name', 'ilike', 'mermas'),
            ('name', 'ilike', 'losses'),
            ('scrap_location', '=', True),
            ('usage', '!=', 'view'),
        ]
        scrap_location_id = self.env['stock.location'].search(domain, limit=1)
        if not scrap_location_id:
            domain = [
                ('scrap_location', '=', True),
                ('usage', '!=', 'view'),
            ]
            scrap_location_id = self.env['stock.location'].search(domain, limit=1)
        if scrap_location_id:
            lot_id = reg.lot_id.id
            move = reg.production_id.move_created_ids[0]
            scrap_move = move.action_scrap(qty, scrap_location_id.id, restrict_lot_id=lot_id)
            if scrap_move:
                scrap_move = self.env['stock.move'].browse(scrap_move[0])
                scrap_move.write({
                    'reason_id': reason_id,
                })
        return True

    @api.model
    def get_quality_checks(self, values):
        product_id = values.get('product_id', False)
        product = self.env['product.product'].browse(product_id)
        domain = [('id', 'in', product.quality_check_ids.ids)]
        fields = ['id', 'name', 'value_type', 'quality_type', 'repeat',
                  'required_text', 'max_value', 'min_value', 'barcode_type']
        res = product.quality_check_ids.search_read(domain, fields)
        res2 = []
        for dic in res:
            dic.update({'value': ''})
            if dic['value_type'] == 'barcode':
                if dic['barcode_type'] == 'ean13':
                    dic.update({
                        'value_type': 'text',
                        'required_text': product.ean13,
                    })
                if dic['barcode_type'] == 'dun14':
                    dic.update({
                        'value_type': 'text',
                        'required_text': product.dun14,
                    })
            res2.append(dic)
        return res2

    @api.model
    def app_save_quality_checks(self, values):
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if not reg:
            return True
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
                'value': str(dic.get('value', False).encode('utf-8')),
                'operator_id': operator_id
            }
            self.env['quality.check.line'].create(vals)
        return True

    @api.model
    def app_save_consumption_line(self, values):
        """
        Crea, borra o actualiza la línea de consumo del modo alimentador
        """
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if not reg:
            return True
        line = values.get('line', False)
        if not line:
            return True
        consume_line = False
        # CREATE LINE IF NOT EXIST
        if not line.get('id', False):
            vals = {
                'product_id': line['product_id'],
                'product_qty': line['qty'],
                'product_uom': line['uom_id'],
                'location_id': line['location_id'],
                'lot_id': False,
                'type': line.get('type', 'in'),
                'scrap_type': line.get('scrap_type', 'losses'),
                'registry_id': registry_id,
            }
            consume_line = self.env['consumption.line'].create(vals)

        if not consume_line:
            consume_line = self.env['consumption.line'].browse(int(line['id']))
        # REMOVE LINE IF KEY REMOVE
        if line.get('remove', False):
            consume_line.unlink()
            return True

        lot_id = line.get('lot_id', False)
        if line.get('type') == 'finished':
            lot_id = reg.lot_id.id
        consume_line.write({
            'product_qty': line['qty'],
            'lot_id': lot_id,
            'scrap_type': line.get('scrap_type', 'losses'),
        })
        # Las lineas de producto terminado podrian no tener el lote al principio.
        # Se revisan por si es necesario actualizarlas
        for line_finished_id in reg.line_finished_ids:
            if line_finished_id.lot_id != reg.lot_id:
                line_finished_id.write({'lot_id': reg.lot_id.id})
        return True

    @api.model
    def get_merged_consumptions(self, values):
        """
        Devuelve el resultado de los consumos finales (in - out - scrap)
        """
        res = []
        dic = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if not reg:
            return []
        for line in reg.line_in_ids:
            key = (line.product_id.id, line.lot_id.id, line.location_id.id)
            if key in dic:
                dic[key]['product_qty'] += line.product_qty
            else:
                dic[key] = {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'lot_id': line.lot_id.id,
                    'location_id': line.location_id.id,
                    'lot_required': line.lot_required,
                }
        for line in reg.line_out_ids:
            key = (line.product_id.id, line.lot_id.id, line.location_id.id)
            if key in dic:
                dic[key]['product_qty'] -= line.product_qty
            else:
                dic[key] = {
                    'product_id': line.product_id.id,
                    'product_qty': -line.product_qty,
                    'lot_id': line.lot_id.id,
                    'location_id': line.location_id.id,
                    'lot_required': line.lot_required,
                }
        for line in reg.line_scrapped_ids:
            key = (line.product_id.id, line.lot_id.id, line.location_id.id)
            if key in dic:
                dic[key]['product_qty'] -= line.product_qty
            else:
                dic[key] = {
                    'product_id': line.product_id.id,
                    'product_qty': -line.product_qty,
                    'lot_id': line.lot_id.id,
                    'location_id': line.location_id.id,
                    'lot_required': line.lot_required,
                }
        for key in dic:
            if dic[key]['product_qty'] == 0.0:
                continue
            if dic[key]['product_qty'] < 0.0:
                return {'lines': False}
            res.append(dic[key])
        return {'lines': res}

    @api.multi
    def validate(self):
        self.ensure_one()
        if not self.consumptions_done:
            raise exceptions.except_orm(_('Error'),
                _("You cannot validate without confirming consumptions."))
        # Comprobamos que la cantidad sea válida
        if self.qty <= 0.0:
            raise exceptions.except_orm(_('Error'),
                _("You cannot validate if the quantity of production are negative or less than zero."))
        # Comprobamos si coincide la cantidad indicada por alimentador con la cantidad indicada por producción
        qty_feeder = sum([line.product_qty for line in self.line_finished_ids])
        if self.qty != qty_feeder:
            raise exceptions.except_orm(_('Error'),
                _("You cannot validate if the quantity of the feeder and quantity of production are not the same."))
        # Si hay varias órdenes de trabajo para la misma producción verificamos que la cantidad sea igual.
        registry_qtys = self.production_id.workcenter_lines.mapped('registry_id.qty')
        if not all(x == self.qty for x in registry_qtys if x > 0):
            raise exceptions.except_orm(_('Error'),
                _("You cannot validate if the quantity in work orders associated with this production are not the same."))
        # Cambiamos la cantidad a producir de la producción si es distinta de la indicada en el registro de app
        if self.qty != self.production_id.product_qty:
            self.change_production_qty()
        # Añadimos los tiempos de producción y las paradas a la orden de trabajo
        wc_line = self.wc_line_id
        operator_ids = self.operator_ids.mapped('operator_id').ids
        stop_values = []
        for stop in self.stop_line_ids:
            val = {
                'name': stop.operator_id.name,
                'reason': stop.reason_id.name,
                'time': stop.stop_duration,
                'in_production': stop.from_state == 'started',
            }
            stop_values.append((0, 0, val))
        vals = {
            'date_start': self.setup_start,
            'date_finished': self.cleaning_end,
            'real_time': self.production_duration,
            'time_start': self.setup_duration,
            'time_stop': self.cleaning_duration,
            'operators_ids': operator_ids and [(6, 0, operator_ids)] or False,
            'production_stops_ids': stop_values or False,
        }
        wc_line.production_stops_ids.unlink()
        wc_line.write(vals)
        # Añadimos los consumos del alimentador a la orden de producción
        # Si la producción solo tiene una orden de trabajo o se trata de la primera en validar,
        # borramos los consumos previos. En caso contrario los añadimos.
        if self.production_id.state not in ('draft', 'closed', 'done'):
            consumptions = self.get_merged_consumptions({'registry_id': self.id}).get('lines', False)
            if consumptions == False:
                raise exceptions.except_orm(_('Error'),
                    _("You cannot validate because an error occurred when calculating the consumptions."))
            registry_states = self.production_id.workcenter_lines.mapped('registry_id.state')
            if 'validated' not in registry_states:
                to_remove_ids = self.production_id.mapped('move_lines')
                to_remove_ids.action_cancel()
                to_remove_ids.unlink()
            for line in consumptions:
                product_id = self.env['product.product'].browse(line['product_id'])
                if product_id.type != 'service':
                    move_id = self.env['mrp.production']._make_consume_line_from_data(
                        self.production_id, product_id, product_id.uom_id.id, line['product_qty'], False, 0)
                    move_id = self.env['stock.move'].browse(move_id)
                    vals = {
                        'restrict_lot_id': line['lot_id'],
                        'location_id': line['location_id'] or move_id.location_id.id,
                    }
                    move_id.write(vals)
                    move_id.action_confirm()
                    if line['lot_required'] and line['lot_id'] or not line['lot_required']:
                        move_id.action_assign()
                    move_id.force_assign()
        # Establecemos el registro a estado validado
        self.write({'state': 'validated'})

    @api.multi
    def change_production_qty(self):
        for reg in self:
            prod = reg.production_id
            data = {'product_qty': reg.qty}
            if prod.product_uos.id:
                data['product_uos_qty'] = self.env['product.uom']._compute_qty(
                    prod.product_uom.id, reg.qty, prod.product_uos.id)
            prod.write(data)
            if prod.move_prod_id:
                data = {'product_uom_qty': reg.qty}
                if prod.move_prod_id.product_uos.id:
                    data['product_uos_qty'] = self.env['product.uom']._compute_qty(
                        prod.move_prod_id.product_uom.id, reg.qty, prod.move_prod_id.product_uos.id)
                prod.move_prod_id.write(data)
            self.env['change.production.qty']._update_product_to_produce(prod, reg.qty)
            res = self.env['mrp.production']._prepare_lines(prod)
            results = res[0] # product_lines
            results2 = res[1] # workcenter_lines
            # unlink product_lines
            prod.product_lines.unlink()
            # create product_lines in production order
            for line in results:
                line['production_id'] = prod.id
                self.env['mrp.production.product.line'].create(line)
            # update workcenter_lines in production order
            for workcenter_line in prod.workcenter_lines:
                for line in results2:
                    if workcenter_line.name == line['name']:
                        vals = {
                            'cycle': line['cycle'],
                            'hour': line['hour'],
                        }
                        workcenter_line.write(vals)

    @api.multi
    def create_stop(self, reason_id, operator_id, date_stop, from_state):
        self.ensure_one()
        vals = {
            'registry_id': self.id,
            'stop_start': date_stop,
            'reason_id': reason_id,
            'operator_id': operator_id,
            'from_state': from_state,
        }
        res = self.env['stop.line'].create(vals)
        return res

    @api.model
    def log_in_operator(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        date = fields.Datetime.now()
        if values.get('date_in', False):
            date = values['date_in']
        if reg and values.get('operator_id', False):
            domain = [
                ('registry_id', '=', reg.id),
                ('operator_id', '=', values['operator_id']),
                ('date_out', '=', False),
            ]
            op_obj = self.env['operator.line']
            op_line_id = op_obj.search(domain, order='date_in', limit=1)
            if not op_line_id:
                vals = {
                    'registry_id': reg.id,
                    'operator_id': values['operator_id'],
                    'date_in': date,
                }
                op_line_id = op_obj.create(vals)
            res = {'operator_line_id': op_line_id.id}
        return res

    @api.model
    def log_out_operator(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        date = fields.Datetime.now()
        if values.get('date_out', False):
            date = values['date_out']
        operator_line_id = values.get('operator_line_id', False)
        if reg and operator_line_id:
            op_obj = self.env['operator.line']
            vals = {
                'date_out': date,
            }
            op_obj.browse(operator_line_id).write(vals)
        return res

    @api.model
    def save_note(self, values):
        res = {}
        registry_id = values.get('registry_id', False)
        reg = self.get_registry(registry_id=registry_id)
        if reg:
            note = values.get('note', False)
            reg.write({
                'note': note,
            })
            res = reg.read()[0]
        return res

    @api.multi
    def write(self, vals):
        if 'qty' in vals:
            for reg in self:
                old_qty = reg.production_id.product_qty
                new_qty = vals.get('qty') or old_qty
                product_lines = reg.production_id.product_lines
                for line in reg.line_scheduled_ids:
                    product_qty = sum([x.product_qty for x in product_lines
                        if x.product_id == line.product_id])
                    product_qty = new_qty * product_qty / old_qty
                    if product_qty and product_qty != line.product_qty:
                        line.product_qty = product_qty
        return super(ProductionAppRegistry, self).write(vals)


class QualityCheckLine(models.Model):
    _name = 'quality.check.line'

    registry_id = fields.Many2one(
        'production.app.registry', 'App Registry', readonly=True,
        ondelete='cascade')
    pqc_id = fields.Many2one(
        'product.quality.check', 'Quality Check', readonly=False)
    date = fields.Datetime('Date', readonly=False)
    value = fields.Text('Value', readonly=False)
    operator_id = fields.Many2one(
        'hr.employee', 'Operator')


class StopLine(models.Model):
    _name = 'stop.line'

    registry_id = fields.Many2one(
        'production.app.registry', 'App Registry', readonly=True,
        ondelete='cascade')
    reason_id = fields.Many2one(
        'stop.reason', 'Reason')
    stop_start = fields.Datetime('Stop Start', readonly=False)
    stop_end = fields.Datetime('Stop End', readonly=False)
    stop_duration = fields.Float('Stop Duration',
        compute='_get_duration')
    operator_id = fields.Many2one('hr.employee', 'Operator')
    from_state = fields.Selection(APP_STATES, 'From State',
        default='started', required=True)

    @api.multi
    @api.depends('stop_start', 'stop_end')
    def _get_duration(self):
        for r in self:
            if r.stop_start and r.stop_end:
                stop_start = fields.Datetime.from_string(r.stop_start)
                stop_end = fields.Datetime.from_string(r.stop_end)
                td = stop_end - stop_start
                r.stop_duration = td.total_seconds() / 3600


class OperatorLine(models.Model):
    _name = 'operator.line'

    registry_id = fields.Many2one(
        'production.app.registry', 'App Registry', readonly=True,
        ondelete='cascade')
    operator_id = fields.Many2one(
        'hr.employee', 'Operator')
    date_in = fields.Datetime('Date In', readonly=False)
    date_out = fields.Datetime('Date Out', readonly=False)
    stop_duration = fields.Float('Hours',
        compute='_get_duration')

    @api.multi
    @api.depends('date_in', 'date_out')
    def _get_duration(self):
        for r in self:
            if r.date_in and r.date_out:
                date_in = fields.Datetime.from_string(r.date_in)
                date_out = fields.Datetime.from_string(r.date_out)
                td = date_out - date_in
                r.stop_duration = td.total_seconds() / 3600


class ConsumptionLine(models.Model):
    _name = 'consumption.line'

    @api.model
    def _default_type(self):
        return self._context.get('consumption_type', False)

    @api.model
    def _default_location(self):
        prod_obj = self.env['mrp.production']
        prod = prod_obj.browse(self._context.get('production_id', False))
        location_id = prod.location_src_id.id or prod_obj._src_id_default()
        if self._context.get('consumption_type', False) == 'finished':
            location_id = prod.location_dest_id.id or prod_obj._dest_id_default()
        return location_id

    registry_id = fields.Many2one(
        'production.app.registry', 'App Registry', readonly=True,
        ondelete='cascade')
    type = fields.Selection([
        ('in', 'In'),
        ('out', 'Out'),
        ('scheduled', 'Scheduled'),
        ('finished', 'Finished'),
        ('scrapped', 'Scrapped'),
        ], string='Type', required=True,
        default=_default_type)
    product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    product_qty = fields.Float('Product Quantity',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        required=True)
    qty_to_compare = fields.Float('Quantity to compare',
        digits_compute=dp.get_precision('Product Unit of Measure'),
        compute='_get_qty_to_compare')
    product_uom = fields.Many2one(
        'product.uom', 'UoM', required=True)
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot', required=False)
    lot_required = fields.Boolean('Lot Required',
        compute='_get_lot_required')
    location_id = fields.Many2one(
        'stock.location', 'Location', required=True,
        default=_default_location)
    scrap_type = fields.Selection([
        ('scrap', 'Scrap'),
        ('losses', 'Losses'),
        ], string='Scrap Type')

    @api.multi
    def _get_qty_to_compare(self):
        for line in self:
            qty_to_compare = 0.0
            line_in_ids = line.registry_id.line_in_ids.filtered(
                lambda r: (
                    r.product_id == line.product_id and
                    r.location_id == line.location_id
                )
            )
            line_out_ids = line.registry_id.line_out_ids.filtered(
                lambda r: (
                    r.product_id == line.product_id and
                    r.location_id == line.location_id
                )
            )
            line_scrapped_ids = line.registry_id.line_scrapped_ids.filtered(
                lambda r: (
                    r.product_id == line.product_id and
                    r.location_id == line.location_id
                )
            )
            for line_in_id in line_in_ids:
                qty_to_compare += line_in_id.product_qty
            for line_out_id in line_out_ids:
                qty_to_compare -= line_out_id.product_qty
            for line_scrapped_id in line_scrapped_ids:
                qty_to_compare -= line_scrapped_id.product_qty
            line.qty_to_compare = qty_to_compare

    @api.multi
    def _get_lot_required(self):
        for line in self:
            line.lot_required = \
                line.product_id.track_all or line.product_id.track_production

    @api.onchange('product_id', 'product_uom')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id

