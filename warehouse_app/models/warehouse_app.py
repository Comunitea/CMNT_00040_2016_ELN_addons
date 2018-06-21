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

FIELDS = {'stock.quant.package': ['id', 'name', 'lot_id', 'location_id', 'package_qty', 'multi', 'product_id', 'uom_id'],
          'stock.production.lot': ['id', 'name', 'qty_available', 'product_id','use_date', 'life_date', 'location_id', 'uom_id'],
          'stock.location': ['id', 'name', 'usage', 'loc_barcode'],
          'product.product': ['id', 'name', 'barcean13ode', 'default_code', 'default_stock_location_id', 'track_all']}

DOMAIN = {'stock.production.lot': [('qty_available', '>', 0.00)],
          'stock.quant.package': [],
          'stock.location': [],
          'product.product': []}

INFO_FIELDS = {'stock.quant.package': ['id', 'name', 'lot_id', 'location_id','package_qty', 'multi', 'product_id', 'uom_id', 'quant_ids', 'children_ids'],
              'stock.production.lot': ['id', 'name', 'product_id', 'use_date', 'removal_date', 'qty_available', 'quant_ids', 'display_name', 'uom_id', 'location_id'],
              'stock.location': ['id', 'name', 'usage', 'loc_barcode', 'need_check'],
              'product.product': ['id', 'display_name', 'name', 'ean13', 'default_code', 'default_stock_location_id', 'track_all', 'uom_id', 'qty_available'],
              'stock.picking': ['id', 'name', 'picking_type_id', 'user_id', 'min_date', 'state', 'location_id', 'location_dest_id', 'wave_id', 'remaining_ops', 'pack_operation_count', 'pack_operation_ids'],
              'stock.picking.wave': ['id', 'name', 'picking_type_id', 'user_id', 'min_date', 'state', 'picking_state', 'location_id', 'location_dest_id', 'wave_id', 'remaining_ops', 'pack_operation_count', 'pack_operation_ids'],
              'stock.pack.operation': ['id', 'display_name', 'package_id', 'result_package_id', 'lot_id', 'pda_product_id', 'pda_done', 'product_qty', 'qty_done', 'track_all', 'picking_id', 'location_id', 'location_dest_id', 'product_uom_id', 'need_confirm', 'uos_id', 'uos_qty', 'ean13'],
              'stock.pack.operation.lot': ['id', 'display_name', 'lot_id', 'qty', 'qty_todo']}

INFO_FIELDS_M2O = {'stock.quant.package': ['id', 'name', 'location_id', 'package_qty', 'multi', 'product_id', 'uom_id'],
                  'stock.production.lot': ['id', 'name', 'use_date', 'location_id', 'qty_available', 'display_name', 'uom_id', 'location_id'],
                  'stock.location': ['id', 'name', 'usage', 'loc_barcode', 'need_check'],
                  'stock.quant':['id', 'display_name', 'lot_id', 'location_id', 'qty', 'reservation_id', 'in_date'],
                  'product.uom': ['id', 'name'],
                  'res.users':  ['id', 'name'],
                  'stock.pack.operation': ['id', 'display_name', 'package_id', 'result_package_id', 'lot_id', 'pda_product_id', 'pda_done', 'product_qty', 'qty_done', 'track_all', 'picking_id', 'location_id', 'location_dest_id', 'product_uom_id', 'need_confirm', 'uos_id', 'uos_qty', 'ean13'],
                  'stock.pack.operation.lot': ['id', 'display_name', 'lot_id', 'qty', 'qty_todo'],
                  'stock.picking.type': ['id', 'name', 'show_in_pda', 'short_name', 'code', 'process_from_tree'],
                  'stock.picking': ['id', 'name', 'picking_type_id', 'user_id', 'min_date', 'state', 'location_id', 'location_dest_id', 'wave_id',  'remaining_ops', 'pack_operation_count', 'pack_operation_ids'],
                  'stock.picking.wave': ['id', 'name', 'picking_type_id', 'user_id', 'min_date', 'state', 'picking_state', 'location_id', 'location_dest_id', 'remaining_ops', 'pack_operation_count', 'pack_operation_ids'],
                  'product.product': ['id', 'display_name', 'ean13', 'name', 'default_code', 'default_stock_location_id', 'track_all', 'uom_id']}


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

    def check_context(self, ctx, model, id):
        if model == 'stock.picking':
            force_company = 1
            ctx.update(force_company=force_company)
            object_id = self.sudo().with_context(ctx).env[model].browse(id)
        elif model == 'stock.production.lot':
            force_company = self.env.user.company_id.id
            ctx.update(force_company=force_company)
            object_id = self.sudo().with_context(ctx).env[model].browse(id)
        elif model in ('stock.quant.package', 'stock.location', 'product.product'):
            domain = [('id', '=', id)]
            company = self.env[model].sudo().search_read(domain, ['company_id'])
            company_id = company and company[0]['company_id'][0]
            if company_id == self.env.user.company_id.id:
                object_id = self.env[model].browse(id)
            else:
                ctx.update(force_company=company_id)
                object_id = self.with_context(ctx).env[model].browse(id)
        else:
            object_id = self.env[model].browse(id)

        return object_id


    def get_selection(self, object_id, field):

        value = [t for t in object_id.fields_get(field)[field]['selection'] if t[0].startswith(object_id[field])]
        return value and {'value': value[0][0], 'name': value[0][1]} or ''

    @api.model
    def get_info_object(self, vals):
        model = vals.get('model', False)
        id = vals.get('id', False)
        object_id = self.check_context(self._context.copy(), model, id)

        field_value = {}
        if not object_id:
            return False
        try:
            for field in INFO_FIELDS[model]:
                print "Buscando %s"%field
                if object_id.fields_get(field)[field]['type'] == 'many2one':
                    field_value[field] = self.get_m2o_vals(object_id, field)

                elif object_id.fields_get(field)[field]['type'] == 'selection':
                    field_value[field] = self.get_selection(object_id, field)
                elif object_id.fields_get(field)[field]['type'] == 'one2many':
                    field_value[field] = self.get_o2m_vals(object_id, field)
                else:
                    field_value[field] = object_id[field]
            res = {'model': model, 'id': id, 'values': field_value}
        except ValidationError, e:
            print "Error en %s"%field
            res.update(error = e)
        
        return res


    def get_m2o_vals(self, object_id, field):


         if object_id[field]:
             sub_values = {}
             submodel = object_id.fields_get(field)[field]['relation']

             for sub_field in INFO_FIELDS_M2O[submodel]:

                 if object_id[field].fields_get(sub_field)[sub_field]['type'] == 'many2one':
                     sub_values[sub_field] = self.get_m2o_val(object_id[field][sub_field])

                 elif object_id[field].fields_get(sub_field)[sub_field]['type'] == 'selection':
                     sub_values[sub_field] = self.get_selection(object_id[field],sub_field)

                 elif object_id[field].fields_get(sub_field)[sub_field]['type'] == 'one2many':
                     if object_id[field][sub_field]._name != object_id._name:
                         sub_values[sub_field] = self.get_o2m_vals(object_id[field], sub_field)
                     else:
                         sub_values[sub_field] = object_id[field][sub_field].mapped('display_name')

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



    def get_order_self(self, objs, field_to_order):
        ##  Si en el contexto viene algo como:
        ## 'o2m_order': {'pack_operation_ids': {'field': 'picking_order', 'reverse': False}}
        sorted_ = self._context.get('o2m_order', False)
        if sorted_:
            sorted = sorted_.get(field_to_order, False)
            if sorted:
                sorted_field = sorted.get('field') 
                sorted_order = sorted.get('reverse', False)

                return objs.sorted(lambda x: x[sorted_field], reverse=sorted_order)


        return objs


    def get_o2m_vals(self, object_id, field):

        submodel = object_id.fields_get(field)[field]['relation']  
        sub_model_id_values = []

        objs = self.get_order_self(object_id[field], field)
        for sub_model_id in objs:
            sub_values = {}
            for sub_field in INFO_FIELDS_M2O[submodel]:
                if sub_model_id.fields_get(sub_field)[sub_field]['type'] == 'many2one':
                    sub_values[sub_field] = self.get_m2o_val(sub_model_id[sub_field])
                elif sub_model_id.fields_get(sub_field)[sub_field]['type'] == 'one2many':
                    sub_values[sub_field] = self.get_o2m_vals(sub_model_id, sub_field)

                elif sub_model_id.fields_get(sub_field)[sub_field]['type'] == 'selection':
                    sub_values[sub_field] = self.get_selection(sub_model_id, sub_field)

                else:
                    sub_values[sub_field] = sub_model_id[sub_field]
            sub_model_id_values.append(sub_values)
        return sub_model_id_values

    @api.model
    def get_object_id(self, vals):
        print vals
        model = vals.get('model', False)
        id = vals.get('id', False)

        if id and model:
            res = self.get_info_object({'id': id, 'model': model})
            return res

        order = vals.get('search_order', False)
        default_domain = vals.get('domain', False)
        search_str = vals.get('search_str')
        ##OPCION 2: Recibo una cadena para buscarla en los model que me lleguen: Devuelvo get_info_object con el primer id que encuentre
        if search_str:
            search_options = list(set(SEARCH_OPTIONS.keys()) & set(model))
            for option in search_options:
                domain = [(SEARCH_OPTIONS[option], '=', search_str)]
                if default_domain:
                    domain += default_domain
                val_id = self.env[option].search_read(domain, ['id'], order=order, limit=1)
                if val_id:
                    id = val_id[0]['id']
                    break

        if id:
            print "Busco el objeto %s con id %s"%(option, id)
            res = self.get_info_object({'id': id, 'model': option})
        else:
            res = {'model': model, 'id': 0,  'message': 'No se ha encontrado un objeto para %s'%search_str}
        return res


    @api.model
    def print_tag(self, values):
        
        printer_barcode = values.get('printer_barcode', False)
        printer = False
        if printer_barcode:
            ctx = self._context.copy()
            printer = self.env['printing.printer'].search([('barcode', '=', values.get('printer_barcode'))], limit=1)

        
        if printer:
            #force_printer = self._context.get('force_printer', False)
            #printer_id = self._context.get('printer_id', False)
            ctx['printer_id'] = printer.id
            ctx['force_printer'] = True
            obj = self.env[values.get('model')].with_context(ctx).browse(values.get('id'))
        
        else:
            obj = self.env[values.get('model')].browse(values.get('id'))
        
        if obj:
            obj.print_barcode_tag_report()
        return True
        



    @api.model
    def get_object_id_V10(self, vals):
        res = {}
        model = vals.get('model', False)
        return_object = vals.get('return_object', False)
        field_value = {}

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
                    object_id = self.env[model].search(domain, limit=1)
                    if object_id:
                        break
            else:
                id = vals.get('id', False)
                if id:
                    object_id = self.env[model].browse(id)
            if object_id:
                res = {'model': model, 'id': object_id.id, 'name': FIELD_NAME[model]}
                if return_object:
                    for field in FIELDS[model]:
                        type = object_id.fields_get(field)[field]['type']
                        if type == 'many2one':
                            field_value[field] = object_id[field]['id'], object_id[field]['name']
                        elif type in ('many2many', 'one2man'):
                            for depend_id in object_id.field:
                                field_value[field] += [depend_id.id, depend_id.name]
                        else:
                            field_value[field] = object_id[field]
                    res['fields'] = field_value
            else:
                res = {'model': model, 'id': 0, 'name': FIELD_NAME[model], 'message': 'No se ha encontrado un %s para %s'%(model, search_str)}
        return res

    @api.model
    def get_scanned_object_id(self, vals):
        res =  {'model': '', 'id': 0}
        search_str = vals.get('search_str')
        search_str.upper()

        models = vals.get('model', [])
        for model in models:
            field = SEARCH_OPTIONS.get(model, False)
            if field:
                domain = [(field, '=', search_str)]
                object_id = self.env[model].search_read(domain, ['id'], limit=1)
                if object_id:
                    id = object_id[0]['id']
                    res = {'model': model, 'id': id}
                    return res
        return res


    @api.model
    def get_ids(self, vals):
        model = vals.get('model', False)
        search_str = vals.get('search_str', '')
        search_domain = vals.get('search_domain', [])
        id = vals.get('id', False)
        if id:
            domain = [('id','=',id)]
            object_ids = self.env[model].search_read(domain, FIELDS[model])
            return {'model': model, 'id': id, 'values': object_ids}
        else:
            search_options = list(set(SEARCH_OPTIONS.keys()) & set(model))
            for option in search_options:
                model = option
                domain = search_domain + [(SEARCH_OPTIONS[option], '=', search_str)] + DOMAIN[option]
                object_ids = self.env[model].search_read(domain, FIELDS[option])
                if object_ids:
                    break
        ##SEGUN EL TIPO DE MODELO, HAGO UNOS FILTROS PARA NO ENVIAR DATOS INSERVIBLES
        if option == 'stock.production.lot':
            object_ids = [x for x in object_ids if x['qty_available'] > 0.00]

        if not object_ids:
            res = {'model': False, 'id': id, 'values': []}

        else:
            if len(object_ids) == 1:
                id = object_ids[0]['id']
            res = {'model': option, 'id': id, 'values': object_ids}
        return res

    @api.model
    def get_scanned_id(self, vals):

        models = vals.get('model', [])
        search_str = vals.get('search_str', '')
        product_id = vals.get('product_id', False)

        #LO HAGO CON SQL POR VELOCIDAD Y COMPAÑIA
        ids = []
        model_str = ''

        if 'stock.quant.package' in models:
            sql = "select id from stock_quant_package where name = '%s' limit 1 "%search_str
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model_str = 'package_id'
        if ids == [] and 'stock.production.lot' in models:
            sql = "select id from stock_production_lot where name = '%s' and (product_id = null or product_id = %s) order by product_id desc limit 1" %(search_str, product_id)
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model_str = 'lot_id'
        if ids == []  and 'stock.location' in models:
            sql = "select id from stock_location where loc_barcode = '%s' limit 1" % search_str
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model_str = 'location_id'
        if ids == [] and 'product.product' in models:
            sql = "select id from product_product where ean13 = '%s' limit 1" % search_str
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model_str ="product_id"

        if ids != []:
            res = {'id': ids[0][0], 'model': model_str}
        else:
            res = {'id': False, 'model': ''}
        print "---------------------\nFuncion get_scanned_id devuelve :\n %s\n--------------------------------" % res
        return res








