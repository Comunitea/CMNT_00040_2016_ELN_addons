#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xmlrpclib
import socket
import traceback
import xlrd

UOM_MAP = {'C': "Box(es)",
           'U': "Unit(s)",
           'K': "kg",
           'L': "Liter(s)"}
IVA_MAP = {
    "1": ["S_IVA10", "P_IVA10_BC"],
    "2": ["S_IVA4", "P_IVA4_BC"],
    "3": ["S_IVA21", "P_IVA21_BC"],
    "4": ["S_IVA0", "P_IVA0_BC"]
}

class import_assets(object):
    def __init__(self, dbname, user, passwd, products_file):
        """método incial"""

        try:
            self.url_template = "http://%s:%s/xmlrpc/%s"
            self.server = "localhost"
            self.port = 8069
            self.dbname = dbname
            self.user_name = user
            self.user_passwd = passwd
            self.products_file = products_file

            #
            # Conectamos con OpenERP
            #
            login_facade = xmlrpclib.ServerProxy(self.url_template % (self.server, self.port, 'common'))
            self.user_id = login_facade.login(self.dbname, self.user_name, self.user_passwd)
            self.object_facade = xmlrpclib.ServerProxy(self.url_template % (self.server, self.port, 'object'))

            res = self.import_assets()
            #con exito
            if res:
                print ("All imported")
        except Exception, e:
            print ("ERROR: ", (e))
            sys.exit(1)

        #Métodos Xml-rpc

    def exception_handler(self, exception):
        """Manejador de Excepciones"""
        print "HANDLER: ", (exception)
        return True

    def create(self, model, data, context={}):
        """
        Wrapper del metodo create.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                            model, 'create', data, context)
            return res
        except socket.error, err:
            raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en create: %s' % (err.faultCode, err.faultString))


    def search(self, model, query, offset=0, limit=False, order=False, context={}, count=False, obj=1):
        """
        Wrapper del metodo search.
        """
        try:
            ids = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                    model, 'search', query, offset, limit, order, context, count)
            return ids
        except socket.error, err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
                raise Exception(u'Error %s en search: %s' % (err.faultCode, err.faultString))


    def read(self, model, ids, fields, context={}):
        """
        Wrapper del metodo read.
        """
        try:
            data = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                            model, 'read', ids, fields, context)
            return data
        except socket.error, err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
                raise Exception(u'Error %s en read: %s' % (err.faultCode, err.faultString))


    def write(self, model, ids, field_values,context={}):
        """
        Wrapper del metodo write.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                    model, 'write', ids, field_values, context)
            return res
        except socket.error, err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
                raise Exception(u'Error %s en write: %s' % (err.faultCode, err.faultString))


    def unlink(self, model, ids, context={}):
        """
        Wrapper del metodo unlink.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                    model, 'unlink', ids, context)
            return res
        except socket.error, err:
                raise Exception(u'Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
                    raise Exception(u'Error %s en unlink: %s' % (err.faultCode, err.faultString))

    def default_get(self, model, fields_list=[], context={}):
        """
        Wrapper del metodo default_get.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                        model, 'default_get', fields_list, context)
            return res
        except socket.error, err:
                raise Exception('Conexion rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
                raise Exception('Error %s en default_get: %s' % (err.faultCode, err.faultString))

    def execute(self, model, method, *args, **kw):
        """
        Wrapper del método execute.
        """
        try:
            res = self.object_facade.execute(self.dbname, self.user_id, self.user_passwd,
                                                                model, method, *args, **kw)
            return res
        except socket.error, err:
                raise Exception('Conexión rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
                raise Exception('Error %s en execute: %s' % (err.faultCode, err.faultString))

    def exec_workflow(self, model, signal, ids):
        """ejecuta un workflow por xml rpc"""
        try:
            res = self.object_facade.exec_workflow(self.dbname, self.user_id, self.user_passwd, model, signal, ids)
            return res
        except socket.error, err:
            raise Exception(u'Conexión rechazada: %s!' % err)
        except xmlrpclib.Fault, err:
            raise Exception(u'Error %s en exec_workflow: %s' % (err.faultCode, err.faultString))

    def getSupplierByRef(self, partner_ref):
        partner_ids = self.search("res.partner", [('supplier','=',True),('ref','=',partner_ref)])
        return partner_ids and partner_ids[0] or False

    def getTaxes(self, tax_name):
        tax_ids = self.search("account.tax", [('name', '=', tax_name)])
        return tax_ids

    def getUomByName(self, uom_name):
        uom_ids = self.search("product.uom", [('name', '=', uom_name)])
        return uom_ids and uom_ids[0] or False

    def getCategoryByName(self, categ_name):
        categ_ids = self.search("product.category", [('name', '=like', categ_name+u"%")])
        return categ_ids and categ_ids[-1] or False

    def getProductByCode(self, code):
        product_ids = self.search("product.product", [('default_code', 'like', code+u"%")])
        return product_ids and product_ids[-1] or False
        
    def getAssetByCode(self, code):
        asset_ids = self.search("account.asset.asset", [('code', '=', code)])
        print asset_ids
        return asset_ids and asset_ids[-1] or False
        
    def getAccountByCode(self, code):
        account_ids = self.search("account.account", [('code', '=', code)])
        print account_ids
        return account_ids and account_ids[-1] or False




    def import_assets(self):
        pwb = xlrd.open_workbook(self.products_file, encoding_override="utf-8")
        sh = pwb.sheet_by_index(0)
        cont = 1
        all_lines = sh.nrows - 1
        print "assets no: ", all_lines
        lista_no_encontrados = []
        lista_encontrados = []
        for rownum in range(1, all_lines):
            record = sh.row_values(rownum)
            try:
                code = '{:,}'.format(record[0]).split('.')[0].replace(',','.')
                asset_id = self.getAssetByCode(code)
                if asset_id:
                    self.execute('account.asset.asset',
                                 'compute_depreciation_board', asset_id)
                    asset_line_ids = self.search('account.asset.depreciation.line',
                                    (['asset_id', '=', asset_id],
                                    ['depreciation_date','<=', '31/12/2015']))
                    if not asset_line_ids:
                        print "No hay lineas de depreciacion en: ", str(record[2])
                    else:

                        print "Contabiliza para activo: ", str(record[2])
                        move_vals = {
                            'ref' : str(record[2]),
                            'journal_id' : 103,
                            'company_id' : 2,
                            'date' : '31/12/2015'
                        }
                        move_id = self.create('account.move', move_vals)
                        account = str(record[8]).split('.')[0]
                        move_line_vals1 = {
                            'name': str(record[2]),
                            'journal_id': 103,
                            'period_id': 119,
                            'date': '31/12/2015',
                            'debit': 0,
                            'credit': record[9],
                            'account_id' : self.getAccountByCode(account),
                            'move_id': move_id
                        }
                        move_line_id =  self.create('account.move.line', move_line_vals1)
                        account = str(record[13]).split('.')[0]
                        move_line_vals2 = {
                            'name' : str(record[2]),
                            'journal_id' : 103,
                            'period_id' : 119,
                            'date' : '31/12/2015',
                            'debit' : record[9],
                            'credit' : 0,
                            'account_id' : self.getAccountByCode(account),
                            'move_id' : move_id
                        } 
                        self.create('account.move.line', move_line_vals2)
                        self.execute('account.move', 'create_reversals', move_id, '31/12/2015', 119, 14)
                        self.write('account.move.line', move_line_id, {'asset_id': asset_id})
                    
                        self.write('account.asset.depreciation.line',
                                    asset_line_ids,
                                    {'move_id': move_id})
                                    
                        self.execute('account.asset.asset', 
                                'compute_depreciation_board', asset_id)
                        self.execute('account.asset.asset', 
                                'validate', asset_id)
                   
                else:
                     print "Asset no encontrado en BD: ", str(record[2])
                     #print str(record[1])
                     if str(record[1]) not in lista_no_encontrados:
                         lista_no_encontrados.append(str(record[1]))
                print "%s de %s" % (cont, all_lines)
                cont += 1
            except Exception, e:
                print "EXCEPTION: REC: ", (record, e)
       
        print lista_encontrados

    def import_product(self):
        pwb = xlrd.open_workbook(self.products_file, encoding_override="utf-8")
        sh = pwb.sheet_by_index(0)

        cont = 1
        all_lines = sh.nrows - 1
        print "assets no: ", all_lines
        for rownum in range(1, all_lines):
            record = sh.row_values(rownum)
            try:
                product_vals = {
                    "default_code": str(int(record[0])),
                    "name": record[4],
                    "categ_id": self.getCategoryByName(record[6]),
                    "uom_id": 1, # Unidad
                    "uom_po_id": record[7] in ["C","U"] and self.getUomByName(UOM_MAP[record[7]]) or 1,
                    "uos_id": self.getUomByName(UOM_MAP[record[7]]),
                    "min_unit": record[9] == "N" and "box" or (record[9] == "S" and "both" or "unit"),
                    "uos_coeff": record[10] and (1.0 / int(record[10])) or 1.0,
                    "mes_type": record[9] == "V" and "variable" or "fixed",
                    "un_ca": record[10] or 1.0,
                    "supplier_un_ca": record[10] or 1.0,
                    "supplier_kg_un": record[8] == "K" and 1.0 or 1.0,
                    "kg_un": record[8] == "K" and 1.0 or 1.0,
                    "taxes_id": [(6, 0, self.getTaxes(IVA_MAP[str(int(record[13]))][0]))],
                    "supplier_taxes_id": [(6, 0, self.getTaxes(IVA_MAP[str(int(record[13]))][1]))],
                    "standard_price": record[16],
                    "cost_method": "average",
                    "type": record[24] == "N" and "service" or "product",
                    "weight": (record[9] == "N" and record[10]) and (record[30] / (1.0 / int(record[10]))) or (record[9] == "S" and record[30] or 0.0),
                    "ca_ma": 1.0,
                    "ma_pa": 1.0,
                    "un_width": 1.0,
                    "ma_width": 1.0,
                    "ca_width": 1.0,
                    "un_height": 1.0,
                    "ma_height": 1.0,
                    "ca_height": 1.0,
                    "un_length": 1.0,
                    "ca_length": 1.0,
                    "ma_length": 1.0,
                    "pa_length": 1.0,
                    "supplier_un_width": 1.0,
                    "supplier_un_height": 1.0,
                    "supplier_un_length": 1.0,
                    "supplier_ca_ma": 1.0,
                    "supplier_ma_width": 1.0,
                    "supplier_ma_height": 1.0,
                    "supplier_ma_length": 1.0,
                    "supplier_ma_pa": 1.0,
                    "supplier_pa_length": 1.0,
                    "supplier_ca_length": 1.0,
                    "supplier_ca_height": 1.0,
                    "supplier_ca_width": 1.0,
                    "purchase_ok": True,
                    "sale_ok": True
                }
                product_id = self.create("product.product", product_vals)

                if record[25] or record[29]:
                    ean13 = str(int((record[29] or record[25])))
                    if len(ean13) == 13:
                        try:
                            self.write("product.product", [product_id], {'ean13': ean13})
                        except:
                            print u"EAN13 no váĺido", ean13

                product_data = self.read("product.product", product_id, ["product_tmpl_id"])
                supplier_id = self.getSupplierByRef(str(int(record[1])))
                if supplier_id:
                    supplier_vals = {
                        "name": supplier_id,
                        "product_code": record[3],
                        "product_tmpl_id": product_data["product_tmpl_id"][0]
                    }
                    self.create("product.supplierinfo", supplier_vals)

                self.exec_workflow("product.template", "logic_validated", product_data["product_tmpl_id"][0])
                self.exec_workflow("product.template", "commercial_validated", product_data["product_tmpl_id"][0])
                self.exec_workflow("product.template", "active", product_data["product_tmpl_id"][0])

                print "%s de %s" % (cont, all_lines)
                cont += 1
            except Exception, e:
                print "EXCEPTION: REC: ",(record, e)

        return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print u"Uso: %s <dbname> <user> <password> <products.xls>" % sys.argv[0]
    else:
        import_assets(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
