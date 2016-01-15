# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>). All Rights Reserved
#    $Id$
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

"""Modificamos las ventas para incluir el comportamiento de comisiones"""

from osv import fields, osv
from tools.translate import _

class sale_order_agent(osv.osv):
    _name = "sale.order.agent"
    _rec_name = "agent_id"

    def name_get(self, cr, uid, ids, context=None):
        """devuelve como nombre del agente del partner el nombre del agente"""
        if context is None: context = {}
        res = []
        for obj in self.browse(cr, uid, ids):
            res.append((obj.id, obj.agent_id.name))
        return res

    _columns = {
        'sale_id':fields.many2one('sale.order', 'Sale order', required=False, ondelete='cascade', help=''),
        'agent_id':fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id':fields.many2one('commission', 'Applied commission', required=True, help=''),
    }

    def onchange_agent_id(self, cr, uid, ids, agent_id):
        """al cambiar el agente cargamos sus comisión"""
        result = {}
        v = {}
        if agent_id:
            agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
            v['commission_id'] = agent.commission.id

        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id=False, commission_id=False):
        """al cambiar la comisión comprobamos la selección"""
        result = {}

        if commission_id:
            partner_commission = self.pool.get('commission').browse(cr, uid, commission_id)
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
                    if agent.commission.id !=  partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        result['warning']['message'] = _('A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
        return result

sale_order_agent()

class sale_order(osv.osv):
    """Modificamos las ventas para incluir el comportamiento de comisiones"""

    _inherit = "sale.order"

    _columns = {
        'sale_agent_ids':fields.one2many('sale.order.agent', 'sale_id', 'Agents', readonly=True, states={'draft': [('readonly', False)]})
    }

    def onchange_partner_id(self, cr, uid, ids, part):
        """heredamos el evento de cambio del campo partner_id para actualizar el campo agent_id"""
        sale_agent_ids=[]
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        sale_order_agent = self.pool.get('sale.order.agent')
        if ids:
            sale_order_agent.unlink(cr, uid, sale_order_agent.search(cr, uid ,[('sale_id','=',ids)]))
        if res.get('value', False) and part:
            partner = self.pool.get('res.partner').browse(cr, uid, part)
            for partner_agent in partner.commission_ids:
                vals={
                    'agent_id':partner_agent.agent_id.id,
                    'commission_id':partner_agent.commission_id.id,
                    #'sale_id':ids
                }
                if ids:
                    for id in ids:
                        vals['sale_id']=id
                sale_agent_id=sale_order_agent.create(cr, uid, vals)
                sale_agent_ids.append(int(sale_agent_id))
            res['value']['sale_agent_ids'] =  sale_agent_ids
        return res


    def action_ship_create(self, cr, uid, ids, context=None):
        """extend this method to add agent_id to picking"""
        res = super(sale_order, self).action_ship_create(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids):
            pickings = [x.id for x in order.picking_ids]
            agents = [x.agent_id.id for x in order.sale_agent_ids]
            if pickings and agents:
                self.pool.get('stock.picking').write(cr, uid, pickings, {'agent_ids': [[6, 0, agents]] })
        return res

    def create(self, cr, uid, values, context=None):
        """
        Para que el cliente gtk no borre el agente al darle a guardar
        """
        res = super(sale_order, self).create(cr, uid, values, context=context)
        if 'sale_agent_ids' in values:
            for sale_order_agent in values['sale_agent_ids']:
                if sale_order_agent[1]:
                    self.pool.get('sale.order.agent').write(cr, uid, [sale_order_agent[1]], {'sale_id':res})
        return res

sale_order()

class sale_line_agent(osv.osv):
    _name = "sale.line.agent"
    _rec_name = "agent_id"

    _columns = {
        'line_id':fields.many2one('sale.order.line', 'Sale order line', required=False, ondelete='cascade', help=''),
        'agent_id':fields.many2one('sale.agent', 'Agent', required=True, ondelete='cascade', help=''),
        'commission_id':fields.many2one('commission', 'Applied commission', required=True, help=''),
    }

    def onchange_agent_id(self, cr, uid, ids, agent_id):
        """al cambiar el agente cargamos sus comisión"""
        result = {}
        v = {}
        if agent_id:
            agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
            v['commission_id'] = agent.commission.id

        result['value'] = v
        return result

    def onchange_commission_id(self, cr, uid, ids, agent_id=False, commission_id=False):
        """al cambiar la comisión comprobamos la selección"""
        result = {}

        if commission_id:
            partner_commission = self.pool.get('commission').browse(cr, uid, commission_id)
            if partner_commission.sections:
                if agent_id:
                    agent = self.pool.get('sale.agent').browse(cr, uid, agent_id)
                    if agent.commission.id !=  partner_commission.id:
                        result['warning'] = {}
                        result['warning']['title'] = _('Fee installments!')
                        result['warning']['message'] = _('A commission has been assigned by sections that does not match that defined for the agent by default, so that these sections shall apply only on this bill.')
        return result
sale_line_agent()


class sale_order_line(osv.osv):
    """Modificamos las lineas ventas para incluir las comisiones en las facturas creadas desde ventas"""

    _inherit = "sale.order.line"
    _columns = {
         'line_agent_ids':fields.one2many('sale.line.agent', 'line_id', 'Agents', states={'draft': [('readonly', False)]})
    }

    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context)
        for inv_line in self.pool.get('account.invoice.line').browse(cr, uid, res):
            list_ids = [x.id for x in inv_line.commission_ids]
            self.pool.get('invoice.line.agent').calculate_commission(cr,uid,list_ids)
        return res

    def _create_invoice_line_agent(self,cr,uid,ids,agent_id,commission_id):
        vals = {
            'agent_id' : agent_id,
            'commission_id' :commission_id,
            'settled': False
        }
        line_agent_id=self.pool.get('invoice.line.agent').create(cr, uid, vals)
        return line_agent_id

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order_line,self)._prepare_order_line_invoice_line(cr,uid,line,account_id,context)
        list_ids = []
        if not line.product_id.commission_exent:
            if not line.line_agent_ids: #si la linea no tiene comissiones arrastro los del pedido a la linea de factura
                for so_comm in line.order_id.sale_agent_ids:
                    line_agent_id= self._create_invoice_line_agent(cr,uid,[],so_comm.agent_id.id,so_comm.commission_id.id)
                    list_ids.append(line_agent_id)

            else:
                for l_comm in line.line_agent_ids:
                    line_agent_id= self._create_invoice_line_agent(cr,uid,[],l_comm.agent_id.id,l_comm.commission_id.id)
                    list_ids.append(line_agent_id)
        res['commission_ids'] = [(6,0,list_ids)]
        return res

    def _create_line_commission(self,cr,uid,ids,agent_id,commission_id):
        sale_line_agent = self.pool.get("sale.line.agent")
        vals={
            'agent_id' : agent_id,
            'commission_id' : commission_id
        }
        if ids:
            vals['line_id'] = ids[0]
        return sale_line_agent.create(cr,uid,vals)
    def product_id_change2(self, cr, uid, ids,pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,sale_agent_ids=False,context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name, partner_id,lang, update_tax, date_order,packaging,fiscal_position,flag,context)
        if product:
            list_agent_ids = []
            product_obj = self.pool.get("product.product").browse(cr,uid,product)
            # order_obj = self.pool.get("sale.order").browse(cr,uid,context['order_id'])
            sale_line_agent = self.pool.get("sale.line.agent")
            if ids:
                sale_line_agent.unlink(cr,uid,sale_line_agent.search(cr,uid,[('line_id','in',ids)]))
                res['value']['line_agent_ids'] = []
            if not product_obj.commission_exent and sale_agent_ids:
                order_comm_ids = [x[1] for x in sale_agent_ids if x[0] != 2 and x[1]]
                if order_comm_ids:
                    order_agent_ids = [ x.agent_id.id for x in self.pool.get("sale.order.agent").browse(cr,uid,order_comm_ids)]
                    # order_agent_ids = [x.agent_id.id for x in order_obj.sale_agent_ids]
                    dic= {}
                    for prod_record in product_obj.product_agent_ids:
                        if not prod_record.agent_ids: #no hay agentes especificados para la comisión: se usan los agentes del pedido
                            for agent_id in order_agent_ids:
                                if agent_id not in dic:
                                    dic[agent_id] = prod_record.commission_id.id
                        else:
                            for agent_id in prod_record.agent_ids:
                                if agent_id.id in order_agent_ids:
                                    dic[agent_id.id] = prod_record.commission_id.id

                    for k in dic:
                        line_agent_id = self._create_line_commission(cr,uid,ids,k,dic[k])
                        list_agent_ids.append(int(line_agent_id))
                    res['value']['line_agent_ids'] = list_agent_ids
        return res

    def create(self, cr, uid, values, context=None):
        """
        Para que el cliente gtk no borre el agente de la linea al darle a guardar
        """
        res = super(sale_order_line, self).create(cr, uid, values, context=context)
        if 'line_agent_ids' in values:
            for sale_line_agent in values['line_agent_ids']:
                self.pool.get('sale.line.agent').write(cr, uid, sale_line_agent[1], {'line_id':res})
        return res

sale_order_line()
