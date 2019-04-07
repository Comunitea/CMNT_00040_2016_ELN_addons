# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-TODAY
#        Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#        $Javier Colmenero Fernández$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
import datetime, time
from edi_logging import logger
from lxml import etree
from openerp import netsvc

log = logger("import_edi")

class edi_import (osv.osv_memory):
    
    _name = "edi.import"
    _columns = {
        'configuration': fields.many2one('edi.configuration', 'Configuration', required=True),
        'downloaded_files':fields.integer('Archivos Descargados', readonly=True),
        'pending_process':fields.integer('Ficheros pendientes de procesar', readonly=True),
        'state': fields.selection([('start','Empezar'),('to_process','A procesar'),('processed','Procesado')], 'Estado', readonly=True),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(edi_import, self).default_get(cr, uid, fields, context=context)
        conf_ids = self.pool.get('edi.configuration').search(cr,uid,[])
        if not conf_ids:
            raise osv.except_osv(_('Error'), _('No existen configuraciones EDI.'))
            
        res.update({'configuration': conf_ids[0],
                    'downloaded_files': 0,
                    'state' : 'start',
                    'pending_process': 0})
        return res
        
    def get_files(self,cr,uid,ids,context=None):
        """Este método es llamado cuando pulsamos el botón de obtener ficheros del asistente de importación.
        Lee los ficheros en el directorio asignado, y si no se han creado documentos para ellos,los
        crea en estado de borrador"""
        res = {}
        files_downloaded = 0
        if context == None:
            context = {}
        wizard = self.browse(cr,uid,ids[0])
        path = wizard.configuration.ftpbox_path + "/in"
        
        if wizard.configuration.local_mode:
            log.info(u'Importando documentos en modo local')
            for file_name in os.listdir(path):
                doc_type,name = file_name.replace('.xml','').split('_')
                if not self.pool.get('edi.doc').search(cr,uid,[('name','=',name)]):
                    f = open(path+"/"+file_name)
                    file_id = self.pool.get('edi.doc').create(cr,uid,{
                        'name' : name,
                        'file_name' : file_name,
                        'status': 'draft',
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'type': doc_type.lower(),
                        'message':f.read(),
                    })
                    f.close()
                    files_downloaded += 1
                    log.info(u"Importado %s " % name)
                else:
                    log.info(u"Ignorado %s, ya existe en el sistema." % name)
               
            doc_ids = self.pool.get('edi.doc').search(cr,uid,[('status','in',['draft','error'])])
            wizard.write({'downloaded_files':files_downloaded , 
                            'pending_process':len(doc_ids),
                            'state':'to_process'})
            log.info(u"%s documento(s) han sido importados." % files_downloaded)
            log.info(u"%s documento(s) están pendientes de procesar." % len(doc_ids))
            
        return True

    def get_partner(self,cr,uid,gln):
        ids = self.pool.get('res.partner').search(cr,uid,[('gln','=',gln)])
        if not ids:
            raise osv.except_osv(_('Error'), _(u'No existen ningún cliente con gln %s.' % gln))
        partner = self.pool.get('res.partner').browse(cr,uid,ids[0])
        
        return partner
    
    def gln_to_dir(self,cr,uid,gln):
        ids = self.pool.get('res.partner.address').search(cr,uid,[('gln','=',gln)])
        if not ids:
            raise osv.except_osv(_('Error'), _(u'No existen ninguna dirección con gln %s.' % gln))
        dir_obj = self.pool.get('res.partner.address').browse(cr,uid,ids[0])
        return dir_obj
     
    def get_notes(self,cr,uid,obs):
        observation = ''
        for line in obs:
            if line.text:
                observation += (line.text + u'\n')
                
        return observation
    
    def get_partner_bank(self,cr,uid,partner):
        pay_type = partner.payment_type_customer
        if pay_type and pay_type.suitable_bank_types and pay_type.suitable_bank_types[0].code=='bank':
            if partner.bank_ids:
                return partner.bank_ids[0].id 
        else:
            return False
            
    def create_order_version(self,cr,uid,mode,order_id,doc):
        sale_obj = self.pool.get('sale.order').browse(cr,uid,order_id)
        version_id = self.pool.get('sale.order').search(cr,uid,[('client_order_ref','=',sale_obj.client_order_ref),('id','!=',sale_obj.id)])
        if version_id:
            old_sale = self.pool.get('sale.order').browse(cr,uid,version_id[0])
            vals = {}
            if not old_sale.sale_version_id:
                vals.update({'sale_version_id':old_sale.id,
                                'version': 1,
                                'name': old_sale.name + u" V.1",
                })
            else:
                vals.update({'sale_version_id':old_sale.sale_version_id.id,
                                'version': old_sale.version + 1,
                                'name': old_sale.sale_version_id.name + u" V." + str(old_sale.version + 1)
                })
            old_sale.write({'active':False})
            sale_obj.write(vals)
            log.info(u"Creada version para el documento %s." % doc.name)
            if mode == 'DEL':
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_validate(uid, 'sale.order', sale_obj.id, 'cancel', cr)
                log.info(u"La venta %s ha sido cancelada." % sale_obj.name)
                
        return True
        
        
    def create_order(self,cr,uid,cdic,root,doc):
        conf_ids = self.pool.get('edi.configuration').search(cr,uid,[])
        if not conf_ids:
            raise osv.except_osv(_('Error'), _('No existen configuraciones EDI.'))
        wizard = self.pool.get('edi.configuration').browse(cr,uid,conf_ids[0])
        ref =  cdic.get('gi_cab_numped',False)!= False and cdic['gi_cab_numped'].text or False
        sale_id = []
        if root.attrib['gi_cab_funcion'] in ['REP','DEL'] and ref:
            sale_id = self.pool.get('sale.order').search(cr,uid,[('client_order_ref','=',ref)])
            
        if sale_id or root.attrib['gi_cab_funcion'] == 'ORI':
            partner = self.get_partner(cr,uid,cdic['gi_cab_emisor'].text)
            contact_dir = self.gln_to_dir(cr,uid,cdic['gi_cab_emisor'].text)
            invoice_dir = self.gln_to_dir(cr,uid,cdic['gi_cab_comprador'].text)
            shipping_dir = self.gln_to_dir(cr,uid,cdic['gi_cab_shipto'].text)
            values = {
                'date_order': cdic.get('gi_cab_fecha',False)!= False and cdic['gi_cab_fecha'].text or time.strftime('%Y-%m-%d'),
                # POST-MIGRATION
                # 'shop_id': self.pool.get('sale.shop').search(cr,uid,[])[0] ,
                'top_date': cdic.get('gi_cab_fechatop',False)!= False and cdic['gi_cab_fechatop'].text or False,
                'client_order_ref': ref,
                'partner_id': partner.id,
                'partner_order_id': contact_dir.id,
                'partner_invoice_id': invoice_dir.id,
                'partner_shipping_id': shipping_dir.id,
                'pricelist_id': partner.property_product_pricelist.id,
                'fiscal_position': partner.fiscal_position.id,
                'note': cdic.get('gi_cab_obs', False) and self.get_notes(cr,uid,cdic['gi_cab_obs']) or "",
                'order_type': root.attrib['gi_cab_funcion'],
                'urgent': root.attrib['gi_cab_nodo'] == '224' and True or False,
                'payment_term': partner.property_payment_term.id,
                'payment_type': partner.payment_type_customer.id,
                'partner_bank': self.get_partner_bank(cr,uid,partner),
                'user_id' : wizard.salesman.id,
            }
            order_id = self.pool.get('sale.order').create(cr,uid,values)
            log.info(u"Creada orden de venta a partir del documento %s." % doc.name)
            if root.attrib['gi_cab_funcion'] in ['REP','DEL']:
                version_id = self.create_order_version(cr,uid,root.attrib['gi_cab_funcion'],order_id,doc)
        else:
            doc.write({'status' : 'error',
                        'message':'La referencia de este documento no existe en el sistema',
                        'mode' : root.attrib['gi_cab_funcion']})
            log.info(u"Error en el documento %s. La venta a la que hace referencia no existe." % doc.name)
            order_id = False
        
        return order_id
    
    def get_product(self,cr,uid,ean13v):
        ids = self.pool.get('product.product').search(cr,uid,[('ean13v','=',ean13v)])
        if not ids:
            raise osv.except_osv(_('Error'), _(u'No existen ningún producto con ean13v %s.' % ean13v))
        product = self.pool.get('product.product').browse(cr,uid,ids[0])
        
        return product
       
    def get_product_uom(self,cr,uid,uom_code):
        if not uom_code:
            raise osv.except_osv(_('Error'), _(u'No se estableció unidad de medida.' % uom_code))
        ids = self.pool.get('product.uom').search(cr,uid,[('edi_code','=',uom_code)])
        if not ids:
            raise osv.except_osv(_('Error'), _(u'No existe unidad de medida %s.' % uom_code))
            
        return ids[0]
    
    def get_taxes(self,cr,uid,product,order_id):
        order = self.pool.get('sale.order').browse(cr,uid,order_id)
        fiscal_position = order.partner_id.fiscal_position
        if fiscal_position:
            taxes = self.pool.get('account.fiscal.position').map_tax(cr,uid,fiscal_position,product.taxes_id)
        else:
            taxes = [x.id for x in product.taxes_id]
            
        return taxes
    
    def create_lines(self,cr,uid,ldic,order_id):
        """ Crea las lineas del pedido de ventas"""
        for l in ldic:
            lines = dict([x.tag,x] for x in ldic[l])
            umedida = lines.get('gi_lin_cantped',False) != False and lines['gi_lin_cantped'].attrib['gi_lin_umedida'] or False
            umedfac = lines.get('gi_lin_cantfac',False) != False and lines['gi_lin_cantfac'].attrib['gi_lin_umedfac'] or False
            product = self.get_product(cr,uid,lines['gi_lin_ean13v'].text)
            values = {
                'order_id': order_id,
                'product_id': product.id ,
                'name': lines.get('gi_lin_descmer',False)!= False and lines['gi_lin_descmer'].text or False,
                'product_uom_qty': lines.get('gi_lin_cantped',False)!= False and float(lines['gi_lin_cantped'].text) or 0.0,
                'product_uom': self.get_product_uom(cr,uid,umedida),
                'price_unit':lines.get('gi_lin_precion',False)!= False and float(lines['gi_lin_precion'].text) or 0.0,
                'product_uos_qty': lines.get('gi_lin_cantfac',False)!= False and float(lines['gi_lin_cantfac'].text) or 0.0,
                'product_uos': self.get_product_uom(cr,uid,umedfac),
                'notes':lines.get('gi_lin_obs',False)!= False and self.get_notes(cr,uid,lines['gi_lin_obs']) or False,
                'tax_id': [(6,0,self.get_taxes(cr,uid,product,order_id))],
                'type': product.procure_method,
                'refcli': lines.get('gi_lin_refcli',False)!= False and lines['gi_lin_refcli'].text or False ,
                'refprov': lines.get('gi_lin_refprov',False)!= False and lines['gi_lin_refprov'].text or False,
            }
            self.pool.get('sale.order.line').create(cr,uid,values)
            
        return True
    
    def update_doc(self,cr,uid,order_id,mode,cdic,doc):
        values = {
            'date_process': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'imported',
            'mode': mode,
            'sale_order_id': order_id,
            'gln_ef': cdic.get('gi_cab_emisor',False) and cdic['gi_cab_emisor'].text or False,
            'gln_ve': cdic.get('gi_cab_vendedor',False) and cdic['gi_cab_vendedor'].text or False,
            'gln_co': cdic.get('gi_cab_comprador',False) and cdic['gi_cab_comprador'].text or False,
            'gln_rm': cdic.get('gi_cab_shipto',False) and cdic['gi_cab_shipto'].text or False,
        }
        return doc.write(values)
        
    
    def parse_order_file(self,cr,uid,filename,doc):
        """Procesa el fichero orders, creando un pedido de venta"""
        xml = etree.parse(filename)
        root = xml.getroot()
        mode = root.attrib['gi_cab_funcion']
        cab = root[0]
        lines = root[1]
        cdic = dict( [ (x.tag,x) for x in cab ] )
        ldic = dict( [ (x.tag + x.attrib['n'],x) for x in lines] )
        
        order_id = self.create_order(cr,uid,cdic,root,doc)
        if order_id:
            self.create_lines(cr,uid,ldic,order_id)
            self.update_doc(cr,uid,order_id,mode,cdic,doc)
            
        return True
    
    def change_moves(self,cr,uid,gilin,sscc,id_alb,doc):
        """ recibe un elemento glin, se lo recorre y comprueba si existen los productos,empaquetado,
        lote y cantidad indicadas"""
        dc = dict( [ (x.tag,x) for x in gilin ] )
        id_track=False
        if sscc:
            id_track = self.pool.get('stock.tracking').search(cr,uid,[('name','=',sscc)])
            if id_track:
                id_track = id_track[0]
            else:
                raise osv.except_osv(_('Error'), _(u'No existe el paquete con sscc %s.' % sscc))
                                    
        id_product = self.pool.get('product.product').search(cr,uid,[('ean13v','=',dc['gi_lin_ean13v'].text)])
        if id_product:
            id_product = id_product[0]
        else:
            raise osv.except_osv(_('Error'), _(u'No existe el producto con ean13v %s.' % dc['gi_lin_ean13v'].text))
   
        num_lot = dc['gi_lin_numserie'].text or False
        id_lot=False
        if num_lot:
            id_lot = self.pool.get('stock.production.lot').search(cr,uid,[('name','=',num_lot),('product_id','=',id_product)])
            if id_lot:
                id_lot = id_lot[0]
            else:
                raise osv.except_osv(_('Error'), 
                    _(u'No existe el lote con nombre %s para el producto con ean13v %s.' % (num_lot,dc['gi_lin_ean13v'].text)))
            
        move_id = self.pool.get('stock.move').search(cr,uid,[ ('picking_id','=',id_alb),('product_id','=',id_product),
                        ('tracking_id','=',id_track),('prodlot_id','=',id_lot),
                        ('product_qty','=',float(dc['gi_lin_cantent'].text)) ])
        if move_id:
            move_id = move_id[0]
        else:
            raise osv.except_osv(_('Error'),
                _(u'No se encontraron movimientos con las características requeridas.Es posible que el paquete, el lote o la cantidad estén mal asignados en el fichero'))

        move = self.pool.get('stock.move').browse(cr,uid,move_id)
        if float(dc['gi_lin_cantrec'].text) >  move.product_qty:
            raise osv.except_osv(_('Error'),_(u'No es posible que la cantidad recibida sea mayor que la cantidad entregada'))
        move.write({'acepted_qty': float(dc['gi_lin_cantrec'].text),
                    'note': dc.get('gi_lin_obs',False)!= False and self.get_notes(cr,uid,dc['gi_lin_obs']) or False,
                    'rejected' : dc['gi_lin_reccode'].text == 'REJECTED' or False
        })
        log.info(u"Ean13v producto -> %s : La cantidad aceptada de %s actualizada en el movimiento. " % (dc['gi_lin_ean13v'].text,dc['gi_lin_cantrec'].text) )
        
        return True
    
    def parse_recadv_file(self,cr,uid,filepath,doc):
        """ Lee el documento recadev y se recorre las lineas para pasarlas a la función, que escribe
        el campo cantidad aceptada a los movimientos """
        xml = etree.parse(filepath)
        root = xml.getroot()
        mode = root.attrib['gi_cab_funcion']
        cab = root[0]
        empacs = root[1]
        gi_cab_dic = dict( [ (x.tag,x.text) for x in cab ] )
        num_alb = gi_cab_dic['gi_cab_numalb']  #sumar el OUT/
        id_alb = self.pool.get('stock.picking').search(cr,uid,[('name','=',num_alb)])
        if id_alb:
            id_alb = id_alb[0]
        else:
            doc.write({'status' : 'error',
                        'message':'La referencia de este documento no existe en el sistema',
                        })
            log.info(u"Error en el documento %s. El albarán %s al que se hace referencia no existe." % (doc.name,num_alb))
            
        gi_empac_dic = dict( [ (x.tag + x.attrib['n'],x) for x in empacs] )
        for e in gi_empac_dic:
            sscc = gi_empac_dic[e].attrib['gi_empaq_sscc']
            for gl in gi_empac_dic[e]:
                for gilin in gl:
                    self.change_moves(cr,uid,gilin,sscc,num_alb,doc)
                    
        f = open(filepath)
        doc.write({'status': 'imported',
            'date_process': time.strftime('%Y-%m-%d %H:%M:%S'),
            'mode': mode,
            'sale_order_id': False,
            'picking_id': id_alb,
            'gln_ef': gi_cab_dic.get('gi_cab_emisor',False) and gi_cab_dic['gi_cab_emisor'] or False,
            'gln_ve': gi_cab_dic.get('gi_cab_vendedor',False) and gi_cab_dic['gi_cab_vendedor'] or False,
            'gln_co': gi_cab_dic.get('gi_cab_comprador',False) and gi_cab_dic['gi_cab_comprador'] or False,
            'gln_rf':  False,
            'gln_rm':  False,
            'gln_de':  False,
            'message':f.read(),
            })
        log.info(u"El documento %s ha sido importado." % doc.name)
        f.close()
        return True
    
    def process_files(self,cr,uid,ids,context=None):
        """Busca todos los ficheros que estén en error o en borrador y los procesa dependiendo del 
        tipo que sean"""
        res = {}
        if context == None:
            context = {}
            
        wizard = self.browse(cr,uid,ids[0])
        path = wizard.configuration.ftpbox_path + "/in"
        doc_ids = self.pool.get('edi.doc').search(cr,uid,[('status','in',['draft','error'])])
        model='sale'
        act='action_order_form'
        for doc in self.pool.get('edi.doc').browse(cr,uid,doc_ids):
            file_path = path + "/" + doc.file_name
            if doc.type == 'orders':
                self.parse_order_file(cr,uid,file_path,doc)
            elif doc.type == 'recadv':
                model = 'stock'; act='action_picking_tree'
                self.parse_recadv_file(cr,uid,file_path,doc)
                
        data_pool = self.pool.get('ir.model.data')
        action_model,action_id = data_pool.get_object_reference(cr, uid, model, act)
        action = self.pool.get(action_model).read(cr,uid,action_id,context=context)
        
        return action
        
edi_import()
