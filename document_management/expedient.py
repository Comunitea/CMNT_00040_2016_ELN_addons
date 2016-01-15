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
from osv import osv, fields
from tools.translate import _
from pyPdf import PdfFileReader, PdfFileWriter
import os
import base64
import time
import random
import string

def random_name():
    random.seed()
    d = [random.choice(string.ascii_letters) for x in xrange(10) ]
    name = "".join(d)
    return name

def create_directory(path):
    dir_name = random_name()
    path = os.path.join(path, dir_name)
    os.makedirs(path)
    return dir_name


class type_expedient(osv.osv):
    _name = "type.expedient"
    _description = "Type of expedient"
    _columns = {
        'ref': fields.char('Ref.', size=8, readonly=True),
        'name': fields.char('Name', size=148),
        #'model_ids': fields.many2many('ir.model', 'ir_model_type_expedient_rel','ir_model_id','type_expedient_id','Models'),
        'model_ids': fields.one2many('ir.model.type.expedient', 'type_expedient_id', 'Models'),
        'origin_model': fields.many2one('ir.model', 'Origin model', required=True),
        'cancellation': fields.char("Cancellation", size=255,help="State in which this model should be canceled. Example: For the sales model in the state set aside would be canceled: cancel"),
        'condition': fields.char('Condition', size=255, help="The condition is met we want when creating a record. Format in python code: o.field_name == value "),
        'expedient_document': fields.one2many('type.expedient.document', 'type_expedient_id', 'Documents')
    }

    def create_act_window(self, cr, uid, active_id=False, model=False, context=None):


        act = self.pool.get('ir.actions.act_window').create(cr, uid, {
                         'name': 'Expedient',
                         'type': 'ir.actions.act_window',
                         'res_model': 'expedient',
                         'src_model': model,
                         'view_type': 'form',
                         'view_mode':'tree,form',
                         'target': 'current',
                         'domain':"[('references', 'like','" + model + ",' + str(active_id))]"
                    }, context)
        self.pool.get('ir.values').create(cr, uid, {
                                 'name': 'Expedient',
                                 'model': model,
                                 'key2': 'client_action_multi',
                                 'value': "ir.actions.act_window," + str(act),
                                }, context)
        return True

    def _create_field(self, cr, uid, model):
        field_ids = self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', 'x_expedient_id'),('model', '=', model.model)])
        if not field_ids:
            field_vals = {
                    'field_description': 'Expedient',
                    'model_id': model.id,
                    'model': model.model,
                    'name': 'x_expedient_id',
                    'ttype': 'many2one',
                    'required': False,
                    'state': 'manual',
                    'relation': 'expedient'
            }
            self.pool.get('ir.model.fields').create(cr, uid, field_vals)
            self.create_act_window(cr, uid, 'active_id', model.model)

    def create(self, cr, uid, vals, context=None):
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'type.expedient')
        vals['ref'] = sequence
        res = super(type_expedient, self).create(cr, uid, vals, context)
        if res:
            current_obj = self.browse(cr, uid, res)
            if current_obj:
                if current_obj.origin_model.id:
                    model_obj = self.pool.get('ir.model').browse(cr, uid,current_obj.origin_model.id)
                    self._create_field(cr, uid, model_obj)

                    for child_models in current_obj.model_ids:
                        if child_models.ir_model:
                            model_obj = self.pool.get('ir.model').browse(cr, uid,child_models.ir_model.id)
                            self._create_field(cr, uid, model_obj)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        for current_obj in self.browse(cr, uid, ids):
            if current_obj.origin_model.id:
                model_obj = self.pool.get('ir.model').browse(cr, uid,current_obj.origin_model.id)
                self._create_field(cr, uid, model_obj)

                for child_models in current_obj.model_ids:
                    if child_models.ir_model:
                        model_obj = self.pool.get('ir.model').browse(cr, uid,child_models.ir_model.id)
                        self._create_field(cr, uid, model_obj)

        return super(type_expedient, self).write(cr, uid, ids, vals, context=context)

type_expedient()

class expedient(osv.osv):
    _name = "expedient"
    _description = "Record documentary that grouping together a series of documents."
    _columns = {
        'name': fields.char('Name', size=10),
        'state': fields.selection([
            ('created', 'Created'),
            ('incomplete', 'Incomplete'),
            ('completed', 'Completed'),
            ('printed', 'Printed'),
            ('finalized', 'Finalized')], 'State', required=True, readonly=True),
        'type': fields.many2one('type.expedient', 'Type', required=True),
        'date': fields.date('Date of expedient'),
        'attachment_ids': fields.one2many('ir.attachment','expedient_id','Attachment'),
        'res_log_expedient_ids': fields.one2many('res.log.expedient', 'expedient_id', 'Log expedient', readonly=True),
        # Campos del modelo tipo de expediente. Se arrastran y, algunos se podrán modificar.
        'model_ids': fields.one2many('ir.model.expedient', 'expedient_id', 'Models'),
        'origin_model': fields.many2one('ir.model', 'Origin model', readonly=True),
        'condition': fields.char('Condition', size=255, help="The condition is met we want when creating a record. Format: [('name of the field to evaluate', '=', field value)]"),
        'expedient_document': fields.one2many('expedient.document', 'expedient_id', 'Documents'),
        'prototipe_barcode': fields.char('Prototipe barcode', size=255, readonly=True),
        'references': fields.char('References', size=255),
        'cancellation': fields.char("Cancellation", size=255,help="State in which this model should be canceled. Example: For the sales model in the state set aside would be canceled: cancel"),



    }
    _defaults = {
        'date': fields.date.context_today,
        'prototipe_barcode': 'MODEL-REPORT-PAG: ${model},${id}/${report}/${number}'
    }
    def create(self, cr, uid, vals, context=None):
        """
        By selected type of records sought the type of sequence that is
        associated and believe in the bar code.
        """
        if context is None:
            context = {}
        seq_name = self.pool.get('ir.sequence').get(cr, uid, 'sequence.expedient')
        vals['name'] = seq_name


        return super(expedient, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context = {}
        model_ids_bd = []
        model_ids_vals = []
        exp_obj = self.pool.get('expedient').browse(cr, uid, ids[0])
        if vals.get('model_ids'):
            for model in vals['model_ids']:
                if 'ir_model' in model[2]:
                    if model[2]['ir_model'] <> False:
                        model_ids_vals.append(model[2]['ir_model'])

        for model in exp_obj.model_ids:
            model_ids_bd.append(model.ir_model.id)
        if len(model_ids_bd) <= len(model_ids_vals):
            new_ids = list(set(model_ids_vals).difference(set(model_ids_bd)))
            if new_ids:
                for id in new_ids:
                    model_obj = self.pool.get('ir.model').browse(cr, uid,id)
                    self.pool.get('type.expedient').create_act_window(cr, uid, 'active_id', model_obj.model, context=context)

        return super(expedient, self).write(cr, uid, ids, vals, context=context)



    def onchange_type(self, cr, uid, ids, type):
        val = {}

        if type:
            type_exp_obj = self.pool.get('type.expedient').browse(cr, uid, type)
            val = {
                'model_ids': [x.id for x in type_exp_obj.model_ids],
                'origin_model': type_exp_obj.origin_model.id,
                'condition': type_exp_obj.condition,
                'expedient_document': [x.id for x in type_exp_obj.expedient_document]

            }
        return {'value': val}
    def unlink(self, cr, uid, ids, context=None):
        """only possible delete when the expedient hasn't associates any models. """
        ids_possibles = []
        if not context.get('manual_unlink', False):
            for expedient_id in self.browse(cr, uid, ids, context=context):
                if expedient_id.origin_model:
                    ids_possibles = self.pool.get(expedient_id.origin_model.model).search(cr, uid, [('x_expedient_id','=',expedient_id.name)])
                    if ids_possibles:
                        raise osv.except_osv(_('Invalid action !'), _("Can't delete the expedient because it has associate models. !"))
                if expedient_id.model_ids:
                    for model in expedient_id.model_ids:
                        if model.ir_model and model.ir_model.model:
                            ids_possibles = self.pool.get(model.ir_model.model).search(cr, uid, [('x_expedient_id','=',expedient_id.name)])
                            if ids_possibles:
                                raise osv.except_osv(_('Invalid action !'), _("Can't delete the expedient because it has associate models. !"))

        return super(expedient, self).unlink(cr, uid, ids, context=context)

    def validate_expedient(self, cr, uid, ids, context=None):

        attachments = []

        valid = True
        for expedient in self.browse(cr, uid, ids, context=context):
            if expedient.attachment_ids:
                for attach in expedient.attachment_ids:
                    attachments.append(attach.type2)
                if attachments:
                    if expedient.expedient_document:
                        for document in expedient.expedient_document:
                            if document.ir_act_report_xml_id and document.ir_act_report_xml_id.report_name:
                                if document.required and document.ir_act_report_xml_id.report_name not in attachments:
                                    valid = False
                                    break
            else:
                message = "EXCEPTION: Unable to validate a expedient that hasn't attachments!"
                self.pool.get('expedient').log_expedient(cr, uid, expedient.id, message, False, expedient.id, context=context)
                valid = False
            if valid == True:
                expedient.write({'state': 'completed'})
                message = "The expedient has been successfully validated"
                self.pool.get('expedient').log_expedient(cr, uid, expedient.id, message, False, expedient.id, context=context)
            else:
               expedient.write({'state': 'incomplete'})


        return True

    def verify(self, cr, uid, ids, context=None):
        if not ids:
            ids = self.search(cr, uid, [('state','in',['created','incomplete'])])
        self.validate_expedient(cr, uid, ids, context=context)
    def check_route(self, cr, uid, ids, path="", context=None):
        if path:
            flag = None
            # This can be improved
            if os.path.isdir(path):
                for dirs in os.listdir(path):
                    if os.path.isdir(os.path.join(path, dirs)) and len(os.listdir(os.path.join(path, dirs))) < 4000:
                        flag = dirs
                        break
            flag = flag or create_directory(path)
        return True

    def create_final_expedient(self, cr, uid, ids, context=None):
        """
        This function creates a .pdf with all associated documents to the file.
        The state of the expedient has to be done.
        """
        if context is None:
             context = {}
        visit_documents = []
        expedient_obj = self.browse(cr, uid,ids)
        for expedient_id in expedient_obj:
            invoice_ids = False
            if expedient_id.state == "completed":
                if expedient_id.attachment_ids:
                    #pyPdf
                    output=PdfFileWriter()
                    attachments = []
                    annexs = []
                    for attach_id in expedient_id.attachment_ids:
                        if attach_id.annex:
                            annexs.append((attach_id.id,False))
                        if expedient_id.expedient_document:
                            for document in expedient_id.expedient_document:
                                if document.ir_act_report_xml_id:
                                    if document.ir_act_report_xml_id.report_name == attach_id.type2:
                                        if document.half_page == True:
                                            if attach_id.id not in visit_documents:
                                                visit_documents.append(attach_id.id)
                                                attachments.append((attach_id.id,True))
                                        else:
                                            if attach_id.id not in visit_documents:
                                                visit_documents.append(attach_id.id)
                                                attachments.append((attach_id.id,False))

                    if annexs:
                        for annex in annexs:
                            attachments.append(annex)
                    if attachments:
                        id_path = self.pool.get('document.storage').search(cr, uid, [('name', '=', 'Temp documents')])
                        path = self.pool.get('document.storage').browse(cr, uid, id_path[0]).path
                        self.check_route(cr, uid, ids, path)
                        a = 10
                        f = False
                        x = 0
                        for atch in range(0,len(attachments)):
                            attach = attachments[atch]
                            attach_id = self.pool.get('ir.attachment').browse(cr, uid, attach[0])
                            if attach[1] == False:
                                if f and f.closed <> True and atch <> 0 and attachments[atch-1][1]:
                                    f.close()
#                                    startingDir = os.getcwd() # save our current directory
#                                    testDir = os.path.dirname(__file__)+os.path.sep+u"temp"
                                    os.chdir(path) # change to our test directory
                                    os.system("pdfrecycle -i file-"+str(x-1)+".prc -o file"+str(a))
#                                    os.chdir(startingDir) # change back to where we started
                                    a += 1
                                #I open a new file and I write the binary data of the document I want to get.
                                fil=open(path+u"/file1.pdf","w")
                                fil.write(attach_id.datas)
                                fil.close()
                                #believe and open for writing a new file
                                filx=open(path+u"/file"+str(a)+u".pdf","w")
                                #decoded the first file created from the decoded data to the second. So I have my file .pdf
                                base64.decode(open(path+u"/file1.pdf","r"),filx)
                                filx.close()
                                a += 1
                            else:
                                #For pages marked with half-sheet printing,
                                if f and f.closed <> True and atch <> 0 and attachments[atch-1][1]:
                                    f.write("FILE fil_" + str(x) + ".pdf\n")
                                    fil2=open(path+u"/fil__"+str(x)+u".pdf","w")
                                    fil2.write(attach_id.datas)
                                    fil2.close()
                                    filx= open(+u"/fil_"+str(x)+u".pdf","w")
                                    base64.decode((path+u"/fil__"+str(x)+u".pdf","r"),filx)
                                    filx.close()

                                    fil=file(+"/fil_" + str(x) + ".pdf","rb")
                                    input = PdfFileReader(fil)
                                    f.write("PAGE 1-" + str(input.getNumPages()) + "\n")
                                    f.close()
#                                    startingDir = os.getcwd() # save our current directory

                                    os.chdir(path) # change to our test directory
                                    os.system("pdfrecycle -i file-"+str(x-1)+".prc -o file"+str(a))
#                                    os.chdir(startingDir) # change back to where we started
                                    x += 1
                                    a += 1
                                else:
                                    #First, I created an empty file .prc. What used to group pdfRecycle two pages on one.
                                    f = open(path+u"/file-"+str(x)+".prc","w")
                                    #What I write
                                    f.write("LAYOUT 1x2\n\n")
                                    fil2=open(path+u"/fil__"+str(x)+u".pdf","w")
                                    fil2.write(attach_id.datas)
                                    fil2.close()
                                    filx= open(path+u"/fil_"+str(x)+u".pdf","w")
                                    base64.decode(open(path+u"/fil__"+str(x)+u".pdf","r"),filx)
                                    f.write("FILE fil_"+str(x)+u".pdf\nANGLE 90\n\n")
                                    filx.close()

                                    f.write("MARK both\n")
                                    f.write("FILE fil_" + str(x) + ".pdf\n")
                                    fil=file(path+"/fil_" + str(x) + ".pdf","rb")
                                    input = PdfFileReader(fil)
                                    f.write("PAGE 1-" + str(input.getNumPages()) + "\n")
                                    x += 1

                        if f and f.closed <> True:
                            f.close()
#                                    startingDir = os.getcwd() # save our current directory
#                                    testDir = os.path.dirname(__file__)+os.path.sep+u"temp"

                            os.chdir(path) # change to our test directory
                            os.system("pdfrecycle -i file-"+str(x-1)+".prc -o file"+str(a))
                            a += 1



                        for n in range(10,a):
                            input1 = PdfFileReader(file(path+u"/file"+str(n)+".pdf", "rb"))
                            pages = input1.getNumPages()
                            x=0
                            for npage in range(pages):
                                page = input1.getPage(x)
                                output.addPage(page)
                                x += 1
                            outputStream= file(path+u"/"+r"output0.pdf", "wb")
                            output.write(outputStream)
                            outputStream.close()

                        fildecode=open(path+u"/output_encode.pdf","w")
                        base64.encode(open(path+u"/output0.pdf","r"),fildecode)
                        fildecode.close()
                        fildecode=open(path+u"/output_encode.pdf","r")
                        encode_data = fildecode.read()
                        fildecode.close()
                        #Sobreescribir existente

                        finalexp_unlink_ids = self.pool.get('ir.attachment').search(cr, uid, [('name','=', expedient_id.name + '_finalDocument'),
                                                                                    ('res_model','=', 'expedient'),
                                                                                    ('res_id','=',expedient_id.id)])
                        if finalexp_unlink_ids:
                            self.pool.get('ir.attachment').unlink(cr, uid, finalexp_unlink_ids, context=context)
                        self.pool.get('ir.attachment').create(cr, uid, {
                                                        'name': expedient_id.name + '_finalDocument',
                                                        'datas': encode_data,
                                                        'datas_fname': expedient_id.name + '_finalDocument' + time.strftime("%Y-%m-%d_%H%M%S"),
                                                        'description': 'Document with the grouping of all attachments required by the expedient.',
                                                        'res_model': 'expedient',
                                                        'res_id': expedient_id.id,
                                                        'type': 'binary' })
                        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('x_expedient_id','=',expedient_id.id)])
                        if invoice_ids:
                            for invoice in invoice_ids:
                                finalinv_unlink_ids = self.pool.get('ir.attachment').search(cr, uid, [('name','=', expedient_id.name + '_finalDocument'),
                                                                                    ('res_model','=', 'account.invoice'),
                                                                                    ('res_id','=',invoice)])
                                if finalinv_unlink_ids:
                                    self.pool.get('ir.attachment').unlink(cr, uid, finalinv_unlink_ids, context=context)
                                self.pool.get('ir.attachment').create(cr, uid, {
                                                        'name': expedient_id.name + '_finalDocument',
                                                        'datas': encode_data,
                                                        'datas_fname': expedient_id.name + '_finalDocument' + time.strftime("%Y-%m-%d_%H%M%S"),
                                                        'description': 'Document with the grouping of all attachments required by the expedient.',
                                                        'res_model': 'account.invoice',
                                                        'res_id': invoice,
                                                        'type': 'binary' })

                        expedient_id.write({'state': 'finalized'})
                        message = "The final expedient has been created successfully. You can view it by entering the expedient attachments."
                        self.pool.get('expedient').log_expedient(cr, uid, expedient_id.id, message, False, expedient_id.id, context=context)
                    else:
                        message = "EXCEPTION: The expedient is bad configured."
                        self.pool.get('expedient').log_expedient(cr, uid, expedient_id.id, message, False, expedient_id.id, context=context)
            else:
                message = "EXCEPTION: The expedient is not yet complete and, therefore, can not generally the final document! Please modify your settings or attach all required documents."
                self.pool.get('expedient').log_expedient(cr, uid, expedient_id.id, message, False, expedient_id.id, context=context)

        return True
    def go_back(self, cr, uid, ids, context=None):
        if context is None:
             context = {}
        for expedient in self.browse(cr, uid, ids, context=context):
            expedient.write({'state': 'completed'})

expedient()
