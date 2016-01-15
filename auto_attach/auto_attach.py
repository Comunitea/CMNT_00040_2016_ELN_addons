##############################################################################
#
# Copyright (c) 2007-2010 NaN Projectes de Programari Lliure, S.L. All rights reserved
#                         http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv
from osv import fields

from NanScan.Template import *
from NanScan.Document import *
from NanScan.Recognizer import *
from NanScan.Ocr import *

from PyQt4.QtCore import *


class scan_template(osv.osv):
    """
    This class holds template information. A template stores information about what data is expected
    to be found in a given type of document. It also stores what information we need to be retrieved
    from the document to be used as input data for a given process.
    """

    _name = 'scan.template'
    _columns = {
        'name': fields.char('Name', 64, required=True),
        'box_ids': fields.one2many('scan.template.box', 'template_id',
                                        'Boxes'),
        'analysis_function': fields.char('Analysis Function', 256),
        'attach_function': fields.char('Attachment Function', 256),
        'action_function': fields.char('Action Function', 256),
        'document_ids': fields.one2many('nan.document', 'template_id',
                                            'Documents')
    }

    # Returns a Template from the fields of a template. You'll usually use 
    # getTemplateFromId() or getAllTemplates()
    def getTemplateFromData(self, cr, uid, data, context=None):
        template = Template(data['name'])
        template.id = data['id']
        template.analysisFunction = data['analysis_function']
        ids = self.pool.get('scan.template.box').search(cr, uid,
                [('template_id', '=', data['id'])], context=context)

        boxes = self.pool.get('scan.template.box').read(cr, uid, ids,
                context=context)
        for y in boxes:
            box = TemplateBox()
            box.id = y['id']
            box.rect = QRectF(y['x'], y['y'], y['width'], y['height'])
            box.name = y['name']
            box.text = y['text']
            box.recognizer = y['recognizer']
            box.type = y['type']
            box.filter = y['filter']
            # Important step: ensure box.text is unicode!
            if isinstance(box.text, str):
                box.text = unicode(box.text, 'latin-1')
            template.addBox(box)
        return template

    # Returns a Template from the given id
    def getTemplateFromId(self, cr, uid, id, context=None):
        templates = self.pool.get('scan.template').read(cr, uid, [id],
                context=context)
        if not templates:
            return None
        return self.getTemplateFromData(cr, uid, templates[0], context)

    # Returns all templates in a list of objects of class Template
    def getAllTemplates(self, cr, uid, context=None):
        # Load templates into 'templates' list
        templates = []
        ids = self.search(cr, uid, [], context=context)
        templateValues = self.read(cr, uid, ids,
                ['name', 'analysis_function'], context=context)
        for x in templateValues:
            templates.append(self.getTemplateFromData(cr, uid, x, context ))
        return templates

scan_template()


class scan_template_box(osv.osv):
    _name = 'scan.template.box'
    _columns = {
        'template_id': fields.many2one('scan.template', 'Template',
                required=True, ondelete='cascade'),
        'x': fields.float('X'),
        'y': fields.float('Y'),
        'width': fields.float('Width'),
        'height': fields.float('Height'),
        'feature_x': fields.float('Feature X'),
        'feature_y': fields.float('Feature Y'),
        'feature_width': fields.float('Feature Width'),
        'feature_height': fields.float('Feature Height'),
        'name': fields.char('Name', 256),
        'text': fields.char('Text', 256),
        'recognizer': fields.selection([('text', 'Text'),
                    ('barcode', 'Barcode'), ('dataMatrix', 'Data Matrix')],
                    'Recognizer'),
        'type': fields.selection([('matcher', 'Matcher'),
                    ('input', 'Input')], 'Type'),
        'filter': fields.selection([('numeric', 'Numeric'),
                    ('alphabetic', 'Alphabetic'),
                    ('alphanumeric', 'Alphanumeric'),
                    ('exists', 'Exists'),
                    ('none', 'None')], 'Filter')
    }
scan_template_box()
