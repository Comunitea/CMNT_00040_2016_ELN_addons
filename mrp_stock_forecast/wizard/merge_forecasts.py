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
from openerp.osv import osv
from openerp.tools.translate import _

class merge_mrp_forecast(osv.osv_memory):
    _name = "merge.mrp.forecast"
    _description = "MRP Forecast Merge"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        if context is None:
            context={}
        res = super(merge_mrp_forecast, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if context.get('active_model','') == 'mrp.forecast' and len(context['active_ids']) < 2:
            raise osv.except_osv(_('Warning'),
            _('Please select multiple order to merge in the list view.'))
        return res

    def merge_orders(self, cr, uid, ids, context=None):
        """
             To merge similar type of purchases forecasts.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: purchase order view

        """
        order_obj = self.pool.get('mrp.forecast')
        #proc_obj = self.pool.get('procurement.order')
        mod_obj =self.pool.get('ir.model.data')
        if context is None:
            context = {}


        allorder = order_obj.do_merge(cr, uid, context.get('active_ids',[]), context)

        return {'type': 'ir.actions.act_window_close'}

merge_mrp_forecast()

class merge_stock_forecast(osv.osv_memory):
    _name = "merge.stock.forecast"
    _description = "Stock Forecast Merge"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        if context is None:
            context={}
        res = super(merge_stock_forecast, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if context.get('active_model','') == 'forecast.kg.sold' and len(context['active_ids']) < 2:
            raise osv.except_osv(_('Warning'),
            _('Please select multiple order to merge in the list view.'))
        return res

    def merge_orders(self, cr, uid, ids, context=None):
        """
             To merge similar type of purchases forecasts.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: purchase order view

        """
        order_obj = self.pool.get('forecast.kg.sold')
        #proc_obj = self.pool.get('procurement.order')
        mod_obj =self.pool.get('ir.model.data')
        if context is None:
            context = {}


        allorder = order_obj.do_merge(cr, uid, context.get('active_ids',[]), context)

        return {'type': 'ir.actions.act_window_close'}
merge_mrp_forecast()

