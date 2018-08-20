# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError

INDEX_SELECTION = [('inc','Inc'), ('dec','Dec'), ('both', 'Both')]
INDEX_ROTATION = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]


class StockLocationRack(models.Model):

    _name = "stock.location.rack"
    _order = 'sequence, name'

    name = fields.Char('Name', required=1)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    code = fields.Char('Code', required=1)
    sequence = fields.Integer('Sequence', default=0)
    x_number = fields.Integer('Pos X', required=1)
    y_number = fields.Integer('Pos Y count', required=1)
    z_number = fields.Integer('Pos Z count', required=1)
    index = fields.Selection(INDEX_SELECTION, 'Index pos')
    parent_id = fields.Many2one('stock.location', string="Parent location", required=1)
    rotation = fields.Selection(INDEX_ROTATION, 'Rotation', default='medium')
    need_check = fields.Boolean("Need check", default=True, help="Need check in PDA")


    @api.multi
    def update_rack_loc_ids(self):

        for rack in self:
            usage = self.parent_id.usage
            loc_order = str(rack.sequence).zfill(3)
            for y in range(1, rack.y_number+1):
                for z in range(1, rack.z_number+1):
                    for x in range(1, rack.x_number+1):
                        pos_x = str(rack.x_number)
                        pos_y = str(y).zfill(2)
                        pos_z = str(z).zfill(2)
                        order_z = rack.z_number - z
                        if rack.index=='inc':
                            order_y = y - 1
                            order_y2 = False
                        elif rack.index == 'dec':
                            order_y = rack.y_number - y
                            order_y2 = False
                        else:
                            order_y = y
                            order_y2 = rack.y_number - y
                        picking_order_dec = ''
                        picking_order = int('{}{}{}'.format(loc_order, str(order_y).zfill(2), str(order_z).zfill(2)))
                        if order_y2:
                            picking_order_dec = int('{}{}{}'.format(loc_order, str(order_y2).zfill(2), str(order_z).zfill(2)))

                        name = "{} / {}.{}.{}".format(rack.name, pos_x, pos_y, pos_z)
                        loc_barcode = "{}.{}.{}.{}".format(rack.code, pos_x, pos_y, pos_z)

                        vals = {'name': name,
                                'warehouse_id': rack.warehouse_id.id,
                                'location_id': rack.parent_id.id,
                                'usage': usage,
                                'posx': x,
                                'posy': y,
                                'posz': z,
                                'loc_barcode': loc_barcode,
                                'picking_order': picking_order,
                                'picking_order_dec': picking_order_dec,
                                'rotation': rack.rotation,
                                'rack_id': rack.id,
                                'in_pack': rack.in_pack,
                                'need_check': rack.need_check,
                                'company_id': False}
                        domain_location = [('loc_barcode','=', loc_barcode), ('warehouse_id', '=', rack.warehouse_id.id)]
                        location = self.env['stock.location'].search(domain_location)
                        if location:
                            location.write(vals)
                        else:
                            self.env['stock.location'].create(vals)

class StockLocation (models.Model):

    _inherit = 'stock.location'


    picking_order = fields.Integer('Picking order')
    picking_order_dec = fields.Integer('Picking order (two side location)')
    rack_id = fields.Many2one('stock.location.rack')
    warehouse_id = fields.Many2one('stock.warehouse')
    rotation = fields.Selection(INDEX_ROTATION, 'Rotation')
    in_pack = fields.Boolean('Must be in pack', default=False, help = "If checked, al quants in this location be in pack, so  ops and moves must have result_package_id")
    need_check = fields.Boolean("Need check", default=False, help="Need check in ")
    rack_name = fields.Char(related='rack_id.name')
    pda_name = fields.Char("PDA name")

    @api.model
    def name_to_id(self, name):
        location = self.search([('loc_barcode', '=', name)], limit=1)
        return location and location.id or False

    @api.multi
    def print_barcode_tag_report(self):
        self.ensure_one()
        custom_data = {
            'location_id': self.id,
        }
        rep_name = 'warehouse_app.location_tag_report'
        rep_action = self.env["report"].get_action(self, rep_name)
        rep_action['data'] = custom_data
        return rep_action

    @api.model
    def get_barcode_id(self, vals):
        barcode = vals.get('barcode', False)
        if barcode:
            domain=[('loc_barcode', '=', barcode)]
            location_id = self.search_read(domain, ['id'], limit=1)
            if location_id:
                id = location_id[0]
            return id
        return False

    @api.model
    def get_pda_info(self, vals):
        print vals
        id = vals.get('id', False)
        type = vals.get('type', 'stock') ##stock, lot, package
        limit = vals.get('limit', 5)
        offset = vals.get('offset', 0)
        last = vals.get('last', False)
        if not id:
            return False
        location_id = self.browse([vals.get('id', False)])
        fields = ['id', 'name', 'usage', 'rotation', 'need_check','in_pack', 'rack_name', 'loc_barcode', 'picking_order']
        location = {}
        vals = {}
        for field in fields:
            location[field] = location_id[field]
        location['rack_name'] = location_id.rack_id.name
        if location['usage']=='customer':
            location['count'] = 0
            location['offset'] = 0
            info = {'location': location, 'stock': []}
            return info

        if type == "stock":
            fields = u'count(sq.id), min(sq.id), ' \
                     u'sq.product_id as pp_id, ' \
                     u'pp.default_code, ' \
                     u'pp.name_template as product_id, ' \
                     u'spl.id as lot_id, ' \
                     u'spl.name as lot_name, ' \
                     u'sqp.id as package_id, ' \
                     u'sqp.name as package_name, ' \
                     u'sum(qty) as qty, ' \
                     u'pu.id as uom_id, ' \
                     u'pu.name as uom_name'
            _from = u' from stock_quant sq ' \
                    u'join product_product pp on pp.id = sq.product_id ' \
                    u'join product_template pt on pt.id = pp.product_tmpl_id ' \
                    u'join product_uom pu on pu.id = pt.uom_id ' \
                    u'left join stock_production_lot spl on spl.id = sq.lot_id ' \
                    u'left join stock_quant_package sqp on sqp.id = sq.package_id '
            _where = u'where sq.location_id = %s'%id
            _group = u'group by sq.product_id, ' \
                     u'pp.id, sq.lot_id, sq.package_id, ' \
                     u'spl.name, sqp.name, spl.id, sqp.id, pu.id, pu.name' \
                     u' order by pp.id '


            if last:
                fields2 = u'count (sq.id) '
                sql2 = u"select %s" % fields2
                sql2 = u'%s %s' % (sql2, _from)
                sql2 = u'%s %s' % (sql2, _where)
                sql2 = u'%s %s' % (sql2, _group)
                self._cr.execute(sql2)
                count_all = len(self._cr.fetchall())
                offset = max(0, count_all - limit)




            sql = u"select %s"%fields
            sql = u'%s %s'%(sql, _from)
            sql = u'%s %s' % (sql, _where)
            sql = u'%s %s' % (sql, _group)

            _limit = u' limit %s offset %s'%(limit, offset)
            sql = u'%s %s' % (sql, _limit)
            self._cr.execute(sql)


            res_all = list(self._cr.fetchall())
            res = []
            for val in res_all:
                vals = {
                    #'pp_id': val[2],
                    'default_code': val[3] or '',
                    'product_id': val[4] or '',
                    #'lot_id': val[5],
                    'lot_name': val[6] or '',
                    #'package_id': val[7],
                    'package_name': val[8] or '',
                    'qty': val[9],
                    'uom_name': val[11]
                }
                res.append(vals)

        elif type == "lot":

            domain = [('location_id','=', id)]

            sql = "select lot_id from stock_quant where location_id=%s and not lot_id isnull group by lot_id order by lot_id"%id
            if last:
                self._cr.execute(sql)
                res_all = self._cr.fetchall()
                offset = max(len(all) - limit, 0)
            sql = "%s limit %s offset %s"%(sql, limit, offset)
            self._cr.execute(sql)
            res_all = self._cr.fetchall()
            lot_ids = self.env['stock.production.lot'].browse([row[0] for row in res_all]) #search([('id', 'in', res_all)], limit=limit, offset=offset)
            res = []
            for lot in lot_ids:
                #q_ids = lot.quant_ids.filtered(lambda x: x.location_id == location_id)
                #package_ids = q_ids.filtered(lambda x:x.package_id).mapped('package_id')

                vals = {
                    #'pp_id': lot.product_id and lot.product_id.id,
                    'default_code': lot.product_id and lot.product_id.default_code or '',
                    'product_id': lot.product_id and lot.product_id.name_template,
                    #'lot_id': lot.id,
                    'lot_name': lot.name,
                    #'package_id': package_ids[0].id if len(package_ids)==1 else False,
                    'package_name': '',# package_ids[0].name if len(package_ids)==1 else package_ids.mapped('name') or '',
                    'qty': lot.qty_available,
                    'uom_name': lot.product_id and lot.product_id.uom_id.name
                }
                res.append(vals)
        elif type == "package":
            domain = [('location_id', '=', id)]
            if last:
                all = self.env['stock.quant.package'].search_read(domain, ['id'], order='name asc')
                offset = max(len(all) - limit, 0)

            package_ids = self.env['stock.quant.package'].search(domain, order='name asc', limit=limit, offset=offset)
            res = []
            for lot in package_ids:
                vals = {
                    #'pp_id': lot.product_id and lot.product_id.id,
                    'default_code': lot.product_id and lot.product_id.default_code or '',
                    'product_id': lot.product_id and lot.product_id.name_template,
                    #'lot_id': lot.lot_id and lot.lot_id.id,
                    'lot_name': lot.lot_id and lot.lot_id.name or '',
                    #'package_id':lot.id,
                    'package_name': lot.name,
                    'qty': lot.package_qty,
                    'uom_name': lot.product_id and lot.product_id.uom_id.name
                }
                res.append(vals)

        location['count'] = len(res)
        location['offset'] = offset
        info = {'location': location, 'stock': res}
        return info


    def get_first_parent_view(self, location_id):
        parent = self.browse(location_id)
        while parent and parent.usage != 'view':
            parent = parent.location_id
        return parent and parent.id

