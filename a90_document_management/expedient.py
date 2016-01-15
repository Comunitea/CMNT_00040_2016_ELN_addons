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
from openerp.osv import osv, fields

from pyPdf import PdfFileReader, PdfFileWriter
import os
import base64
import time
import logging as log
from subprocess import Popen, PIPE


class expedient(osv.osv):
    _inherit = 'expedient'
    _columns = {
        'wzd_name': fields.char('Group', size=255, readonly=True, help='Name of the group of files created in the assistant'),
        'date_origin_model': fields.char('Date', size=255,readonly=True),
        'name_origin_model': fields.char('Origin document',size=255,readonly=True),
        'partner_name_expedient': fields.char('Partner name',size=255,readonly=True),
        'parent_expedient': fields.many2one('expedient', 'Parent', readonly=True),
        'child_expedient_ids': fields.one2many('expedient', 'parent_expedient', readonly=True),

    }

    def validate_expedient(self, cr, uid, ids,  context=None):

        for expedient_obj in self.browse(cr, uid, ids, context=context):
            valid = True
            if expedient_obj.child_expedient_ids:
                self.validate_expedient(cr, uid, [x.id for x in expedient_obj.child_expedient_ids], context=context)
                expedient_obj = self.browse(cr, uid, expedient_obj.id, context=context)
                for child in expedient_obj.child_expedient_ids:
                    if child.state == "incomplete":
                        valid = False

            if valid:
                return super(expedient, self).validate_expedient(cr, uid, ids, context=context)
            else:
                message = "EXCEPTION: Incomplete child expedient"
                self.pool.get('expedient').log_expedient(cr, uid, expedient_obj.id, message, False, expedient_obj.id, context=context)
                expedient_obj.write({'state': 'incomplete'})
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
                        if expedient_id.expedient_document:
                            for document in expedient_id.expedient_document:
                                    if document.ir_act_report_xml_id:
                                        if document.ir_act_report_xml_id.report_name == attach_id.type2:
                                            if document.half_page == True:
                                                if attach_id.id not in visit_documents:
                                                    visit_documents.append(attach_id.id)
                                                    attachments.append((attach_id.id,True,document.sequence))
                                            else:
                                                if attach_id.id not in visit_documents:
                                                    visit_documents.append(attach_id.id)
                                                    attachments.append((attach_id.id,False,document.sequence))






                    attachments = sorted(attachments,key=lambda attachments: attachments[2])
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
                                    # os.system("pdfrecycle -i file-"+str(x-1)+".prc -o file"+str(a))
                                    p = Popen(["pdfrecycle","-i","file-"+str(x-1)+".prc","-o","file"+str(a)],stdout=PIPE, stderr=PIPE, env = {"PATH" : "/usr/local/bin/:/usr/bin"})
                                    code = p.wait()
                                    out, errs = p.communicate()
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
                                    filx= open(path+u"/fil_"+str(x)+u".pdf","w")
                                    base64.decode(open(path+u"/fil__"+str(x)+u".pdf","r"),filx)
                                    filx.close()

                                    fil=file(path+"/fil_" + str(x) + ".pdf","rb")
                                    input = PdfFileReader(fil)
                                    f.write("PAGE 1-" + str(input.getNumPages()) + "\n")
                                    f.close()
#                                    startingDir = os.getcwd() # save our current directory

                                    os.chdir(path) # change to our test directory
                                    # os.system("pdfrecycle -i file-"+str(x-1)+".prc -o file"+str(a))

                                    p = Popen(["pdfrecycle","-i","file-"+str(x-1)+".prc","-o","file"+str(a)],stdout=PIPE, stderr=PIPE, env = {"PATH" : "/usr/local/bin/:/usr/bin"})
                                    p.wait()
                                    out, errs = p.communicate()
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
#
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
                            # os.system("pdfrecycle -i file-"+str(x-1)+".prc -o file"+str(a))

                            p = Popen(["pdfrecycle","-i","file-"+str(x-1)+".prc","-o","file"+str(a)],stdout=PIPE, stderr=PIPE, env = {"PATH" : "/usr/local/bin/:/usr/bin"})
                            p.wait()
                            out, errs = p.communicate()
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

                        finalexp_unlink_ids = self.pool.get('ir.attachment').search(cr, uid, [('name','=', expedient_id.name + '_finalDocument.pdf'),
                                                                                    ('res_model','=', 'expedient'),
                                                                                    ('res_id','=',expedient_id.id)])
                        if finalexp_unlink_ids:
                            self.pool.get('ir.attachment').unlink(cr, uid, finalexp_unlink_ids, context=context)
                        self.pool.get('ir.attachment').create(cr, uid, {
                                                        'name': expedient_id.name + '_finalDocument.pdf',
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
