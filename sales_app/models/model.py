# -*- coding: utf-8 -*-

from openerp.service import model
import openerp
from openerp.osv.orm import except_orm

def execute_cr(cr, uid, obj, method, *args, **kw):
    object = openerp.registry(cr.dbname).get(obj)
    if object is None:
        raise except_orm('Object Error', "Object %s doesn't exist" % obj)
    user_obj = openerp.registry(cr.dbname).get('res.users')
    user = getattr(user_obj, 'browse')(cr, uid, [uid])
    for arg in args:
        if arg and isinstance(arg, dict):
            app_company_id = arg.get('app_company_id', False)
            if app_company_id and user.company_id.id != app_company_id:
                user.write({'company_id': app_company_id})

    return getattr(object, method)(cr, uid, *args, **kw)


model.execute_cr = execute_cr