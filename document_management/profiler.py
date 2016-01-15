# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import osv
import report
import openerp.pooler as pooler
from tools.translate import _
import time
import base64

def log_expedient(self, cr, uid, id, message, secondary=False, expedient_id=False, context=None):
        if context and context.get('disable_log'):
            return True
        return self.pool.get('res.log.expedient').create(cr, uid,
                {
                    'name': message,
                    'res_model': self._name,
                    'secondary': secondary,
                    'res_id': id,
                    'expedient_id': expedient_id
                },
                context=context
        )
if 'log_expedient' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.log_expedient = log_expedient
#Allow calling to old create method...
if 'old_create' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_create = osv.orm.BaseModel.create
#Allow calling to old write method...
if 'old_write' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_write = osv.orm.BaseModel.write
if 'old_copy' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_copy = osv.orm.BaseModel.copy
if 'old_create' not in dir(report.report_sxw.report_sxw.create):
    report.report_sxw.report_sxw.old_create = report.report_sxw.report_sxw.create
if 'old_unlink' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_unlink = osv.orm.BaseModel.unlink


def fill_field_child_models(cr, user, self, ids, context=None):
    if context is None:
            context = {}
    """
    Logic for the models allocated in the file type requiring documents.
    """
    ir_model_type_expedient_exist = self.pool.get('ir.model').search(cr, user, [('model','=','ir.model.type.expedient')])
    if ir_model_type_expedient_exist:
        model_message = ""
        id_expedient_message = ""
        ir_model_type_expedient=[]
        type_expedient = []
        set2 = False
        for obj in self.pool.get(self._name).browse(cr, user, ids):

            ir_models = self.pool.get('ir.model').search(cr, user, [('model','=',self._name)])
            if ir_models and self.pool.get('ir.model.type.expedient'):
                ir_model_type_expedient = self.pool.get('ir.model.type.expedient').search(cr, user, [('ir_model','in',[ir_models[0]])])
            if ir_model_type_expedient and self.pool.get('type.expedient') != None:
                type_expedient = self.pool.get('type.expedient').search(cr, user, [('model_ids','in',ir_model_type_expedient)])
                set = False
                for x in self.pool.get('type.expedient').browse(cr, user, type_expedient):
                    for col in self._columns:
                        if self._columns[col]._obj and self._columns[col]._obj == x.origin_model.model and "2" in self._columns[col]._type:
                            id_obj = eval('obj.'+col,{'obj':obj})
                            if self._columns[col]._type <> 'many2one':
                                if id_obj:
                                    id_obj = id_obj[0]

                            if id_obj and id_obj.x_expedient_id:

                                exp_obj = self.pool.get('expedient').browse(cr, user, id_obj.x_expedient_id.id)

                                if exp_obj.references:
                                    ref = (exp_obj.references).split('/')
                                    if obj._name + ',' + str(obj.id) not in ref:
                                        self.pool.get('expedient').old_write(cr, user, id_obj.x_expedient_id.id, {'references': '/'.join(ref) + '/' + obj._name + ',' + str(obj.id)})
                                else:
                                    self.pool.get('expedient').old_write(cr, user, id_obj.x_expedient_id.id, {'references': '/' + obj._name + ',' + str(obj.id)})

                                obj.old_write({'x_expedient_id': id_obj.x_expedient_id.id})
                                set = True

                                if not set2:
                                    model_message = x.origin_model.model
                                    id_expedient_message = id_obj.x_expedient_id.id
                                    set2 = True
                                break

                    if not set:
                        parent_obj = self.pool.get(x.origin_model.model)
                        for col in parent_obj._columns:
                            if parent_obj._columns[col]._obj and parent_obj._columns[col]._obj == self._name:
                                parent_ids = parent_obj.search(cr, user, [(col,'in',ids)])
                                if parent_ids:
                                    parent = parent_obj.browse(cr, user, parent_ids[0])

                                    if parent.x_expedient_id:

                                        obj.old_write({'x_expedient_id': parent.x_expedient_id.id})
                                        set = True

                                        if not set2:
                                            model_message = self._name
                                            id_expedient_message = parent.x_expedient_id.id
                                            set2 = True
                                        break

                    if set2:
                        expedient_ref = self.pool.get('expedient').browse(cr, user, id_expedient_message)
                        message = "Is assign to the line " + str(obj.id) + " from the " + model_message + " object for the " + self._name + " model the x_expedient_id field, with the expedient " + expedient_ref.name
                        logs_expedient = self.pool.get('res.log.expedient').search(cr, user, [('expedient_id','=',obj.x_expedient_id.id),('name','=', message)])
                        if not logs_expedient:
                            self.log_expedient(cr, user, obj.id, message, False, obj.x_expedient_id.id, context=context)

                    if set:
                        break
    return True

def create(self, cr, user, vals, context=None):
    """
    Observer to the method of creating database orm
    that records 'automatically' files and attachments
    if appropriate conditions are met.
    """
    # import ipdb; ipdb.set_trace()
    if context is None:
        context = {}
    model_orig = str(self._name)
     #Logic for the source model given in the type of file.
    create_current = self.old_create(cr, user, vals, context=context)
    vals_expedient = {}
    expedient_id = 0
    set=True
    vals_model_expedient = {}
    # import ipdb; ipdb.set_trace()
    type_expedient_exist = self.pool.get('ir.model').search(cr, user, [('model','=','type.expedient')])
    if type_expedient_exist and self.pool.get('type.expedient') != None:
        type_expedient_ids = self.pool.get('type.expedient').search(cr, user, [('origin_model', '=', model_orig)])
        if type_expedient_ids:
            expedient_type_obj = self.pool.get('type.expedient').browse(cr,user,type_expedient_ids[0])
            obj_=self.pool.get(model_orig).browse(cr, user, create_current)
            if expedient_type_obj.condition:
                if eval(expedient_type_obj.condition,{'o':obj_}):
                    set=True
                else:
                    set=False
            if set==True:
                vals_expedient = {
                                'state': 'created',
                                'type': type_expedient_ids[0],
                                'origin_model': expedient_type_obj.origin_model.id,
                                'condition': expedient_type_obj.condition,
                                'references': model_orig + ',' + str(obj_.id),
                                'cancellation': expedient_type_obj.cancellation
                            }

                expedient_id = self.pool.get('expedient').create(cr, user, vals_expedient)

                for x in expedient_type_obj.expedient_document:
                    vals_expedient_document = {
                        'sequence': x.sequence,
                        'valid_last': x.valid_last,
                        'required': x.required,
                        'ir_act_report_xml_id': x.ir_act_report_xml_id.id,
                        'expedient_id': expedient_id,
                        'half_page': x.half_page,
                        'attach_mode': x.attach_mode,
                    }
                    self.pool.get('expedient.document').create(cr, user, vals_expedient_document)
                for x in expedient_type_obj.model_ids:
                    if x.ir_model and x.cancellation:
                        vals_model_expedient = {
                            'ir_model': x.ir_model.id,
                            'expedient_id': expedient_id,
                            'cancellation': x.cancellation
                        }
                    self.pool.get('ir.model.expedient').create(cr, user, vals_model_expedient)

                self.old_write(cr, user, create_current, {'x_expedient_id':expedient_id})


                for line in obj_._columns:
                    if not self.pool.get('expedient').browse(cr, user, expedient_id).parent_expedient:
                        if "2" in obj_._columns[line]._type and obj_._columns[line]._obj == model_orig:
                            object_relation = eval('obj.'+line,{'obj':obj_})
                            if object_relation:
                                if object_relation.x_expedient_id:
                                    if object_relation.x_expedient_id.parent_expedient:
                                        self.pool.get('expedient').old_write(cr, user, expedient_id, {'parent_expedient': object_relation.x_expedient_id.parent_expedient.id})
                                    else:
                                        self.pool.get('expedient').old_write(cr, user, expedient_id, {'parent_expedient': object_relation.x_expedient_id.id})

        if set==True:
            if expedient_id <> 0 and create_current:
                expedient_ref = self.pool.get('expedient').browse(cr, user, expedient_id)

                message = "The Expedient was created from the object: " + self._description + " and is assign the x_expedient_id field, with the expedient " + expedient_ref.name
                self.log_expedient(cr, user, create_current, message, False, expedient_id, context=context)

            #Function call that fills the field x_expedient_id if you must.
            fill_field_child_models(cr, user, self, [create_current], context=context)

    return create_current

#override create method
osv.orm.BaseModel.create = create

def write(self, cr, user, ids, vals, context=None):
    """
    Observer to the method of creating database orm
    that records 'automatically' files and attachments
    if appropriate conditions are met.
    """
    model_orig = str(self._name)
    if context is None:
        context = {}
    if isinstance(ids,(int,long)):
        ids = [ids]
    if vals.get('attachment_ids',False):
        ids_attach_vals = vals['attachment_ids']
        exp_obj = self.pool.get('expedient').browse(cr, user, ids[0])
        ids_attach_bd = [(6,0,[x.id for x in exp_obj.attachment_ids])]

        if len(ids_attach_bd[0][2]) >= len(ids_attach_vals[0][2]): # remove
            ids_to_remove = list(set(ids_attach_bd[0][2]).difference(set(ids_attach_vals[0][2]))) #ids that are in the database that are not in the vals
            if ids_to_remove:
                for id_unlink in ids_to_remove:
                    ir_attachment_obj = self.pool.get('ir.attachment').browse(cr, user, id_unlink)
                    message = "Has removed to the document " + ir_attachment_obj.name + " of the object " + ir_attachment_obj.res_model
                    self.log_expedient(cr, user, exp_obj.id, message, False, exp_obj.id, context=context)
        else: # add
            ids_to_add = list(set(ids_attach_vals[0][2]).difference(set(ids_attach_bd[0][2]))) #ids that are in the vals that are not in the database
            if ids_to_add:
                for id_add in ids_to_add:
                    ir_attachment_obj = self.pool.get('ir.attachment').browse(cr, user, id_add)
                    message = "Has been added to the document " + ir_attachment_obj.name + " of the object " + ir_attachment_obj.res_model
                    self.log_expedient(cr, user, exp_obj.id, message, False, exp_obj.id, context=context)

    create_current = self.old_write(cr, user, ids, vals, context=context)

    #Function call that fills the field x_expedient_id if you must.
    fill_field_child_models(cr, user, self, ids, context=context)

    type_expedient_exist = self.pool.get('ir.model').search(cr, user, [('model','=','type.expedient')])
    if type_expedient_exist and self.pool.get('type.expedient') != None:
        type_expedient_ids = self.pool.get('type.expedient').search(cr, user, [('origin_model', '=', model_orig)])
        if type_expedient_ids:
            if model_orig <> 'expedient':
                obj_ = self.pool.get(model_orig).browse(cr, user, ids[0])
                for line in obj_._columns:
                    if obj_.x_expedient_id and not obj_.x_expedient_id.parent_expedient:
                        if "2" in obj_._columns[line]._type and obj_._columns[line]._obj == model_orig:
                            object_relation = eval('obj.'+line,{'obj':obj_})
                            if object_relation: #TODO en facturas viene como lista!!!!!!!!!!!!!11
                                if obj_._columns[line]._type == 'many2many':
                                    object_relation = object_relation[0]
                                if object_relation.x_expedient_id:
                                    if object_relation.x_expedient_id.parent_expedient:
                                        self.pool.get('expedient').old_write(cr, user, obj_.x_expedient_id.id, {'parent_expedient': object_relation.x_expedient_id.parent_expedient.id})
                                    else:
                                        self.pool.get('expedient').old_write(cr, user, obj_.x_expedient_id.id, {'parent_expedient': object_relation.x_expedient_id.id})



    ids_add = []
    model_ids = []

    if vals.get('state', False):
        if 'x_expedient_id' in self._columns:
            for obj in self.pool.get(model_orig).browse(cr, user, ids):
                if obj.x_expedient_id:
                    if obj.x_expedient_id.model_ids:
                        for model in obj.x_expedient_id.model_ids:
                            if model.ir_model and model.ir_model.model and model.ir_model.model == model_orig:
                                if model.cancellation and model.cancellation == vals['state']:
                                    model_ids.append(model.ir_model.id)
                    if obj.x_expedient_id.origin_model:
                        if obj.x_expedient_id.origin_model.model == model_orig:
                            if obj.x_expedient_id.cancellation and obj.x_expedient_id.cancellation == vals['state']:
                                model_ids.append(obj.x_expedient_id.origin_model.id)
                    if model_ids:
                        for models in model_ids:
                            model_obj = self.pool.get('ir.model').browse(cr, user, models)
                            if obj.x_expedient_id.attachment_ids:
                                for attach in obj.x_expedient_id.attachment_ids:
                                    if model_obj and model_obj.model and model_obj.model <> attach.res_model:
                                        ids_add.append(attach.id)

                        self.pool.get('expedient').write(cr, user, [obj.x_expedient_id.id], {'attachment_ids': [(6,0,ids_add)]})


    return create_current

#override write method
osv.orm.BaseModel.write = write

def copy(self, cr, uid, id, default=None, context=None):
    if context is None: context = {}
    if 'x_expedient_id' in self._columns:
        default.update({'x_expedient_id': False})

    return self.old_copy(cr, uid, id, default=default, context=context)

#override copy method
osv.orm.BaseModel.copy = copy

def unlink(self, cr, uid, ids, context=None):
    expedients_to_delete = []
    if 'x_expedient_id' in self._columns:
        for obj in self.browse(cr, uid, ids):
            if obj.x_expedient_id:
                expedients_to_delete.append(obj.x_expedient_id.id)

    res = self.old_unlink(cr, uid, ids, context=context)
    if res and expedients_to_delete:
        context['manual_unlink'] = True
        self.pool.get('expedient').unlink(cr, uid, expedients_to_delete, context=context)

    return res

#override unlink method
osv.orm.BaseModel.unlink = unlink

def create_rml(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}

        data_binary,type = self.old_create(cr, uid, ids, data, context=context)
        expedient_document_id = False
        at = []
        continuate = False
        last = False
        state = False
        attachment_id = False

        if context.get('active_model',False) and context.get('active_ids', []):
            obj = pooler.get_pool(cr.dbname).get(context['active_model']).browse(cr, uid, context['active_ids'][0])
            if 'x_expedient_id' in obj._columns:
                if obj.x_expedient_id and obj.x_expedient_id.expedient_document:
                    for report in obj.x_expedient_id.expedient_document:
                        if report.attach_mode and report.attach_mode == 'printing' \
                        and report.ir_act_report_xml_id and report.ir_act_report_xml_id.model \
                        and report.ir_act_report_xml_id.model == context['active_model'] \
                        and report.ir_act_report_xml_id.report_name == (self.name).split("report.")[1]:
                            if report.valid_last == True:
                                last = True
                            else:
                                last = False
                            continuate = True
                            expedient_document_id = report.id
                            break
            if continuate == True:
                if obj.x_expedient_id.attachment_ids:
                    for attach in obj.x_expedient_id.attachment_ids:
                        if attach.res_model == context['active_model']:
                            if attach.name == self.name:
                                if last == False:
                                    at.append(attach.id)
                            else:
                                at.append(attach.id)
                        else:
                            at.append(attach.id)
                obj_current = pooler.get_pool(cr.dbname).get(context['active_model']).browse(cr, uid, context['active_ids'][0])
                if obj.x_expedient_id.model_ids:
                    for model in obj.x_expedient_id.model_ids:
                        if model.ir_model and model.ir_model.model and model.ir_model.model == context['active_model']:
                            if model.cancellation and model.cancellation == obj_current.state:
                                state = True
                if obj.x_expedient_id.origin_model and obj.x_expedient_id.cancellation and obj.x_expedient_id.cancellation == obj_current.state:
                    state = True

                if state == False:
                    attachment_id = pooler.get_pool(cr.dbname).get('ir.attachment').create(cr, uid, {
                        'res_id': context['active_ids'][0],
                        'res_model': context['active_model'],
                        'name': self.name,
                        'datas':  base64.encodestring(data_binary),
                        'datas_fname': obj.name + '_' + time.strftime("%Y-%m-%d") + '.pdf',
                        'description': _('Attachment of ' + context['active_model'] + '-' + str(context['active_ids'][0])),
                        'type2': (self.name).split("report.")[1],
                        'expedient_document_id': expedient_document_id and expedient_document_id or False,
                        'type': 'binary'
                        }, context)

                if attachment_id:
                    at.append(attachment_id)
                if at:
                    pooler.get_pool(cr.dbname).get('expedient').write(cr, uid, [obj.x_expedient_id.id], {'attachment_ids': [(6,0,at)]})
                at = []
        return data_binary, type

#override create method of class report_sxw
report.report_sxw.report_sxw.create = create_rml
