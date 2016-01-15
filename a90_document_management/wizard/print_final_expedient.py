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
from pyPdf import PdfFileReader
from tempfile import mkstemp
import os
import base64
from openerp import netsvc
import subprocess
class print_final_expedient(osv.osv_memory):
    _name = 'print.final.expedient'
    _description = 'Print final expedient filter by invoices'
    _columns = {
        'invoice_ids': fields.many2many('account.invoice','account_invoice_print_final_exp', 'print_final_exp_id', 'invoice_id', 'Invoices', required=True),
        'set_order_by': fields.selection([('partner_name', 'Partner name'),('number', 'Invoice number'),('origin', 'Origin'),('wzd_name','Wizard name'),
                                          ('date_due', 'Due date'),('date_invoice', 'Invoice date')], 'Order by'),
        'asc_desc': fields.selection([('asc', 'Up'),('desc','Down')], 'Order mode')

    }
    _defaults = {
        'asc_desc': 'desc',
        'set_order_by': 'partner_name'
    }

    def default_get(self, cr, uid, fields, context=None):
        """ Get default values
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for default value
        @param context: A standard dictionary
        @return: default values of fields
        """
        if context is None:
            context = {}
        res = super(print_final_expedient, self).default_get(cr, uid, fields, context=context)
        res.update({'invoice_ids' : context.get('active_ids',False)})
        return res

    def print_final_expedient(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        form_obj = self.browse(cr, uid, ids, context=context)[0]
        attach_ids = []
        send_printer = []
        to_print_invoices = []
        printer = False

        if form_obj.invoice_ids:
            if form_obj.set_order_by and form_obj.asc_desc:
                invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('id','in', [x.id for x in form_obj.invoice_ids])], order=form_obj.set_order_by + ' ' + form_obj.asc_desc)
            else:
                invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('id','in', [x.id for x in form_obj.invoice_ids])])

            for inv_id in invoice_ids:
                invoice = self.pool.get('account.invoice').browse(cr, uid, inv_id, context=context)
                if 'x_expedient_id' in invoice._columns and invoice.x_expedient_id:
                    attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_id','=',invoice.id),('res_model','=','account.invoice')],order='create_date desc')
                    if attach_ids:
                        for attach in attach_ids:
                            attach_obj = self.pool.get('ir.attachment').browse(cr, uid, attach)
                            if 'finalDocument' in attach_obj.name:

                                send_printer.append(attach_obj.id)
                                to_print_invoices.append(invoice.id)
                                break
                    attach_ids = []
        user = self.pool.get('res.users').browse(cr, uid, uid,context)
        if user.printing_printer_id:
            printer = user.printing_printer_id.system_name

        pages = {}
        if send_printer and printer:
            x = 1
            for id in send_printer:
                attach_obj = self.pool.get('ir.attachment').browse(cr, uid, id)
                #self.pool.get('ir.actions.report.xml').print_direct(cr, uid, attach_obj.datas,'raw',printer)


                logger = netsvc.Logger()

                fd, file_name = mkstemp()
                try:
                    os.write(fd, base64.decodestring(attach_obj.datas))
                finally:
                    os.close(fd)

                input1 = PdfFileReader(file(file_name, "rb"))
                pages_total = input1.getNumPages()
                pages[file_name.split('/')[2]] = pages_total

                printer_system_name = ''
                if printer:
                    if isinstance(printer, (str,unicode)):
                        printer_system_name = printer
                    else:
                        printer_system_name = printer.system_name
                    cmd = "lpr -q -P %s %s" % (printer_system_name,file_name)
                    logger.notifyChannel("report", netsvc.LOG_INFO,"Printing job : '%s'" % cmd)
                    a = subprocess.Popen(cmd, shell = True)
                    x += 1

            y = subprocess.Popen('lpq -P ' + printer_system_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            text = False
            while True:
                line = y.stdout.readline()
                if line != '':
                    print "test:", line.rstrip()
                    text = line.split()
                    if text[0][0].isdigit():
                        if text[2].isdigit():
                            if pages.get(text[3],False):
                                if pages[text[3]]:
                                    pro = "lp -i %s -H resume -P 1-%s" % (text[2],pages[text[3]])
                                    subprocess.call(pro, shell=True)
                else:
                    break

            for invoice in self.pool.get('account.invoice').browse(cr, uid, to_print_invoices):
                if 'x_expedient_id' in invoice._columns and invoice.x_expedient_id:
                    cr.commit()
                    cr.execute("update expedient set state = 'printed' where id = %s" % str(invoice.x_expedient_id.id))
                    cr.commit()
                    # self.pool.get('expedient').write(cr, uid, [invoice.x_expedient_id.id], {'state': 'printed'},context=context)
                    # invoice.write({'printed': True},context=context)
                    cr.execute("update account_invoice set printed = true where id = %s" % str(invoice.id))

                    message = "Printed final expedient of the invoice " + invoice.number + " from wizard of invoices."
                    self.pool.get('account.invoice').log_expedient(cr, user.id, invoice.id, message, False, invoice.x_expedient_id.id, context=context)


        return {'type': 'ir.actions.act_window_close'}
