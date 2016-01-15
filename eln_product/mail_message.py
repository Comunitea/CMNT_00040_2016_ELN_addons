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
from osv import osv
import ast
import base64
import re
import logging


_logger = logging.getLogger('mail')

def to_email(text):
    """Return a list of the email addresses found in ``text``"""
    if not text: return []
    return re.findall(r'([^ ,<@]+@[^> ,]+)', text)

class mail_message(osv.osv):
    _inherit = 'mail.message'
    def send(self, cr, uid, ids, auto_commit=False, context=None):
        """Sends the selected emails immediately, ignoring their current
           state (mails that have already been sent should not be passed
           unless they should actually be re-sent).
           Emails successfully delivered are marked as 'sent', and those
           that fail to be deliver are marked as 'exception', and the
           corresponding error message is output in the server logs.

           :param bool auto_commit: whether to force a commit of the message
                                    status after sending each message (meant
                                    only for processing by the scheduler),
                                    should never be True during normal
                                    transactions (default: False)
           :return: True
        """

        if context is None:
            context = {}
        
        ir_mail_server = self.pool.get('ir.mail_server')
        self.write(cr, uid, ids, {'state': 'outgoing'}, context=context)
        for message in self.browse(cr, uid, ids, context=context):
            try:
                attachments = []
                for attach in message.attachment_ids:
                    attachments.append((attach.datas_fname, base64.b64decode(attach.datas)))

                body = message.body_html if message.subtype == 'html' else message.body_text
                body_alternative = None
                subtype_alternative = None
                if message.subtype == 'html' and message.body_text:
                    # we have a plain text alternative prepared, pass it to
                    # build_message instead of letting it build one
                    body_alternative = message.body_text
                    subtype_alternative = 'plain'

                to = to_email(message.email_to)
                for email in to:
                    msg = ir_mail_server.build_email(
                        email_from=message.email_from,
                        email_to=[email],
                        subject=message.subject,
                        body=body,
                        body_alternative=body_alternative,
                        email_cc=[],
                        email_bcc=[],
                        reply_to=message.reply_to,
                        attachments=attachments, message_id=message.message_id,
                        references = message.references,
                        object_id=message.res_id and ('%s-%s' % (message.res_id,message.model)),
                        subtype=message.subtype,
                        subtype_alternative=subtype_alternative,
                        headers=message.headers and ast.literal_eval(message.headers))
                    res = ir_mail_server.send_email(cr, uid, msg,
                                                    mail_server_id=message.mail_server_id.id,
                                                    context=context)
                    if res:
                        message.write({'state':'sent', 'message_id': res})
                        message_sent = True
                    else:
                        message.write({'state':'exception'})
                        message_sent = False

                    # if auto_delete=True then delete that sent messages as well as attachments
                    if message_sent and message.auto_delete:
                        self.pool.get('ir.attachment').unlink(cr, uid,
                                                              [x.id for x in message.attachment_ids \
                                                                    if x.res_model == self._name and \
                                                                       x.res_id == message.id],
                                                              context=context)

                message.unlink()
            except Exception:
                _logger.exception('failed sending mail.message %s', message.id)
                message.write({'state':'exception'})

            if auto_commit == True:
                cr.commit()
        return True
mail_message()