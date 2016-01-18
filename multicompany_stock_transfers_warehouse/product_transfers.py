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
import decimal_precision as dp
import time
from openerp import netsvc
from tools.translate import _

class multicompany_moves_rel(osv.osv):
    _name = 'multicompany.moves.rel'
    _rec_name = 'move_in_id'
    _columns = {
        'move_in_id': fields.many2one("stock.move",'Related move in', readonly=True),
    }
    
multicompany_moves_rel() 

class stock_move(osv.osv):   
    _inherit = "stock.move"    
    _columns = {
        'related_company_move_id': fields.many2one("multicompany.moves.rel",'Related move', readonly=True)
    }
    
stock_move()

class stock_picking(osv.osv):   
    _inherit = "stock.picking"    
    _columns = {
        'is_transfer': fields.boolean("Is Transfer")
    }
    
stock_picking()

class product_transfer(osv.osv):
    _name = 'product.transfers'

    def _get_wharehouse_id_name(self, cr, uid, context=None):
        if context is None:
            context = {}
        user_company_id  = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        cr.execute("select id, name from stock_warehouse where company_id != %s" % str(user_company_id) )
        tup = [(str(x[0]),x[1]) for x in cr.fetchall()]
        return tup

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_ids': fields.one2many('wzd.transfers.product.rel', 'product_tranfer_id','Products to tranfer', required=True),
#       'orig_warehouse_id': fields.many2one('stock.warehouse', 'Source warehouse', required=True),
        'orig_warehouse_id': fields.selection(_get_wharehouse_id_name, 'Source warehouse', required=True),
        'dest_warehouse_id': fields.many2one('stock.warehouse', 'Dest. warehouse', required=True),
        'transfer_location_id': fields.many2one('stock.location', 'Tranfer location', required=True),
        'journal_id': fields.many2one('stock.journal', 'Journal', required=True),
        'bill_output': fields.boolean('Bill output'),
        'bill_entry': fields.boolean('Bill entry'),
        'automatic_execution': fields.boolean('Automatic execution'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'date_planned': fields.datetime('Date Planned'),
        'state': fields.selection([
            ('draft','Draft'),
            ('transferred', 'Transferred')], 'State', readonly=True)
    }
    _defaults = {
        'transfer_location_id': lambda self, cr, uid, c: self.pool.get('ir.model.data').get_object_reference(cr,uid,"multicompany_stock_transfers_warehouse","location_transfers")[1],
        'journal_id': lambda self, cr, uid, c: self.pool.get('ir.model.data').get_object_reference(cr,uid,"multicompany_stock_transfers_warehouse","journal_transfers_hpaniagua")[1],
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.transfer', context=c),
        'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft'
    }
    
    def prepare_picking_transfer(self, cr, uid, ids, origin, company, picking_type, line, notep, bill, address, warehouse):

        return {
                'origin': origin,
                'company_id': company or False,
                'type': picking_type,
                'stock_journal_id': line.journal_id and line.journal_id.id or False,
                'move_type': 'one',
                'note': notep,
                'invoice_state': bill,
                'address_id': address,
                'is_transfer' : True
                }

    def prepare_pickings(self,cr,uid,ids,trans,obj_warehouse,transfer1,transfer2,wf_service,move_in_ids,move_out_ids,is_pick_in):
        picking_obj=self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        if trans.bill_entry:
                bill = '2binvoiced'
        else:
            bill = 'none'

        origin = is_pick_in and (trans.name) + ':' + transfer1 or (trans.name) + ':' + transfer2
        company = is_pick_in and trans.dest_warehouse_id.company_id.id or obj_warehouse.company_id.id
        picking_type = is_pick_in and 'in' or 'out'
        notep = is_pick_in and _('Picking for pulled procurement coming from original warehouse %s, pull rule %s, via original Procurement %s') % (obj_warehouse.name, transfer1, trans.name) or  _('Picking for pulled procurement coming from original warehouse %s, pull rule %s, via original Procurement %s') % (obj_warehouse.name, transfer2, trans.name),
        if trans.dest_warehouse_id.partner_address_id or obj_warehouse.partner_address_id:
            address = is_pick_in and obj_warehouse.partner_address_id.id or trans.dest_warehouse_id.partner_address_id.id
        else:
            raise osv.except_osv(_('Warning'), _("The warehouse of entry needs to have the address of the owner configured."))
        warehouse = is_pick_in and trans.dest_warehouse_id.id or obj_warehouse.id
        picking_id = picking_obj.create(cr, uid, self.prepare_picking_transfer(cr, uid, ids, 
                                                                                    origin,
                                                                                    company,
                                                                                    picking_type,
                                                                                    trans,
                                                                                    notep,
                                                                                    bill,
                                                                                    address,
                                                                                    warehouse)) 

        if is_pick_in:
            move_obj.write(cr,uid,move_in_ids,{'picking_id' : picking_id})
        else:
            move_obj.write(cr,uid,move_out_ids,{'picking_id' : picking_id})
        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
      
        if trans.automatic_execution:
            picking_obj.force_assign(cr, uid, [picking_id])
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_done', cr)

    def execute_transfer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        picking_obj=self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")
        proc_obj = self.pool.get('procurement.order')

        for trans in self.browse(cr, uid, ids, context=context):
            obj_warehouse = self.pool.get('stock.warehouse').browse(cr,1,int(trans.orig_warehouse_id),context)
            transfer1 = "Entrada en " + trans.dest_warehouse_id.company_id.name
            transfer2 = "Salida de " + obj_warehouse.company_id.name
            picking_type = ''
            notep = ''
            notem = ''
            noteproc = ''
            bill = ''
            address = False
            warehouse = False
            move_in_ids = []
            move_out_ids = []
            usr_uid = uid
            for product in trans.product_ids:
                
                if product.product_id.company_id and product.product_id.company_id.id == trans.dest_warehouse_id.company_id.id:
                    raise osv.except_osv(_('Warning'), _("Product %s must not belong to the company %s if you whant transfer it.") % (product.product_id.name, trans.dest_warehouse_id.company_id.name))

                first = 0
                while first < 2:
                    if first == 0:
                        origin = (trans.name) + ':' + transfer1
                        company = trans.dest_warehouse_id.company_id.id
                        notem = _('Move for pulled procurement coming from original warehouse %s, pull rule %s, via original Procurement %s') % (obj_warehouse.name, transfer1, trans.name),
                        noteproc = _('Pulled procurement coming from original warehouse %s, pull rule %s, via original Procurement %s') % (obj_warehouse.name, transfer1, trans.name),
                        location_orig = trans.transfer_location_id.id
                        location_dest = trans.dest_warehouse_id.lot_stock_id.id
                        related_company_move_id = False
                        
                    elif first == 1:
                        origin = (trans.name) + ':' + transfer2
                        company = obj_warehouse.company_id.id
                        notem = _('Move for pulled procurement coming from original warehouse %s, pull rule %s, via original Procurement %s') % (obj_warehouse.name, transfer2, trans.name),
                        noteproc = _('Pulled procurement coming from original warehouse %s, pull rule %s, via original Procurement %s') % (obj_warehouse.name, transfer2, trans.name),
                        location_orig = obj_warehouse.lot_stock_id.id
                        location_dest = trans.transfer_location_id.id
                        related_company_move_id = self.pool.get('multicompany.moves.rel').create(cr,uid,{'move_in_id' : move_id})
                                               
                    if first == 1:
                        usr_uid = 1
                    else:
                        usr_uid = uid
                    move_id = move_obj.create(cr, usr_uid, {
                        'name': origin,
                        'picking_id': False,
                        'company_id':  company or False,
                        'product_id': product.product_id.id,
                        'date': trans.date_planned,
                        'product_qty': product.product_uom_qty,
                        'product_uom': product.product_uom.id,
                        'product_uos_qty': (product.product_uos and product.product_uos_qty)\
                                or product.product_uom_qty,
                        'product_uos': (product.product_uos and product.product_uos.id)\
                                or product.product_uom.id,
                        'address_id': False,
                        'location_id': location_orig,
                        'location_dest_id': location_dest,
                            
                        'tracking_id': False,
                        'cancel_cascade': False,
                        'state': 'confirmed',
                        'note': notem,
                        'related_company_move_id' : related_company_move_id
                    })
                    if first == 0:
                        move_in_ids.append(move_id)
                    elif first == 1:
                        move_out_ids.append(move_id)    

                    proc_id = proc_obj.create(cr, usr_uid, {
                        'name': trans.name,
                        'origin': origin,
                        'note': noteproc,
                        'company_id':  company or False,
                        'date_planned': trans.date_planned,
                        'product_id': product.product_id.id,
                        'product_qty': product.product_uom_qty,
                        'product_uom': product.product_uom.id,
                        'product_uos_qty': (product.product_uos and product.product_uos_qty)\
                                or product.product_uom_qty,
                        'product_uos': (product.product_uos and product.product_uos.id)\
                                or product.product_uom.id,
                        'location_id': location_orig,
                        'procure_method': 'make_to_stock',
                        'move_id': move_id,
                    })
                   
                    wf_service.trg_validate(usr_uid, 'procurement.order', proc_id, 'button_confirm', cr)
                    proc_obj.write(cr, usr_uid, [proc_id], {'state':'running', 'message':_('Pulled from another location via procurement %d')%proc_id})
                    wf_service.trg_validate(usr_uid, 'procurement.order', proc_id, 'button_check', cr)
                    first += 1
                    
            self.prepare_pickings(cr,uid,ids,trans,obj_warehouse,transfer1,transfer2,wf_service,move_in_ids,move_out_ids,True)
            self.prepare_pickings(cr,1,ids,trans,obj_warehouse,transfer1,transfer2,wf_service,move_in_ids,move_out_ids,False)
            

        self.write(cr, uid, ids, {'state': 'transferred'})

        return True

product_transfer()

class wzd_transfer_product_rel(osv.osv):
    _name = 'wzd.transfers.product.rel'
    _description = "one2many betweetn product.product and product.transfer"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute= dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'product_uos_qty': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS')),
        'product_uos': fields.many2one('product.uom', 'Product UoS'),
        'product_tranfer_id': fields.many2one('product.transfers', 'Transfer ')
    }
    
    def product_id_change(self, cr, uid, ids, product, qty=0, uom=False, qty_uos=0, uos=False, context=None):
        context = context or {}
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        res = {}
        if not product:
            return {'value': {'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}

        result = res.get('value', {})
        warning_msgs = res.get('warning') and res['warning']['message'] or ''
        product_obj = product_obj.browse(cr, uid, product, context=context)

        uom2 = False
        if uom:
           
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}

        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff

        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty

        return {'value': result, 'domain': domain, 'warning': warning}
        
    def product_uos_change(self, cr, uid, ids, product, qty=0,
            uom=False, qty_uos=0, uos=False):
        res = {}
        if product:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            if uos:
                if self.pool.get('product.uom').browse(cr,uid, uos).category_id.id == product_obj.uos_id.category_id.id:
                    if qty_uos:
                        qty_uom = qty_uos / product_obj.uos_coeff
                        uom = product_obj.uom_id.id

                        res = self.product_id_change(cr, uid, ids, product,
                            qty=qty_uom, uom=False, qty_uos=qty_uos, uos=uos)
                        if 'product_uom' in res['value']:
                            del res['value']['product_uom']
        return res

wzd_transfer_product_rel()


