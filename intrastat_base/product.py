# -*- encoding: utf-8 -*-
##############################################################################
#
#    Report intrastat base module for OpenERP
#    Copyright (C) 2010-2011 Akretion (http://www.akretion.com/) All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from osv import osv, fields

class report_intrastat_code(osv.osv):
    _name = "report.intrastat.code"
    _description = "Intrastat code"
    _order = "name,intrastat_code"
    _rec_name = "intrastat_code"

    _columns = {
        'name': fields.char('H.S. code', size=16, required=False, select=True,
            help="Code from the Harmonised System. Nomenclature is available from the World Customs Organisation, see http://www.wcoomd.org/. Some countries have made their own extensions to this nomenclature."),
        'description': fields.char('Description', size=128, select=True,
            help='Short text description of the H.S. category'),
        'intrastat_code': fields.char('Intrastat CN code', size=12, required=True, select=True,
            help="Code used for the Intrastat declaration. Must be part of the 'Combined Nomenclature' (CN) with 8 digits with sometimes a 9th digit."),
        'intrastat_uom_id': fields.many2one('product.uom', 'UoM for intrastat product report', select=True,
            help="Select the unit of measure if one is required for this particular intrastat code (other than the weight in Kg). If no particular unit of measure is required, leave empty."),
    }

    def _intrastat_code(self, cr, uid, ids):
        for intrastat_code_to_check in self.read(cr, uid, ids, ['intrastat_code']):
            code = intrastat_code_to_check['intrastat_code']
            if code:
                code = code.replace(' ', '')
                if not code.isdigit() or len(code) not in (8, 9):
                    return False
        return True

    def _hs_code(self, cr, uid, ids):
        for code_to_check in self.read(cr, uid, ids, ['name']):
            if code_to_check['name']:
                if not code_to_check['name'].isdigit():
                    return False
        return True

    _constraints = [
        (_intrastat_code, "The 'Intrastat code' should have exactly 8 or 9 digits.", ['intrastat_code']),
        (_hs_code, "The 'Harmonised System Code' should only contain digits.", ['name']),
    ]
report_intrastat_code()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'intrastat_id': fields.many2one('report.intrastat.code', 'Intrastat code', help="Code from the Harmonised System. If this code is not set on the product itself, it will be read here, on the related product category."),
    }
product_category()

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'intrastat_id': fields.many2one('report.intrastat.code', 'Intrastat code'),
        'exclude_from_intrastat': fields.boolean('Exclude from Intrastat reports', help="If set to True, the product or service will not be taken into account for Intrastat Product or Service reports. So you should leave this field to False unless you have a good reason. Exemple of good reason : 'Shipping' is a service that should probably be excluded from the Intrastat Service report."),
    }

    _default = {
        'exclude_from_intrastat': False,
    }
product_template()
