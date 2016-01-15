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

from osv import osv, fields
from dateutil.relativedelta import relativedelta
from datetime import datetime
class rappel_renovation(osv.osv_memory):
    _name = 'rappel.renovation'
    _columns = {
        'exception_partners':fields.many2many('res.partner','renew_rappel_partners_rel','renew_rappel_id','partner_id','Exception partners'),
        'rappel_ids': fields.many2many('rappel', 'rappel_renew_rappel_rel', 'renew_rappel_id', 'rappel_id', 'Rappels to renew', domain=[('state','=','done')], required=True),
        'categ_ids': fields.many2many('product.category','rappel_renew_categ_product','renew_rappel_id','categ_id', 'Categ. Product'),
        'by_categ': fields.boolean('By categ')
    }

    def renew_rappels(self, cr, uid, ids, context=None):
        form_obj = self.browse(cr, uid, ids, context=context)[0]
        partner_obj = self.pool.get('res.partner')
        rappels = []

        if form_obj.by_categ:
            rappel_lines = self.pool.get('rappel.line').search(cr, uid, [('condition_category_id','in',[x.id for x in form_obj.categ_ids])])
            if rappel_lines:
                for line in rappel_lines:
                    rappels.append(self.pool.get('rappel.line').browse(cr, uid, line).rappel_id.id)

            if rappels:
                partner_rappels = partner_obj.search(cr, uid, [('rappel_id','!=', False),('rappel_id','in', rappels)])
                if partner_rappels:
                    if form_obj.exception_partners:
                        for partner in form_obj.exception_partners:
                            if partner.id in partner_rappels:
                                partner_rappels.remove(partner.id)
                for rap in rappels:
                    lines = []
                    rappel = self.pool.get('rappel').browse(cr, uid, rap)
                    date_start = (datetime.strptime(rappel.date_start, "%Y-%m-%d") + relativedelta(months=12)).strftime("%Y-%m-%d")
                    date_stop = (datetime.strptime(rappel.date_stop, "%Y-%m-%d") + relativedelta(months=12)).strftime("%Y-%m-%d")
                    for l in rappel.line_ids:
                        if l.id in rappel_lines:
                            newline = self.pool.get('rappel.line').copy(cr, uid, l.id)
                            lines.append(newline)
                    new_rappel_id = self.pool.get('rappel').copy(cr, uid, rappel.id,{'date_start': date_start, 'date_stop': date_stop, 'line_ids':[(6,0,lines)]})
                    partners = partner_obj.search(cr, uid, [('rappel_id','=', rappel.id)])
                    if partners:
                        for part in partners:
                            if part in partner_rappels:
                                partner_obj.write(cr, uid, part,{'rappel_id': new_rappel_id})
                    
        else:
            partner_rappels = partner_obj.search(cr, uid, [('rappel_id','!=', False),('rappel_id','in', [x.id for x in form_obj.rappel_ids])])

            if partner_rappels:
                if form_obj.exception_partners:
                    for partner in form_obj.exception_partners:
                        if partner.id in partner_rappels:
                            partner_rappels.remove(partner.id)

            for rappel in form_obj.rappel_ids:
                date_start = (datetime.strptime(rappel.date_start, "%Y-%m-%d") + relativedelta(months=12)).strftime("%Y-%m-%d")
                date_stop = (datetime.strptime(rappel.date_stop, "%Y-%m-%d") + relativedelta(months=12)).strftime("%Y-%m-%d")
                new_rappel_id = self.pool.get('rappel').copy(cr, uid, rappel.id,{'date_start': date_start, 'date_stop': date_stop})
                partners = partner_obj.search(cr, uid, [('rappel_id','=', rappel.id)])
                if partners:
                    for part in partners:
                        if part in partner_rappels:
                            partner_obj.write(cr, uid, part,{'rappel_id': new_rappel_id})

        return {'type': 'ir.actions.act_window_close'}

rappel_renovation()