# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError


SEARCH_OPTIONS= {'stock.quant.package':'name',
                 'stock.production.lot': 'name',
                 'stock.location': 'loc_barcode',
                 'product.product': 'ean13'}

FIELD_NAME = {'stock.quant.package':'name',
        'stock.production.lot': 'name',
        'stock.location': 'loc_barcode',
        'product.product': 'display_name',


        }

FIELDS = {'stock.quant.package': ['id', 'name', 'lot_id', 'lot_id_name', 'location_id', 'location_id_name', 'package_qty', 'multi', 'product_id', 'product_id_name', 'uom'],
          'stock.production.lot': ['id', 'name', 'product_id', 'product_id_name', 'use_date', 'life_date', 'location_id'],
          'stock.location': ['id', 'name', 'usage', 'loc_barcode'],
          'product.product': ['id', 'name', 'ean13', 'default_code', 'default_stock_location_id', 'default_stock_location_id_name']}


class WarehouseApp (models.Model):

    _name = 'warehouse.app'

    @api.model
    def get_app_fields(self, id):

        object_id = self.browse(id)
        fields = {}
        if object_id:
            for field in fields:
                fields[field] = object_id[field]
        return fields


    @api.model
    def get_object_id(self, vals):
        #import ipdb; ipdb.set_trace()
        print "Recibo %s"%vals
        res = {}
        model = vals.get('model', False)
        return_object = vals.get('return_object', False)
        field_value = {}
        default_domain = vals.get('domain', False)
        if not model:
            search_options = SEARCH_OPTIONS.keys()
        elif model == ['stock.qty']:
            qty = vals.get('qty')
            try:
                qty = float(qty.replace(',','.')) or 0.00
            except:
                qty = 0.00
            res = {'model': 'stock.qty', 'id': 0, 'name': qty}
        else:
            search_options = list(set(SEARCH_OPTIONS.keys()) & set(model))
            search_str = vals.get('search_str')
            if search_str:
                search_options = list(set(SEARCH_OPTIONS.keys()) & set(model))
                for option in search_options:
                    model = option
                    domain = [(SEARCH_OPTIONS[option], '=', search_str)]
                    if default_domain:
                        domain += default_domain
                    object_id = self.env[model].search(domain, limit=1)
                    if object_id:
                        break
            else:
                id = vals.get('id', False)
                if id:
                    object_id = self.env[model].browse(id)
                    print model, id, object_id
            if object_id:
                res = {'model': model, 'id': object_id.id, 'name': FIELD_NAME[model]}
                if return_object:
                    for field in FIELDS[model]:
                        if field[-3:] == '_id':
                            field_value[field] = object_id[field]['id']
                        elif field[-5:] == '_name':
                            field_value[field] = object_id[field[:-5]]['name']
                        else:
                            field_value[field] = object_id[field]
                    res['fields'] = field_value
            else:
                res = {'model': model, 'id': 0, 'name': FIELD_NAME[model], 'message': 'No se ha encontrado un %s para %s'%(model, search_str)}

        print "Retorno %s"%res
        return res

