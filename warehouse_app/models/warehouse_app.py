# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp


SEARCH_OPTIONS = {
    'stock.production.lot': ['name'],
    'stock.location': ['loc_barcode'],
    'product.product': ['ean13', 'dun14', 'default_code'],
}

FIELD_NAME = {
    'stock.production.lot': 'name',
    'stock.location': 'loc_barcode',
    'product.product': 'display_name',
}

FIELDS = {
    'stock.production.lot': ['id', 'name', 'qty_available', 'product_id','use_date', 'life_date', 'location_id', 'uom_id'],
    'stock.location': ['id', 'name', 'usage', 'loc_barcode', 'company_id'],
    'product.product': ['id', 'name', 'barcode13', 'default_code', 'track_all', 'company_id'],
}

DOMAIN = {
    'stock.production.lot': [],
    'stock.location': [],
    'product.product': [],
}

INFO_FIELDS = {
    'stock.production.lot': ['id', 'name', 'product_id', 'use_date', 'removal_date', 'qty_available', 'quant_ids', 'display_name', 'uom_id', 'location_id'],
    'stock.location': ['id', 'name', 'usage', 'loc_barcode', 'need_check'],
    'product.product': ['id', 'display_name', 'name', 'ean13', 'dun14', 'default_code', 'track_all', 'uom_id', 'qty_available', 'quant_ids'],
    'stock.picking': ['id', 'name', 'picking_type_id', 'user_id', 'min_date', 'state', 'location_id', 'location_dest_id', 'ops_str', 'remaining_ops', 'pack_operation_count', 'pack_operation_ids', 'partner_id'],
    'stock.pack.operation': ['id', 'display_name', 'lot_id', 'pda_product_id', 'pda_done', 'product_qty', 'qty_done', 'track_all', 'picking_id', 'location_id', 'location_dest_id', 'product_uom_id', 'need_confirm', 'uos_id', 'uos_qty', 'ean13'],
    'stock.pack.operation.lot': ['id', 'display_name', 'lot_id', 'qty', 'qty_todo'],
}

INFO_FIELDS_M2O = {
    'stock.production.lot': ['id', 'name', 'use_date', 'location_id', 'qty_available', 'display_name', 'uom_id', 'location_id'],
    'stock.location': ['id', 'name', 'usage', 'loc_barcode', 'need_check', 'pda_name'],
    'stock.quant':['id', 'display_name', 'lot_id', 'location_id', 'qty', 'reservation_id', 'in_date'],
    'product.uom': ['id', 'name'],
    'res.users':  ['id', 'name'],
    'stock.pack.operation': ['id', 'display_name', 'lot_id', 'pda_product_id', 'pda_done', 'product_qty', 'qty_done', 'track_all', 'picking_id', 'location_id', 'location_dest_id', 'product_uom_id', 'need_confirm', 'uos_id', 'uos_qty', 'ean13'],
    'stock.pack.operation.lot': ['id', 'display_name', 'lot_id', 'qty', 'qty_todo'],
    'stock.picking.type': ['id', 'name', 'show_in_pda', 'short_name', 'code', 'process_from_tree'],
    'stock.picking': ['id', 'name', 'picking_type_id', 'user_id', 'min_date', 'state', 'location_id', 'location_dest_id', 'remaining_ops', 'pack_operation_count', 'pack_operation_ids'],
    'product.product': ['id', 'display_name', 'ean13', 'name', 'default_code', 'track_all', 'uom_id', 'quant_ids'],
}


class WarehouseApp(models.Model):
    _name = 'warehouse.app'

    @api.model
    def get_app_fields(self, wa_id):
        object_id = self.browse(wa_id)
        fields = {}
        if object_id:
            for field in fields:
                fields[field] = object_id[field]
        return fields

    def check_context(self, ctx, model, wa_id):
        if model == 'stock.picking':
            force_company = 1
            ctx.update(force_company=force_company)
            object_id = self.sudo().with_context(ctx).env[model].browse(wa_id)
        elif model == 'stock.production.lot':
            force_company = self.env.user.company_id.id
            ctx.update(force_company=force_company)
            object_id = self.sudo().with_context(ctx).env[model].browse(wa_id)
        elif model in ('stock.location', 'product.product'):
            domain = [('id', '=', wa_id)]
            company = self.env[model].sudo().search_read(domain, ['company_id'])
            company_id = company and company[0]['company_id'] and company[0]['company_id'][0]# or self.env.user.company_id.id
            if company_id == self.env.user.company_id.id:
                object_id = self.env[model].browse(wa_id)
            else:
                ctx.update(force_company=company_id)
                object_id = self.with_context(ctx).env[model].browse(wa_id)
        else:
            object_id = self.env[model].browse(wa_id)
        return object_id

    def get_selection1(self, object_id, field):
        value = [t for t in object_id.fields_get(field)[field]['selection'] if t[0].startswith(object_id[field])]
        return value and {'value': value[0][0], 'name': value[0][1]} or ''

    @api.model
    def get_info_object(self, vals):
        model = vals.get('model', False)
        reg_id = vals.get('id', False)
        object_id = self.check_context(self._context.copy(), model, reg_id)
        field_value = {}
        if not object_id:
            return False
        try:
            for field in INFO_FIELDS[model]:
                if object_id.fields_get(field)[field]['type'] == 'many2one':
                    field_value[field] = self.get_m2o_vals(object_id, field)
                elif object_id.fields_get(field)[field]['type'] == 'selection':
                    field_value[field] = self.get_selection1(object_id, field)
                elif object_id.fields_get(field)[field]['type'] == 'one2many':
                    field_value[field] = self.get_o2m_vals(object_id, field)
                else:
                    field_value[field] = object_id[field]
            res = {'model': model, 'id': object_id.id, 'values': field_value}
        except ValidationError, e:
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
                    sub_values[sub_field] = self.get_selection1(object_id[field], sub_field)
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
        if len(val) > 0:
            res = {'id': val.id, 'name': val.name}
            if 'pda_name' in val._fields:
                res['pda_name'] = val.pda_name
            return res
        else:
            return False

    def get_order_self(self, objs, field_to_order):
        ##  Si en el contexto viene algo como:
        ## 'o2m_order': {'pack_operation_ids': {'field': 'picking_order', 'reverse': False}}
        o2m_order = self._context.get('o2m_order', False)
        if o2m_order:
            field_to_order = o2m_order.get(field_to_order, False)
            if field_to_order:
                sorted_field = field_to_order.get('field') 
                sorted_order = field_to_order.get('reverse', False)
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
                    sub_values[sub_field] = self.get_selection1(sub_model_id, sub_field)
                else:
                    sub_values[sub_field] = sub_model_id[sub_field]
            sub_model_id_values.append(sub_values)
        return sub_model_id_values

    @api.model
    def get_object_id(self, vals):
        model = vals.get('model', False)
        reg_id = vals.get('id', False)
        if reg_id and model:
            res = self.get_info_object({'id': reg_id, 'model': model})
            return res
        order = vals.get('search_order', False)
        default_domain = vals.get('domain', [])
        search_str = vals.get('search_str')
        ##OPCION 2: Recibo una cadena para buscarla en los model que me lleguen: Devuelvo get_info_object con el primer id que encuentre
        if search_str:
            search_options = list(set(SEARCH_OPTIONS.keys()) & set(model))
            for option in search_options:
                fields = SEARCH_OPTIONS.get(option, [])
                option = []
                for field in fields:
                    domain = [(field, '=', search_str)]
                if default_domain:
                    domain += default_domain
                val_id = self.env[option].search_read(domain, ['id'], order=order, limit=1)
                if val_id:
                    reg_id = val_id[0]['id']
                    break

        if reg_id:
            res = self.get_info_object({'id': reg_id, 'model': option})
        else:
            res = {'model': model, 'id': 0,  'message': 'No se ha encontrado un objeto para %s' % search_str}
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
            fields = SEARCH_OPTIONS.get(model, [])
            for field in fields:
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

                fields = SEARCH_OPTIONS.get(option, [])
                option = []
                for field in fields:
                    options_domain = [(field, '=', search_str)]
                    domain = search_domain + options_domain + DOMAIN[option]
                    object_ids = self.env[model].search_read(domain, FIELDS[option])
                    if object_ids:
                        break
        ##SEGUN EL TIPO DE MODELO, HAGO UNOS FILTROS PARA NO ENVIAR DATOS INSERVIBLES
        if option == 'stock.production.lot' and False:
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
        limit = vals.get('limit', False)
        domain = vals.get('domain', False)
        #LO HAGO CON SQL POR VELOCIDAD Y COMPAÑIA
        limit_str = ''
        if domain:
            limit_str = domain
        if limit:
            limit_str= "and limit %s"%limit
        ids = []
        if ids == [] and 'stock.production.lot' in models:
            sql = ""
            sql = "select id, name, %s as model from stock_production_lot where name = '%s' %s" %('stock.production.lot', search_str, limit_str)
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model = "lot_id"
        if ids == []  and 'stock.location' in models:
            sql = "select id, name, %s as model from stock_location where loc_barcode = '%s' %s" %('stock.location', search_str, limit_str)
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model = "location_id"
        if ids == [] and 'product.product' in models:
            sql = "select id, name, %s as model from product_product where ean13 = '%s' %s" %('product.product', search_str, limit_str)
            self._cr.execute(sql)
            ids = self._cr.fetchall()
            model = "product_id"
        if ids != []:
            res = {'ids': ids}
        else:
            res = {'id': False}
        return res

    @api.model
    def get_picks_info(self, vals):
        types = vals.get('types', False)
        domain = vals.get('domain', [])
        limit = vals.get('limit', 25)
        if types:
            fields = ('id', 'short_name', 'name')
            types = self.env['stock.picking.type'].search_read([('show_in_pda', '=', True)], fields, limit=limit)

        picks = vals.get('picks', False)
        fields_pick = INFO_FIELDS['stock.picking']
        #fields_pick = ['id', 'name', 'picking_type_id', 'state', 'min_date', 'user_id', 'ops_str', 'pack_operation_count']
        if picks:
            ## Solo debe de encontrar estos estados
            domain_pick = domain + [['state', 'in', ('confirmed', 'partially_available', 'assigned', 'in_progress')]]
            picks = self.env['stock.picking'].search_read(domain_pick, fields_pick, limit=limit)
            picks = self.get_selection_field('stock.picking', picks, 'state')
        res = {
            'types': types,
            'picks': picks,
        }
        return res

    def dict_m2o(self, val):
        if val:
            res = {'id': val[0], 'name': val[1]}
        return res or val

    @api.model
    def get_pick_id(self, vals):
        ## DEVUELVE EL FORMULARIO DE PICK Y LAS OPERACIONES
        id = vals.get('id')
        model = vals.get('model')
        pick = self.env[model].search_read([('id', '=', id)], INFO_FIELDS[model])
        pick = self.get_selection2(model, pick)
        #if model == 'stock.picking':
        #    pick = self.get_selection_field(model, pick, 'state')
        pick = pick and pick[0]
        pick['pack_operation_ids'] = self.env['stock.pack.operation'].search_read([('id', 'in', pick['pack_operation_ids'])], INFO_FIELDS['stock.pack.operation'], order="picking_order asc")
        return pick

    @api.model
    def get_selection2(self, model, values):
        value = values and values[0]
        if value:
            for key in value.keys():
                if 'selection' in self.env[model].fields_get()[key]:
                    values = self.get_selection_field(model, values, key)
        return values

    @api.model
    def get_selection_field(self,  model, values, field):
        selection_values = self.env[model].fields_get()[field]['selection']
        for pick in values:
            dict = [x[1] for x in selection_values if x[0] == pick[field]]
            if dict:
                pick[field] = dict[0]
        return values

    @api.model
    def get_op_id(self, vals):
        id = vals.get('id')
        operation = self.env['stock.pack.operation'].search_read([('id', '=', id)], INFO_FIELDS['stock.pack.operation'])
        operation = operation and operation[0]
        if not operation:
            return
        lot_fields = ['id', 'name', 'display_name', 'location_id', 'use_date']
        location_field = ['id', 'name', 'loc_barcode', 'display_name', 'need_check']

        if operation.get('lot_id', False):
            lot_id = self.env['stock.production.lot'].search_read(
                [('id', '=', operation['lot_id'][0])], lot_fields
            )
            operation['lot_id'] = lot_id and lot_id[0]
        ##Podría usar dict_m2o pero mejor así por si hace falta despues
        #import ipdb; ipdb.set_trace()
        if operation.get('pda_product_id', False):
            pda_product_id = self.env['product.product'].search_read([('id', '=', operation['pda_product_id'][0])], list(set(INFO_FIELDS['product.product']) - set(['quant_ids'])))
            operation['pda_product_id'] = pda_product_id and pda_product_id[0]


        location_id = self.env['stock.location'].search_read(
                [('id', '=', operation['location_id'][0])], location_field)
        operation['location_id'] = location_id and location_id[0]

        location_dest_id = self.env['stock.location'].search_read(
                [('id', '=', operation['location_dest_id'][0])], location_field)
        operation['location_dest_id'] = location_dest_id and location_dest_id[0]
        sql = "select move_id from stock_move_operation_link where operation_id = %s"%id
        self._cr.execute(sql)
        res_all = self._cr.fetchall()
        operation['move_id'] = [x[0] for x in res_all]

        operation['product_uom_id'] = self.dict_m2o(operation['product_uom_id'])
        operation['uos_id'] = self.dict_m2o(operation['uos_id'])

        operation['need_location_check'] = self.env['stock.pack.operation'].get_need_location_check(id)
        if operation['need_location_check']:
            operation['location_id']['need_check'] = True
        return operation

    @api.model
    def check_pack_operation_ids(self, vals):
        pick_id = vals.get('pick_id', False)
        picking = self.env['stock.picking'].browse(pick_id)
        #picking.do_unrserve()
        if picking and not picking.pack_operation_ids:
            if picking.state == 'confirmed2':
                picking.action_confirm()
                picking.action_assign()
            if picking.state == 'confirmed':
                picking.action_confirm()
                picking.force_assign()
            picking.do_prepare_partial()
            ops = picking.pack_operation_count
            return ops
        return False

