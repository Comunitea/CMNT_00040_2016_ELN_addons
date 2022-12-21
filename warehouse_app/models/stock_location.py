# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields


INDEX_SELECTION = [
    ('inc','Inc'), ('dec','Dec'), ('both', 'Both')
]


class StockLocation (models.Model):
    _inherit = 'stock.location'

    picking_order = fields.Integer('Picking order')
    picking_order_dec = fields.Integer('Picking order (two side location)')
    warehouse_id = fields.Many2one('stock.warehouse')
    need_check = fields.Boolean("Need check", default=False, help="Need check in ")
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
        id = vals.get('id', False)
        type = vals.get('type', 'stock') #stock, lot
        limit = vals.get('limit', 5)
        offset = vals.get('offset', 0)
        last = vals.get('last', False)
        if not id:
            return False
        location_id = self.browse([vals.get('id', False)])
        fields = ['id', 'name', 'usage', 'need_check','in_pack', 'loc_barcode', 'picking_order']
        location = {}
        vals = {}
        for field in fields:
            location[field] = location_id[field]
        if location['usage']=='customer':
            location['count'] = 0
            location['offset'] = 0
            info = {'location': location, 'stock': []}
            return info

        if type == "stock":
            fields = u'count(sq.id), ' \
                     u'min(sq.id), ' \
                     u'sq.product_id as pp_id, ' \
                     u'pp.default_code, ' \
                     u'pp.name_template as product_id, ' \
                     u'spl.id as lot_id, ' \
                     u'spl.name as lot_name, ' \
                     u'sum(qty) as qty, ' \
                     u'pu.id as uom_id, ' \
                     u'pu.name as uom_name '
            _from =  u'from stock_quant sq ' \
                     u'join product_product pp on pp.id = sq.product_id ' \
                     u'join product_template pt on pt.id = pp.product_tmpl_id ' \
                     u'join product_uom pu on pu.id = pt.uom_id ' \
                     u'left join stock_production_lot spl on spl.id = sq.lot_id '
            _where = u'where sq.location_id = %s ' % id
            _group = u'group by sq.product_id, ' \
                     u'pp.id, sq.lot_id, ' \
                     u'spl.name, spl.id,  pu.id, pu.name ' \
                     u'order by pp.id '
            if last:
                fields2 = u'count (sq.id) '
                sql2 = u"select %s" % fields2
                sql2 = u'%s %s' % (sql2, _from)
                sql2 = u'%s %s' % (sql2, _where)
                sql2 = u'%s %s' % (sql2, _group)
                self._cr.execute(sql2)
                count_all = len(self._cr.fetchall())
                offset = max(0, count_all - limit)

            sql = u'select %s' % fields
            sql = u'%s %s' % (sql, _from)
            sql = u'%s %s' % (sql, _where)
            sql = u'%s %s' % (sql, _group)

            _limit = u' limit %s offset %s' % (limit, offset)
            sql = u'%s %s' % (sql, _limit)
            self._cr.execute(sql)

            res_all = list(self._cr.fetchall())
            res = []
            for val in res_all:
                vals = {
                    'default_code': val[3] or '',
                    'product_id': val[4] or '',
                    'lot_name': val[6] or '',
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
                vals = {
                    'default_code': lot.product_id and lot.product_id.default_code or '',
                    'product_id': lot.product_id and lot.product_id.name_template,
                    'lot_name': lot.name,
                    'qty': lot.qty_available,
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

