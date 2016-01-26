# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
import time
from openerp import tools
from openerp.addons.jasper_reports import report_jasper
from openerp.tools.translate import _


class mail_compose_message_product_datasheet(osv.osv_memory):
    _name = 'mail.compose.message.product.datasheet'
    _inherit = 'mail.compose.message'
    _columns = {
        'report_template':fields.many2one('ir.actions.report.xml', 'Report to attach'),
        'user_signature': fields.boolean('Signature user'),
        'contact_ids': fields.many2many('res.partner.contact', 'send_email_partner_contact_rel', 'send_email_id', 'contact_id', 'Contacts'),
    }
    
   
    def send_mail(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        attachments = []
        
        form_obj = self.pool.get('mail.compose.message.product.datasheet').browse(cr, uid, ids[0], context=context)
        
        date=time.strftime('%Y-%m-%d %H:%M:%S')
        sent_date = _('On %(date)s, ') % {'date': date}
        sender = _('%(sender_name)s wrote:') % {'sender_name': tools.ustr(form_obj.email_from or _('You'))}
        quoted_body = '> %s' % tools.ustr(form_obj.body_text.replace('\n', "\n> ") or '')
        body = '\n'.join(["\n", (sent_date + sender), quoted_body])
        if form_obj.user_signature == 1:
            body += "\n" + (self.pool.get('res.users').browse(cr, uid, uid).signature or '')
        
            subject = "%s" % ( form_obj.subject)
        msg_vals = {
            'subject': form_obj.subject,
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': uid,
            'model': 'product.product',
            'res_id': context['active_id'],
            'body_text': body,
            'body_html': False,
            'email_from': form_obj.email_from,
            'email_to': form_obj.email_to,
            'email_cc': '',
            'email_bcc': '',
            'subtype': 'plain',
            #'headers': headers, # serialize the dict on the fly
            'state': 'outgoing',
            'auto_delete': True
        }
        email_msg_id = self.pool.get('mail.message').create(cr, uid, msg_vals, context)
        
        if form_obj.report_template:
            jasper_class = report_jasper('report.product.datasheet.jasper', 'product.product', parser=None)
            (result, format) = jasper_class.create(cr, uid, context['active_ids'], {'model': 'product.product', 'id': context['active_ids'][0], 'ids': context['active_ids']}, context=context)

            attachment_data = {
                    'name': 'ficha_tecnica_' + time.strftime('%Y-%m-%d') + '.pdf',
                    'datas_fname': 'ficha_tecnica_' + time.strftime('%Y-%m-%d') + '.pdf',
                    'datas': result and result.encode('base64'),
                    'res_model': 'mail.message',
                    'res_id': email_msg_id,
            }
            
            attachments.append(self.pool.get('ir.attachment').create(cr, uid, attachment_data, context))
            if attachments:
                self.pool.get('mail.message').write(cr, uid, email_msg_id, { 'attachment_ids': [(6, 0, attachments)]}, context=context)
            

           
        ok = self.pool.get('mail.message').send(cr, uid, [email_msg_id], context=context)

        if ok == True:
            product_obj = self.pool.get('product.product').browse(cr, uid, context['active_ids'][0])
            if form_obj.contact_ids:
                for cont in form_obj.contact_ids:
                    if cont.partner_id:
                        partner_id = cont.partner_id.id
                    else:
                        partner_id = False

                    self.pool.get('product.sheet.shipments').create(cr, uid, {
                                'partner_id': partner_id,
                                'contact_id': cont.id,
                                'date': time.strftime("%Y-%m-%d"),
                                'product_id': product_obj.id,
                                'revision': product_obj.last_revision
                                })





        return {'type': 'ir.actions.act_window_close'}

    def default_get(self, cr, uid, fields, context=None):
        """Overridden to provide specific defaults depending on the context
           parameters.

           :param dict context: several context values will modify the behavior
                                of the wizard, cfr. the class description.
        """
        if context is None:
            context = {}
        result = super(mail_compose_message_product_datasheet, self).default_get(cr, uid, fields)
        
        # link to model and record if not done yet
        if not result.get('model') or not result.get('res_id'):
            active_model = context.get('active_model')
            res_id = context.get('active_id')
            if active_model and active_model not in (self._name, 'mail.message'):
                result['model'] = active_model
                if res_id:
                    result['res_id'] = res_id
        # Try to provide default email_from if not specified yet
        
        if not result.get('contact_ids'):
            result['contact_ids'] =context.get('contact_ids')
        if not result.get('email_from'):
            result['email_from'] = context.get('email_from')
        if not result.get('email_to'):
            result['email_to'] = context.get('email_to')
        if not result.get('report_template'):
            result['report_template'] = context.get('report_template')
        return result

mail_compose_message_product_datasheet()

class send_datasheet(osv.osv_memory):
    _name = 'send.datasheet'
    _columns = {
        'contact_ids': fields.many2many('res.partner.contact', 'send_datasheet_partner_contact_rel', 'send_datasheet_id', 'contact_id', 'Contacts'),
        'send_all': fields.boolean('Send all records'),
        'product_id': fields.many2one('product.product', 'Product active')
    }
    def default_get(self, cr, uid, fields, context=None):
        """ To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        
        res = super(send_datasheet, self).default_get(cr, uid, fields, context=context)

        product_id = self.pool.get('product.product').browse(cr, uid, context.get('active_id', False), context=context).id
        if product_id:
            res['product_id'] = product_id

        return res
    def onchange_send_all(self, cr, uid, ids, send_all, product_id,context=None):
        res = {}
        if context is None:
            context = {}
        contact_ids = []
        shipments = []
        if product_id:
            if send_all and send_all == 1:

                shipments = self.pool.get('product.sheet.shipments').search(cr, uid, [('product_id','=', product_id)])
                if shipments:
                    for id in shipments:
                        ship_obj = self.pool.get('product.sheet.shipments').browse(cr, uid, id)
                        if ship_obj.contact_id:
                            contact_ids.append(ship_obj.contact_id.id)

                if contact_ids:
                    res['contact_ids'] = contact_ids
            elif send_all == 0:
                res['contact_ids'] = []

        return {'value': res}
    def open_mail(self, cr, uid, ids, context=None):
        if context is None: context = {}
        
        stream = []
        contacts = []
        emails_to = ''
        form_obj = self.pool.get('send.datasheet').browse(cr, uid, ids[0])
        if form_obj.contact_ids:
            for contact in form_obj.contact_ids:
                contacts.append(contact.id)
                if contact.email:
                    stream.append(contact.email)
            if stream:
                emails_to = u", ".join(stream)
                

        result = self.pool.get('ir.model.data')._get_id(cr, uid, 'eln_product', 'action_email_compose_message_product_wizard')
        id = self.pool.get('ir.model.data').read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = self.pool.get('ir.actions.act_window').read(cr, uid, [id])[0]
       
        result['context'] = str({'email_from': (self.pool.get('res.users').browse(cr, uid, uid) and \
                                                self.pool.get('res.users').browse(cr, uid, uid).user_email) \
                                                or (self.pool.get('res.users').browse(cr, uid, uid) and \
                                                self.pool.get('res.users').browse(cr, uid, uid).company_id and \
                                                self.pool.get('res.users').browse(cr, uid, uid).company_id.email) or False,
                                'email_to': emails_to or False,
                                'report_template': self.pool.get('ir.actions.report.xml').search(cr, uid, [('report_name','=', 'product.datasheet.jasper')])[0] or False,
                                'contact_ids': contacts
                                })

                                

        result.update({'target': 'new',
                        'nodestroy': False})

        return result
        
send_datasheet()