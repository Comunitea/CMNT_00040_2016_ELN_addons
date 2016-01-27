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


class mrp_bom(osv.osv):
    _inherit = "mrp.bom"


    # def search(self, cr, uid, args, offset=0, limit=None, order=None,
    #            context=None, count=False):
    #     """ Overwrite in order to search only location of a unique product
    #         if search_product_id is in context."""
    #     import ipdb; ipdb.set_trace()
    #     if context.get('split', False):
    #         loc_ids = context.get('split', False).split(',')
    #         args.append(['id', 'in', loc_ids])
    #     res = super(copy_product_ldm, self).search(cr, uid, args,
    #                                               offset=offset,
    #                                               limit=limit,
    #                                               order=order,
    #                                               context=context,
    #                                               count=count)
    #
    #     return res


    def name_search(self, cr, uid, name,
                    args=None, operator='ilike', context=None, limit=80):

        if context.get('split', False):
            loc_ids = context.get('split', False).split(',')
            args.append(['id', 'in', loc_ids])
        res = super(mrp_bom, self).name_search(cr, uid, name, args=args,
                                                      operator=operator,
                                                      limit=limit)
        return res

class copy_product_ldm(osv.osv_memory):

    _name = "copy.product.ldm"
    _columns = {
        'product_ldm_id': fields.many2one('mrp.bom', string='LdM', required=True),
        'ldm_ids_str': fields.char('LdM ids str', size=255),
        #'ldm_ids' : fields.one2many('mrp.bom', 'bom_id')

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
        stream = []    
        res = super(copy_product_ldm, self).default_get(cr, uid, fields, context=context)
        ldm_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id','=',context.get('active_id', False))], context=context)

        if ldm_ids:
            for id in ldm_ids:
                stream.append(str(id))
            if stream:
                res['ldm_ids_str'] = u", ".join(stream)
            else:
                res['ldm_ids_str'] = "0"
        else:
            res['ldm_ids_str'] = False
        return res

    def _get_bom_lines(self, bom):

        bom_lines = []
        for bom in bom.bom_line_ids:
            if bom.product_id.bom_ids:
                x = self._get_bom_lines(bom.product_id.bom_ids[0])
                if x:
                    for id in x:
                        bom_lines.append(id)
            else:
                bom_lines.append(bom.id)

        res = list(set(bom_lines))
        return res

    def copy_ldm_to_ingredients(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        bom_lines = []
        form_obj = self.browse(cr, uid, ids, context=context)[0]
        if form_obj.product_ldm_id:
            if form_obj.product_ldm_id.bom_line_ids:
                bom_lines = self._get_bom_lines(form_obj.product_ldm_id)

        if bom_lines:
            #bom_lines = list(set(bom_lines))
            for z in bom_lines:
                obj = self.pool.get('mrp.bom.line').browse(cr, uid, z)
                self.pool.get('product.ingredient').create(cr, uid, {
                    'product_parent_id': form_obj.product_ldm_id and form_obj.product_ldm_id.product_id.id or False,
                    'product_id': obj.product_id.id,
                    'name': obj.product_id.name,
                    'product_qty': obj.product_qty
                    })
                    
        return {'type': 'ir.actions.act_window_close'}
