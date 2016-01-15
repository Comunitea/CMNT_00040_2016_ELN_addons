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
from openerp import netsvc
from jasper_reports.jasper_report import report_jasper

class expedient_account_invoices(osv.TransientModel):
    _name = "expedient.account.invoices"
    _description = "Wizard to expedient the selected invoices."
    _columns = {
        'name': fields.char('Name', size=255)
    }

    def expedient_invoices(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        validate_ids = []
        child_invalid = []
        ok = False
        form_obj = self.browse(cr, uid, ids, context=context)[0]
        expe_obj = self.pool.get('expedient')
        inv_obj = self.pool.get('account.invoice')
        wf_service = netsvc.LocalService('workflow')
        data_inv = self.pool.get('account.invoice').read(cr, uid, context['active_ids'], ['state', 'number'], context=context)

        def _write_log(invoice_obj,message,context):
            inv_obj.log_expedient(cr, uid, invoice_obj.id, message, False, invoice_obj.x_expedient_id.id, context=context)

        def _create_jaspers(invoice_id,context):
            """Generate de invoice jasper documents for Alfa90"""

            jasper_class = report_jasper('report.invoice', 'account.invoice', parser=None)
            jasper_class.create(cr, uid, [invoice_id], {'model': 'account.invoice', 'id': invoice_id, 'ids': [invoice_id]}, context=context)

        def _validate_invoice(invoice_obj,number, id,context):
            if invoice_obj.state == 'open':
                if 'x_expedient_id' in invoice_obj._columns:
                    if invoice_obj.x_expedient_id:
                        _write_log(invoice_obj,"Invoice " + str(invoice_obj.number) + " validated",context)
            else:
                if 'x_expedient_id' in invoice_obj._columns:
                    if invoice_obj.x_expedient_id:
                        _write_log(invoice_obj, "Couldn't validate the invoice " + str(number), context)


        for record in data_inv:
            invoice_obj = inv_obj.browse(cr, uid, record['id'])
            wf_service.trg_validate(uid, 'account.invoice', record['id'], 'invoice_open', cr)
            _validate_invoice(invoice_obj, str(record['number']),record['id'],context)
            _create_jaspers(invoice_obj.id,context)
            invoice_obj = inv_obj.browse(cr, uid, record['id'])
            validate_ids.append(record['id'])
        if validate_ids:
            for id in validate_ids:
                invoice_obj = inv_obj.browse(cr, uid, id)
                if 'x_expedient_id' in invoice_obj._columns:
                    if invoice_obj.x_expedient_id:
                        if form_obj.name:
                            expe_obj.write(cr, uid, [invoice_obj.x_expedient_id.id],{'wzd_name': form_obj.name})
                            inv_obj.write(cr, uid, [invoice_obj.id], {'wzd_name':form_obj.name})
                        if invoice_obj.x_expedient_id.child_expedient_ids:

                            def _validate_child_expedients(child, invoice_obj):
                                _write_log(invoice_obj, "Validating child expedient " + child.name, context)
                                expe_obj.validate_expedient(cr, uid, [child.id],context=context)
                                exp_obj = expe_obj.browse(cr, uid, child.id)
                                if exp_obj.state == 'completed':
                                    _write_log(invoice_obj,"Expedient " + exp_obj.name + " validated" , context)
                                else:
                                    _write_log(invoice_obj, "The expedient " + exp_obj.name + " is incompleted and can't be validated", context)
                                    child_invalid.append(child.id)
                                    expe_obj.write(cr, uid, [invoice_obj.x_expedient_id.id], {'state': 'incomplete'})
                                if child.child_expedient_ids:
                                    for ch in child.child_expedient_ids:
                                        _validate_child_expedients(ch, invoice_obj)
                                return True

                            for child in invoice_obj.x_expedient_id.child_expedient_ids:
                                _validate_child_expedients(child, invoice_obj )

                        if not child_invalid:
                            _write_log(invoice_obj, "Validating expedient " + invoice_obj.x_expedient_id.name, context)
                            #validating expedient
                            expe_obj.validate_expedient(cr, uid, [invoice_obj.x_expedient_id.id],context=context)
                            exp_obj = expe_obj.browse(cr, uid, invoice_obj.x_expedient_id.id)

                            if exp_obj.state == 'completed':
                                _write_log(invoice_obj, "Expedient " + exp_obj.name + " validated", context)
                                _write_log(invoice_obj,"Creating expedient final for expedient " + exp_obj.name, context)
                                ok = expe_obj.create_final_expedient(cr, uid, [exp_obj.id], context=context)
                                if ok == True:
                                    exp_obj = expe_obj.browse(cr, uid, exp_obj.id)
                                    _write_log(invoice_obj,"The final expedient was created successfully for expedient " + exp_obj.name, context)
                                    ok = False
                                else:
                                    _write_log(invoice_obj,"Error! The final expedient wasn't created. Expedient:  " + exp_obj.name, context)
                            else: # exp_obj.state <> 'completed'
                                expe_obj.write(cr, uid, [invoice_obj.x_expedient_id.id], {'state': 'incomplete'})
                                _write_log(invoice_obj,"The expedient " + exp_obj.name + " is incompleted and can't be validated", context)
                        else: # child_invalid
                            _write_log(invoice_obj,"The expedient of the invoice" + invoice_obj.number + " has child expedients that it can't validate", context)
                    else: # not invoice_obj.x_expedient_id
                        _write_log(invoice_obj,"The invoice " + invoice_obj.number + " hasn't expedient. So isn't associated with any expedient", context)
                else: # not 'x_expedient_id' in invoice_obj._columns
                    _write_log(invoice_obj,"The invoice " + invoice_obj.number + " hasn't field expedient.", context)

        return {'type': 'ir.actions.act_window_close'}
