# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError


SEARCH_OPTIONS = {'stock.quant.package': 'name',
                  'stock.production.lot': 'name',
                  'stock.location': 'loc_barcode',
                  'product.product': 'ean13'}

FIELD_NAME = {'stock.quant.package': 'name',
              'stock.production.lot': 'name',
              'stock.location': 'loc_barcode',
              'product.product': 'display_name'}

FIELDS = {'stock.quant.package': ['id', 'name', 'lot_id', 'lot_id_name', 'location_id', 'location_id_name', 'package_qty', 'multi', 'product_id', 'product_id_name', 'uom'],
          'stock.production.lot': ['id', 'name', 'product_id', 'product_id_name', 'use_date', 'life_date', 'location_id'],
          'stock.location': ['id', 'name', 'usage', 'loc_barcode'],
          'product.product': ['id', 'name', 'ean13', 'default_code', 'default_stock_location_id', 'default_stock_location_id_name', 'track_all']}


INFO_FIELDS = {'stock.quant.package': ['id', 'name', 'lot_id', 'location_id','package_qty', 'multi', 'product_id', 'uom', 'quant_ids', 'children_ids'],
              'stock.production.lot': ['id', 'name', 'product_id', 'use_date', 'removal_date', 'qty_available', 'quant_ids', 'display_name', 'uom_id'],
              'stock.location': ['id', 'name', 'usage', 'loc_barcode'],
              'product.product': ['id', 'display_name', 'name', 'ean13', 'default_code', 'default_stock_location_id', 'track_all', 'uom_id', 'qty_available', 'quant_ids']}

INFO_FIELDS_M2O = {'stock.quant.package': ['id', 'name', 'location_id', 'package_qty', 'multi', 'product_id', 'uom'],
                  'stock.production.lot': ['id', 'name', 'use_date', 'location_id', 'qty_available', 'display_name', 'uom_id'],
                  'stock.location': ['id', 'name', 'usage', 'loc_barcode'],
                  'stock.quant':['id', 'display_name', 'lot_id', 'location_id', 'qty', 'reservation_id', 'in_date'],
                  'product.uom': ['id', 'name'],
                  'product.product': ['id', 'display_name', 'ean13', 'name', 'default_code', 'default_stock_location_id', 'track_all']}

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
    def get_info_object(self, vals):

        model = vals.get('model', False)
        id = vals.get('id', False)
        object_id = self.env[model].browse(id)
        field_value = {}
        if not object_id:
            return False
        for field in INFO_FIELDS[model]:
            #if field=='quant_ids':
            #    import ipdb; ipdb.set_trace()
            if object_id.fields_get(field)[field]['type'] == 'many2one':

                field_value[field] = self.get_m2o_vals(object_id, field)
            elif object_id.fields_get(field)[field]['type'] == 'one2many':
                field_value[field] = self.get_o2m_vals(object_id, field)
            else:
                field_value[field] = object_id[field]
            print "---------%s\n\n\n%s\n\n"%(field, field_value)
        res = {'model': model, 'id': id, 'values': field_value}

        return res


    def get_m2o_vals(self, object_id, field):
         print "-----------%s"%object_id
         import ipdb; ipdb.set_trace()
         if object_id[field]:
             sub_values = {}
             submodel = object_id.fields_get(field)[field]['relation']
             print "-------------------%s"%field
             for sub_field in INFO_FIELDS_M2O[submodel]:
                 print "-------------------%s  >>>  %s" % (field, sub_field)
                 if object_id[field].fields_get(sub_field)[sub_field]['type'] == 'many2one':
                     sub_values[sub_field] = self.get_m2o_val(object_id[field][sub_field])
                 else:
                     sub_values[sub_field] = object_id[field][sub_field]
         else:
             sub_values = False
         return sub_values

    def get_m2o_val(self, val):
        if len(val)>0:
            return {'id': val.id, 'name': val.name}
        else:
            return False

    def get_o2m_vals(self, object_id, field):

        submodel = object_id.fields_get(field)[field]['relation']
        sub_model_id_values = []
        for sub_model_id in object_id[field]:
            sub_values = {}
            for sub_field in INFO_FIELDS_M2O[submodel]:
                if sub_model_id.fields_get(sub_field)[sub_field]['type'] == 'many2one':
                    sub_values[sub_field] = self.get_m2o_val(sub_model_id[sub_field])
                else:
                    sub_values[sub_field] = sub_model_id[sub_field]
            sub_model_id_values.append(sub_values)
        return sub_model_id_values

    @api.model
    def get_object_id(self, vals):
        print "Recibo %s"%vals
        object_id = False
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
            search_str = vals.get('search_str')
            if search_str:
                search_options = list(set(SEARCH_OPTIONS.keys()) & set(model))
                for option in search_options:
                    domain = [(SEARCH_OPTIONS[option], '=', search_str)]
                    if default_domain:
                        domain += default_domain
                    object_id = self.env[option].search(domain, limit=1)
                    if object_id:
                        model = option
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
                res = {'model': SEARCH_OPTIONS.keys(), 'id': 0,  'message': 'No se ha encontrado un objeto para %s'%search_str}

        print "Retorno %s"%res
        return res

