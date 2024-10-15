# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    Copyright (C) 2015-2016 Comunitea Servicios Tecnológicos All Rights Reserved
#    $kiko sánchez$ <kiko@comunitea.com>
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
from odoo.osv import orm, fields
from odoo.addons import decimal_precision as dp


class budget_line(orm.Model):
    #TODO: TRADUCIR -> Se añade el campo producto para poder añadir líneas
    #al presupuesto por producto. Creadas a partir de las previsiones previamente
    #creadas y aprobadas.
    _inherit = 'budget.line'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
    }


class budget_item(orm.Model):
    MODELS = [('sales.forecast', 'Sales forecast'), ('forecast.kg.sold', 'Kg sold forecast'), ('mrp.forecast', 'Hour forecast')]
    TYPES = [('euros', '€'), ('units', 'Uds'), ('kg', 'Kg'), ('min','Mins')]
    _inherit = "budget.item"
    _columns = {
        'distribution_mode': fields.reference('Forecast', MODELS, size=128),
        'type_c': fields.selection(TYPES, 'type',required=False)
    }

class budget_version_total2(orm.Model):
    _name = "budget.version.total2"

    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'budget_item_id': fields.many2one('budget.item', 'Item', readonly=True),
        'version_id': fields.many2one('budget.version', 'Version', readonly=True),
        'total': fields.float('Total', readonly=True,digits_compute=dp.get_precision('Purchase Price'),),


    }
    _defaults = {
        'name': '/',
    }

class budget_version(orm.Model):
    _inherit = 'budget.version'

    #def _get_totals(self, cr, uid, ids, field_name, arg, context=None):
        #"""gets other service order with same product and serial number"""
        #result = {}
        #lines = self.pool.get('budget.line')
        #total = self.pool.get('budget.version.total2')
        #item_facade = self.pool.get('budget.item')
        #lines = []

        #for version in self.browse(cr, uid, ids):
            #if version.budget_line_ids:
                #cr.execute("""
                #SELECT sum(amount),budget_item_id FROM budget_line GROUP BY budget_item_id""")
                #items = cr.fetchall()
                #if items:
                    #for res in items:
                        #field = u''
                        #model = u''
                        #parent = u''
                        #tot_prev = 0.0
                        #item_obj = item_facade.browse(cr, uid, res[1])

                        #if item_obj.distribution_mode:
                            #prevfac = item_obj.distribution_mode
                            #if 'kgsold_forecast_lines' in prevfac._columns:
                                #model = u'forecast_kg_sold_line'
                                #parent = u'kgsold_forecast_id'
                                #field = u"total_kg"
                                #name = version.name + '/' + item_obj.name + u" - €/kg"
                            #elif 'sales_forecast_lines' in prevfac._columns:
                                #model = u'sales_forecast_line'
                                #parent = u'sales_forecast_id'
                                #if item_obj.type_c == 'units':
                                    #field = 'total_qty'
                                    #name = version.name + '/' + item_obj.name + u" - €/Units"
                                #elif item_obj.type_c == 'euros':
                                    #field = 'total_amount'
                                    #name = version.name + '/' + item_obj.name + u" - €/€"
                            #elif 'mrp_forecast_lines' in prevfac._columns:
                                #model = u'mrp_forecast_line'
                                #parent = u'mrp_forecast_id'
                                #field = u"total_hours"
                                #name = version.name + '/' + item_obj.name + u" - €/Mins"
                            #if field and model and parent and name:
                                #cr.execute(""" SELECT sum("""+field+""") from """ + model + """ where """ + parent + """ = """ + str(prevfac.id) + """""")
                                #tot_prev = cr.fetchall()[0][0]

                                #ids_to_delete = total.search(cr, uid, [('budget_item_id','=', res[1]),('version_id','=',version.id)])
                                #if ids_to_delete:
                                    #total.unlink(cr, uid, ids_to_delete)
                                #new_total_id = total.create(cr, uid, {'budget_item_id': res[1], 'version_id':version.id, 'total': round(float(res[0])/ float(tot_prev or 1.0), 2), 'name': name})
                                #lines.append(new_total_id)
            #if lines:
                #result[version.id] = lines
            #else:
                #result[version.id] = []

        #return result

    _columns = {
        'version_total': fields.one2many('budget.version.total2', 'version_id', string="Totals")

    }


    def action_calculate_totals(self, cr, uid, ids, properties=[],context=None):
        result = {}
        lines = self.pool.get('budget.line')
        total = self.pool.get('budget.version.total2')
        item_facade = self.pool.get('budget.item')
        lines = []
        #3 previsiones
        #prevision de ventas: modelo sales_forecast_lines en euros o kgrs
        #prevision de kgrs: modelo kgsold_forecast_line en kgr
        #prevision de mrp_forecast_lines en tiempo de fabricación

        for version in self.browse(cr, uid, ids):
            if version.budget_line_ids:
                #recuperamos todas las lineas agrupadas por partidas presupestarias
                # select sum(total_hours) from mrp_forecast_line where mrp_forecast_id =
                cr.execute("""
                SELECT sum(amount),budget_item_id FROM budget_line GROUP BY budget_item_id""")
                items = cr.fetchall()
                if items:
                    for res in items:
                        field = u''
                        model = u''
                        parent = u''
                        tot_prev = 0.0
                        item_obj = item_facade.browse(cr, uid, res[1])
                        #instanciamos cada partida presupuestaria

                        if item_obj.distribution_mode:
                            #tipo de previsión
                            prevfac = item_obj.distribution_mode
                            if 'kgsold_forecast_lines' in prevfac._columns:
                                model = u'forecast_kg_sold_line'
                                parent = u'kgsold_forecast_id'
                                field = u"total_kg"
                                name = version.name + '/' + item_obj.name + u" - €/kg"
                            elif 'sales_forecast_lines' in prevfac._columns:
                                model = u'sales_forecast_line'
                                parent = u'sales_forecast_id'
                                if item_obj.type_c == 'units':
                                    field = 'total_qty'
                                    name = version.name + '/' + item_obj.name + u" - €/Units"
                                elif item_obj.type_c == 'euros':
                                    field = 'total_amount'
                                    name = version.name + '/' + item_obj.name + u" - €/€"
                            elif 'mrp_forecast_lines' in prevfac._columns:
                                model = u'mrp_forecast_line'
                                parent = u'mrp_forecast_id'
                                field = u"total_hours"
                                name = version.name + '/' + item_obj.name + u" - €/Mins"
                            if field and model and parent and name:
                                cr.execute(""" SELECT sum("""+field+""") from """ + model + """ where """ + parent + """ = """ + str(prevfac.id) + """""")
                                tot_prev = cr.fetchall()[0][0]
                                ids_to_delete = total.search(cr, uid, [('budget_item_id','=', res[1]),('version_id','=',version.id)])
                                if ids_to_delete:
                                    total.unlink(cr, uid, ids_to_delete)
                                new_total_id = total.create(cr, uid, {'budget_item_id': res[1], 'version_id':version.id, 'total': round(float(res[0])/ float(tot_prev or 1.0), 2), 'name': name})
        return True
