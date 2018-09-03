# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields



class ProductionApp (models.Model):
    _name = 'production.app'

    @api.model
    def get_available_lot(self, vals):
        product_ids = vals.get('product_ids', [])
        if len(product_ids) == 0:
            return False
        if len(product_ids) == 1:
            product_ids = '(' + str(product_ids[0]) + ')'
        else:
            product_ids = str(tuple(product_ids))
        sql = "select spl.id, spl.name, spl.use_date, pp.id as product_id, sum(sq.qty) as qty_available " \
              "from stock_quant sq " \
              "join stock_production_lot spl on spl.id = sq.lot_id " \
              "join stock_location sl on sl.id = sq.location_id " \
              "join product_product pp on pp.id = sq.product_id " \
              "where sl.usage = 'internal' and pp.id in %s " \
              "group by spl.id, pp.id " \
              "having sum(sq.qty) > 0.00 " \
              "order by use_date" % (product_ids)
        self._cr.execute(sql)
        records = self._cr.fetchall()
        lots = []
        for lot_id in records:
            vals = {'id': lot_id[0] or 0,
                    'name': lot_id[1] or '',
                    'use_date': lot_id[2] or False,
                    'product_id': lot_id[3] or False,
                    'qty_available': lot_id[4] or False,
            }
            lots.append(vals)
        return lots

