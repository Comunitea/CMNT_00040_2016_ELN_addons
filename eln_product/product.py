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
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime
from openerp.tools.translate import _

class product_options_product(orm.Model):
    _name = 'product.options.product'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'option_id': fields.many2one('product.options', 'Option'),
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.options.product') or '/',
    }


class product_verifications_product(orm.Model):
    _name = 'product.verifications.product'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'verification_id': fields.many2one('product.verifications', 'Verification'),
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.verifications.product') or '/',
    }


class product_revisions(orm.Model):
    _name = 'product.revision'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'user_id': fields.many2one('res.users', 'User'),
        'date': fields.date('Date'),
        'product_id': fields.many2one('product.product', 'Product'),
        'description': fields.text('Description')

    }
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'date':lambda *a: time.strftime("%Y-%m-%d"),
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.revision') or '/',
    }


class product_sheet_shipments(orm.Model):
    _name = 'product.sheet.shipments'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        # 'contact_id': fields.many2one('res.partner.contact', 'Contact', required=True),
        'date': fields.date('Date', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'revision': fields.char('Rev.', size=255, readonly=True)
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.sheet.shipments') or '/',
    }


class product_product(orm.Model):
    _inherit = 'product.product'

    def _get_last_revision(self, cr, uid, ids, field_name, arg, context):

        res = {}
        revisions = []
        last_revision = ""
        for line in self.browse(cr, uid, ids, context=context):
            revisions = self.pool.get('product.revision').search(cr, uid, [('product_id','=',line.id)], order="date desc")
            if revisions:
                rev = self.pool.get('product.revision').browse(cr, uid, revisions[0])
                date = datetime.strptime(rev.date, "%Y-%m-%d")
                last_revision = rev.name + " (" + date.strftime("%d/%m/%Y") + ")"
            res[line.id] = last_revision

        return res

    def _get_ldm_last_revision(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        revisions = []
        boms = []
        last_revision = ""
        for line in self.browse(cr, uid, ids, context=context):
            revisions = self.pool.get('mrp.bom').search(cr, uid, [('product_id','=', line.id)], order='date_start desc')
            if revisions:
                rev = self.pool.get('mrp.bom').browse(cr, uid, revisions[0])
                if rev.date_start:
                    date = datetime.strptime(rev.date_start, "%Y-%m-%d")
                    last_revision=rev.name + " (" + date.strftime("%d/%m/%Y") + ")"
            res[line.id] = last_revision

        return res

    def _get_signature(self, cr, uid, ids, field_name, arg, context=None):
        res = {}

        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = {
                'written_signature': False,
                'reviewed_signature': False,
                'approved_signature': False
            }

            res[product.id]['written_signature'] = product.written_by and product.written_by.user_id and product.written_by.user_id.signature_image or False
            res[product.id]['reviewed_signature'] = product.reviewed_by and product.reviewed_by.user_id and product.reviewed_by.user_id.signature_image or False
            res[product.id]['approved_signature'] = product.approved_by and product.approved_by.user_id and product.approved_by.user_id.signature_image or False

        return res

    def _product_dispo(self, cr, uid, ids, name, arg, context={}):
        if context is None:
            context = {}
        res = {}
        c_in = context.copy()
        c_out = context.copy()
        c_in.update({ 'states': ('done',), 'what': ('in',) })
        c_out.update({ 'states': ('assigned','done',), 'what': ('out',) })
        # COMENTADO POST-MIGRATION
        # stock_in = self.get_product_available(cr, uid, ids, context=c_in)
        # stock_out = self.get_product_available(cr, uid, ids, context=c_out)
        # for p_id in ids:
        #     res[p_id] = stock_in.get(p_id, 0.0) + stock_out.get(p_id, 0.0)
        #     if res[p_id] < 0.0:
        #         res[p_id] = 0.0

        # AHORA ES STOCK REAL - SALIDAS
        for prod in self.browse(cr, uid, ids, context=context):
            stock_in = prod.qty_available
            stock_out = prod.outgoing_qty
            res[prod.id] = stock_in - stock_out
            if res[prod.id] < 0.0:
                res[prod.id] = 0.0
                res[prod.id] = 0.0

        return res

    _columns = {
        'product_ingredient_ids': fields.one2many('product.ingredient', 'product_parent_id', string="Ingredients"),
        'protective_atmosphere': fields.boolean('Protective atmosphere'),
        'perforated_bag': fields.boolean('Perforated bag'),
        'energy': fields.float('Energy', digits_compute=dp.get_precision('Product Unit of Measure')),
        'carbohydrates': fields.float('Carbohydrates', digits_compute=dp.get_precision('Product Unit of Measure')),
        'carbo_sugar': fields.float('of which sugars', digits_compute=dp.get_precision('Product Unit of Measure')),
        'fats': fields.float('Fats', digits_compute=dp.get_precision('Product Unit of Measure')),
        'fat_saturates': fields.float('of which saturates', digits_compute=dp.get_precision('Product Unit of Measure')),
        'proteins': fields.float('Proteins', digits_compute=dp.get_precision('Product Unit of Measure')),
        'salt': fields.float('Salt', digits_compute=dp.get_precision('Product Unit of Measure')),
        'storage_conditions': fields.text('Storage conditions', translate=True),
        'expected_use': fields.text('Expected use', translate=True),
        'allergen': fields.text('Allergen', translate=True),
        'ogms': fields.text('OGMs', translate=True),
        'comments_product_sheet': fields.char('Comments (product sheet)', size=255, translate=True),
        'comments_sheet': fields.char('Comments (sheet)', size=255, translate=True),
        'comments_product_logistics_sheet': fields.char('Comments (product logistics sheet)', size=255, translate=True),
        'palletizing': fields.binary('Palletizing'),
        'provision_boxes_base': fields.binary('Provision of boxes base'),
        'format': fields.char('Format', size=64, translate=True),
        'comercial_format': fields.char('Comercial format', size=255, translate=True),
        'bag_length': fields.char('Bag length', size=64),
        'box': fields.property(type='many2one', relation='product.product', string ='Box', method=True),
        'bobbin': fields.property(type='many2one', relation='product.product', string ='Bobbin', method=True),
        'bag': fields.property(type='many2one', relation='product.product', string ='Bag', method=True),
        'others': fields.property(type='many2one', relation='product.product', string ='Others', method=True),
        'seal': fields.property(type='many2one', relation='product.product', string ='Seal', method=True),
        'allergen_labeling': fields.boolean('Allergen labeling'),
        'gluten_free_labeling': fields.boolean('Gluten free labeling'),
        'parameter_ids': fields.one2many('product.parameter.product', 'product_id', 'Parameters'),
        'option_ids':fields.one2many('product.options.product', 'product_id', 'Options'),
        'verification_ids':fields.one2many('product.verifications.product', 'product_id', 'Verfications'),
        'revision_ids': fields.one2many('product.revision', 'product_id', 'Revisions'),
        'shipments_ids': fields.one2many('product.sheet.shipments', 'product_id', 'Shipments'),
        'partner_product_code': fields.char('Partner code', size=64),
        'dun14': fields.char('DUN14', size=64),
        'last_revision': fields.function(_get_last_revision,readonly=True,string='Last revision', type='char',size=255),
        'last_revision_ldm': fields.function(_get_ldm_last_revision,readonly=True,string='Last revision LdM', type='char',size=255),
        'company_product_code': fields.char('Company code', size=64),
        'written_by': fields.many2one('hr.employee','Written by'),
        'written_signature': fields.function(_get_signature, readonly=True, type='binary', multi="rev_signature"),
        'written_job': fields.many2one('hr.job', 'Job'),
        'reviewed_by': fields.many2one('hr.employee','Reviewed by'),
        'reviewed_signature': fields.function(_get_signature, readonly=True, type='binary', multi="rev_signature"),
        'reviewed_job': fields.many2one('hr.job', 'Job'),
        'approved_by': fields.many2one('hr.employee','Approved by'),
        'approved_signature': fields.function(_get_signature, readonly=True, type='binary', multi="rev_signature"),
        'approved_job': fields.many2one('hr.job', 'Job'),
        'recommended_ration': fields.integer('Recommended ration (g)'),
        'qty_dispo': fields.function(_product_dispo, method=True, digits_compute=dp.get_precision('Product Unit of Measure'), type='float', string='Stock available',
                    help="Stock available for assignment. It refers to the actual stock not reserved."),
        'pallet_boxes_layer': fields.integer('Boxes per layer'),
        'pallet_layers': fields.integer('Layers'),
        'pallet_boxes_pallet': fields.integer('Boxes per pallet'),
        'pallet_gross_weight': fields.float('Gross weight per pallet (kg)', digits=(16,2)),
        'pallet_net_weight': fields.float('Net weight per pallet (kg)', digits=(16,2)),
        'pallet_total_height': fields.float('Total height per pallet (mm)', digits=(16,0)),
        'pallet_total_width': fields.float('Total width per pallet (mm)', digits=(16,0)),
        'pallet_total_length': fields.float('Total length per pallet (mm)', digits=(16,0)),
        'pallet_ul' : fields.many2one('product.ul', 'Pallet type'),
        'box_units': fields.integer('Units per box'),
        'box_gross_weight': fields.float('Gross weight per box (kg)', digits=(16,2)),
        'box_net_weight': fields.float('Net weight per box (kg)', digits=(16,2)),
        'box_total_height': fields.float('Total height per box (mm)', digits=(16,0)),
        'box_total_width': fields.float('Total width per box (mm)', digits=(16,0)),
        'box_total_length': fields.float('Total length per box (mm)', digits=(16,0)),
        'box_ul' : fields.many2one('product.ul', 'Box type'),
        'unit_gross_weight': fields.float('Gross weight per unit (g)', digits=(16,2)),
        'unit_net_weight': fields.float('Net weight per unit (g)', digits=(16,2)),
        'unit_total_height': fields.float('Unit total height (mm)', digits=(16,0)),
        'unit_total_width': fields.float('Unit total width (mm)', digits=(16,0)),
        'unit_total_length': fields.float('Unit total length (mm)', digits=(16,0)),
    }

    def onchange_ean13(self, cr, uid, ids, ean13):
        '''Comprueba que no esté en uso ya el código ean introducido. Si lo está muestra un aviso'''
        res = {}
        warning = {}
        product_ids = []

        if ean13:
            product_ids = self.search(cr, uid, [('ean13', '=', ean13), ('id', 'not in', ids), ('active', '=', 1)], limit=100, context=None)
            if product_ids:
                cadena = '| '
                for product_id in product_ids:
                    cadena += self.browse(cr, uid, product_id).default_code + ' | '
                warning = {
                    'title': _('Warning!'),
                    'message' : _('The EAN-13 code you entered is already in use.\nThe references of related products are: %s') % (cadena)
                            }
                res = {'warning': warning}

        return res

    def onchange_dun14(self, cr, uid, ids, dun14):
        '''Comprueba que no esté en uso ya el código dun introducido. Si lo está muestra un aviso'''
        res = {}
        warning = {}
        product_ids = []

        if dun14:
            product_ids = self.search(cr, uid, [('dun14', '=', dun14), ('id', 'not in', ids), ('active', '=', 1)], limit=100, context=None)
            if product_ids:
                cadena = '| '
                for product_id in product_ids:
                    cadena += self.browse(cr, uid, product_id).default_code + ' | '
                warning = {
                    'title': _('Warning!'),
                    'message' : _('The DUN-14 code you entered is already in use.\nThe references of related products are: %s') % (cadena)
                            }
                res = {'warning': warning}

        return res

    def onchange_rev_employee(self, cr, uid, ids, employee_id, rev_type, context=None):
        '''Al cambiar el empleado rellena automáticamente el puesto de trabajo si está en la ficha de empleado'''
        res = {}

        if employee_id:
            employee_obj = self.pool.get('hr.employee')
            employee_obj = employee_obj.browse(cr, uid, employee_id, context=context)
            if employee_obj:
                if rev_type == 'written_by':
                    res = {'written_job': employee_obj.job_id and employee_obj.job_id.id or False}
                elif rev_type == 'reviewed_by':
                    res = {'reviewed_job': employee_obj.job_id and employee_obj.job_id.id or False}
                elif rev_type == 'approved_by':
                    res = {'approved_job': employee_obj.job_id and employee_obj.job_id.id or False}

        return {'value': res}

product_product()

class product_template(orm.Model):
    _inherit = 'product.template'
    _columns = {
        'uos_coeff': fields.float('UOM -> UOS Coeff', digits=(16,8),
            help='Coefficient to convert UOM to UOS\n'
            ' uos = uom * coeff'),
    }

product_template()
