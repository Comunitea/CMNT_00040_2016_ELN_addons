# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Pedro Gómez$ <pegomez@elnogal.com>
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
from tools.translate import _

class res_partner_address(osv.osv):

    _inherit = 'res.partner.address'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner Name', ondelete='cascade', select=True, help="Keep empty for a private address, not related to partner."),
        'comercial': fields.char('Nombre comercial', size=128, select=True), # Nombre Comercial de la dirección del partner,
        'mobile2': fields.char('Mobile phone', size=64), # Teléfono de la partner.address. El mobile es el del contacto asociado a la partner.address,
    }

    def name_get(self, cr, uid, ids, context=None):
        result = {}
        for rec in self.browse(cr,uid, ids, context=context):
            res = []
            #import ipdb; ipdb.set_trace()
            if rec.partner_id:
                res.append(rec.partner_id.name_get()[0][1])
            if rec.comercial:
                res.append(rec.comercial)
            if rec.contact_id and rec.contact_id.name:
                res.append(rec.contact_id.name)
            if rec.street:
                res.append(rec.street)
            if rec.street2:
                res.append(rec.street2)

            #if rec.location_id:
            #    if rec.location_id.city: res.append(rec.location_id.city)
            #    if rec.location_id.country_id: res.append(rec.location_id.country_id.name_get()[0][1])
            # cambiamos las de arriba por las dos de abajo
            if rec.city:
                res.append(rec.city)
            if rec.country_id:
                res.append(rec.country_id.name_get()[0][1])
            result[rec.id] = ', '.join(res)
        return result.items()

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        elif context.get('contact_display', 'contact') == 'partner':
            ids = self.search(cr, user, [('partner_id', operator, name)] + args, limit=limit, context=context)
        else:
            # first lookup zip code, as it is a common and efficient way to search on these data
            ids = self.search(cr, user, [('zip', '=', name)] + args, limit=limit, context=context)
            # then search on other fields:
            if context.get('contact_display', 'contact') == 'partner_address':
                fields = ['partner_id', 'name', 'country_id', 'city', 'street', 'street2', 'comercial']
            else:
                fields = ['name', 'country_id', 'city', 'street', 'street2', 'comercial']
            # Here we have to search the records that satisfy the domain:
            #       OR([[(f, operator, name)] for f in fields])) + args
            # Searching on such a domain can be dramatically inefficient, due to the expansion made
            # for field translations, and the handling of the disjunction by the DB engine itself.
            # So instead, we search field by field until the search limit is reached.
            while (not limit or len(ids) < limit) and fields:
                f = fields.pop(0)
                new_ids = self.search(cr, user, [(f, operator, name)] + args,
                                      limit=(limit-len(ids) if limit else limit),
                                      context=context)
                # extend ids with the ones in new_ids that are not in ids yet (and keep order)
                old_ids = set(ids)
                ids.extend([id for id in new_ids if id not in old_ids])

        if limit:
            ids = ids[:limit]
        return self.name_get(cr, user, ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):

        default = default or {}
        address_reg = self.browse(cr, uid, id)

        dir_copy = {
                'street': address_reg.street or False,
                'street2': address_reg.street2 or False,
                'zip': address_reg.zip or False,
                'city': address_reg.city or False,
                'country_id': address_reg.country_id.id or False,
                'state_id': address_reg.state_id.id or False
                }

        default.update({'location_id' : False})
        default.update(dir_copy)
        
        return super(res_partner_address, self).copy(cr, uid, id, default, context)

    def copy_data(self, cr, uid, id, default=None, context=None):

        default = default or {}        
        address_reg = self.browse(cr, uid, id)

        dir_copy = {
                'street': address_reg.street or False,
                'street2': address_reg.street2 or False,
                'zip': address_reg.zip or False,
                'city': address_reg.city or False,
                'country_id': address_reg.country_id.id or False,
                'state_id': address_reg.state_id.id or False
                }
        
        default.update({'location_id' : False})
        default.update(dir_copy)

        return super(res_partner_address, self).copy_data(cr, uid, id, default, context)

    def create(self, cr, uid, vals, context=None):
        '''override create to set company of address = company of the partner'''

        if vals.get('partner_id', False):
            partner_obj = self.pool.get('res.partner').browse(cr, uid, vals.get('partner_id'))
            vals.update({'company_id' : partner_obj.company_id.id})

        if vals.get('location_id', False): #Para que siempre se cree una localización nueva. Fallaba al crear direccion desde un many2one que usaba la que había seleccionada
            vals.update({'location_id' : False})
        
        return super(res_partner_address, self).create(cr, uid, vals, context)

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        '''Si la dirección tiene partner asociado, la compañía tiene que ser la misma'''
        res = {}
        
        if partner_id:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
            res['company_id'] = partner_obj.company_id.id

        return {'value': res}

    def onchange_company_id(self, cr, uid, ids, company_id, partner_id, context=None):
        '''Si la dirección tiene partner asociado, la compañía tiene que ser la misma'''
        res = {}
        warning = {}
        
        if partner_id:
            partner_obj = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner_obj.company_id.id != company_id:
                res['company_id'] = partner_obj.company_id.id
                warning = {
                    'title': _('Warning!'),
                    'message' : _('You can not change the company of the address. It must be the same as the company of the partner to which it belongs.')
                            }

        return {'value': res, 'warning': warning}

res_partner_address()




