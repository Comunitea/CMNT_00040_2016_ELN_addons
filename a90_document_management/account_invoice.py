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


#class account_invoice_refund(osv.osv_memory):
#    _inherit = 'account.invoice.refund'
#    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
#        """
#        @param cr: the current row, from the database cursor,
#        @param uid: the current user’s ID for security checks,
#        @param ids: the account invoice refund’s ID or list of IDs
#
#        """
#        inv_obj = self.pool.get('account.invoice')
#
#        if context is None:
#            context = {}
#
#        result = super(account_invoice_refund, self).compute_refund(cr, uid, ids, mode, context)
#        # An example of result['domain'] computed by the parent wizard is:
#        # [('type', '=', 'out_refund'), ('id', 'in', [43L, 44L])]
#        # The created refund invoice is the first invoice in the ('id', 'in', ...) tupla
#        created_inv = [x[2] for x in result['domain'] if x[0] == 'id' and x[1] == 'in']
#        if context.get('active_ids') and created_inv and created_inv[0]:
#            for form in self.read(cr, uid, ids, context=context):
#                refund_inv_id = created_inv[0][0]
#                ref = inv_obj.browse(cr, uid, refund_inv_id)
#                if ref.x_expedient_id:
#                    for id in context.get('active_ids'):
#                        inv = inv_obj.browse(cr, uid, id)
#                        if inv.x_expedient_id:
#                            self.pool.get('expedient').write(cr, uid, [inv.x_expedient_id.id],{'parent_expedient': ref.x_expedient_id.id})
#
#        return result
#account_invoice_refund()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    SELECT = [
            ('no_exp', 'No expedient'),
            ('created', 'Created'),
            ('incomplete', 'Incomplete'),
            ('completed', 'Completed'),
            ('printed', 'Printed'),
            ('finalized', 'Finalized')]

    def _get_expedient_state(self, cr, uid, ids, name, arg, context=None):
        res = {}

        for inv in self.browse(cr, uid, ids):
            if 'x_expedient_id' in inv and inv.x_expedient_id:
                res[inv.id] = inv.x_expedient_id.state
            else:
                res[inv.id] = 'no_exp'
        return res

    def _get_partner_name(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids):
            res[invoice.id] = invoice.partner_id.name

        return res

    def _search_by_state(self, cr, uid, obj, name, args, context):
        if not len(args):
            return []
        ids = []
        # ids = self.search(cr,uid, [('exp_state2','=',args[0][2])])
        # import ipdb; ipdb.set_trace()
        if 'no_exp' in args[0][2]:
            field_ids = self.pool.get('ir.model.fields').search(cr,uid,[('name', '=', 'x_expedient_id'),('model', '=', 'account.invoice')])
            if field_ids:
                ids = self.pool.get("account.invoice").search(cr,uid,[('x_expedient_id','=',False)])
            else:
                ids = []
        else:
            expedient_ids = self.pool.get("expedient").search(cr, uid,[('state','=',args[0][2]), ('references','like','account.invoice')])
            for exp in self.pool.get("expedient").browse(cr,uid,expedient_ids):
                inv_id = int(exp.references.split(',')[1])
                ids.append(inv_id)
        return [('id', 'in', ids)]

    def _get_invoice(self, cr, uid, ids, context={}):
        result = {}
        invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id', 'in', ids)])
        return invoice_ids

    _columns = {
        'wzd_name': fields.char('Wzd Name', size=255),
        'printed': fields.boolean('Printed', readonly=True),
        'partner_name': fields.function(_get_partner_name, method=True, string='Partner name', type="char", size=255, readonly=True,
                                        store={'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['partner_id'], 10),
                                               'res.partner': (_get_invoice, ['name'], 10),}),
        'exp_state': fields.function(_get_expedient_state, method=True, type="selection", selection=SELECT, string="Expedient state",readonly=True,fnct_search=_search_by_state),
    }

    def write(self, cr, uid, ids, vals, context=None):

        if context is None: context = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        for current_obj in self.browse(cr, uid, ids):

            if 'x_expedient_id' in self._columns:
                if current_obj.x_expedient_id:
                    if current_obj.date_invoice:
                        self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'date_origin_model': str(current_obj.date_invoice)},context=context)
                    if current_obj.partner_id:
                        self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'partner_name_expedient': (current_obj.partner_id and current_obj.partner_id.name or '')},context=context)
                    if current_obj.number:
                        self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'name_origin_model': current_obj.number},context=context)


        return res
    def create(self, cr, uid, vals, context=None):

        res = super(account_invoice, self).create(cr, uid, vals, context)
        if res:
            current_obj = self.browse(cr, uid, res)
            if current_obj:
                if 'x_expedient_id' in self._columns:
                    if current_obj.x_expedient_id:
                        if current_obj.date_invoice:
                            self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'date_origin_model': str(current_obj.date_invoice)},context=context)
                        if current_obj.partner_id:
                            self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'partner_name_expedient': (current_obj.partner_id and current_obj.partner_id.name or '')},context=context)
                        if current_obj.number:
                            self.pool.get('expedient').write(cr, uid, [current_obj.x_expedient_id.id],{'name_origin_model': current_obj.number},context=context)

        return res
