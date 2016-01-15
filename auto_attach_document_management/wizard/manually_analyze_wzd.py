# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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

from osv import osv, fields
from tools.translate import _
from tools import ustr
import netsvc

class manually_analyze_wzd(osv.osv_memory):
    
    _name = "manually.analyze.wzd"
    
    
    def attachableDocuments(self, cr, uid, context={}):
        expedient_ids = self.pool.get('type.expedient').search(cr, uid, [])
        models = []
        for expedient in self.pool.get('type.expedient').browse(cr, uid, expedient_ids):
            models.append(expedient.origin_model.id)
            for model in expedient.model_ids:
                models.append(model.ir_model.id)
           
        models = list(set(models))
        records = self.pool.get('ir.model').read(cr, uid, models,
                        ['model', 'name'], context)        
        data = []
        for record in records:
            model = record['model']
            name = record['name']
            if len(name) > 30:
                name = name[:30] + '...'
            data.append((model, name))
        return data
        
    def reports(self, cr, uid, context={}):
        expedient_ids = self.pool.get('type.expedient').search(cr, uid, [])
        reports = []
        for expedient in self.pool.get('type.expedient').browse(cr, uid, expedient_ids):
            for report in expedient.expedient_document:
                reports.append(report.ir_act_report_xml_id.id)
        
        reports = list(set(reports))
        records = self.pool.get('ir.actions.report.xml').read(cr, uid, reports,
                    ['report_name', 'name'], context)
        data = []
        for record in records:
            r_name = record['report_name']
            name = record['name']
            if len(name) > 30:
                name = name[:30] + '...'
            data.append((r_name, name))
        return data
    
    _columns = {
        'associated_doc_id': fields.reference('Associated document',
                selection=attachableDocuments, size=128, required=True),
        'expedient_id': fields.many2one('expedient', 'Expedient', readonly=True),
        'annex': fields.boolean('Annex'),
        'report_sel': fields.selection(reports, 'Report'),
        'state': fields.selection([('first','First'),('second','Second')], 'State', readonly=True)
    }  
    
    _defaults = {
        'state': 'first'
    }
    
    def search_expedient(self, cr, uid, ids, context=None):
        if context is None: context = {}
        obj = self.browse(cr, uid, ids[0])
        asso_obj = self.pool.get(obj.associated_doc_id._name).browse(cr, uid, obj.associated_doc_id.id)
        if 'x_expedient_id' in asso_obj._columns and asso_obj.x_expedient_id:
            obj.write({'expedient_id': asso_obj.x_expedient_id.id, 'state': 'second'})
        else:
            raise osv.except_osv(_("Error"), _("Cannot associate it to this document, because this document don't have any expedient related"))
            
        return True
        
    def process(self, cr, uid, ids, context=None):
        if context is None: context = {}
        obj = self.browse(cr, uid, ids[0])
        asso_obj = self.pool.get(obj.associated_doc_id._name).browse(cr, uid, obj.associated_doc_id.id)
        doc = self.pool.get('scan.document').browse(cr, uid, context['active_id'])
        
        if obj.report_sel:
            self.pool.get('scan.document.property').create(cr, uid, {'document_id': doc.id,
                                                                    'name': "Manual",
                                                                    'value': obj.associated_doc_id._name + u"," + ustr(obj.associated_doc_id.id) + u"/" + obj.report_sel + u"/PAG1"})
        elif obj.annex:
            self.pool.get('scan.document.property').create(cr, uid, {'document_id': doc.id,
                                                                    'name': "Manual",
                                                                    'value': obj.associated_doc_id._name + u"," + ustr(obj.associated_doc_id.id)})
                    
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'scan.document', doc.id, 'manual_analysis', cr)
                    
        return {}
    
manually_analyze_wzd()
