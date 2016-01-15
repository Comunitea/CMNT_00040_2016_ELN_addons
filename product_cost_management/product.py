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
from osv import fields, osv
import decimal_precision as dp
import time
from tools.translate import _

def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r

class update_product_cost_label(osv.osv_memory):
    _name = 'update.product.cost.label'

    def action_product_costs(self, cr, uid, ids, context=None):
        if context is None: context = {}
        c = context.copy()
        c['cron'] = True
        return self.pool.get('product.costs.line').get_product_costs(cr,uid,ids,c)
update_product_cost_label()

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
         'cost_method': fields.selection([('standard','Standard Price'),
                                          ('average','Average Price'),
                                          ('calc_average', 'Average price calculated')],
                                        'Costing Method',
                                         required=True),

    }
product_template()

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'theoric_cost': fields.float('Theoric Cost', digits_compute=dp.get_precision('Purchase Price'),),
        'cost_structure_id': fields.many2one('cost.structure',
                                             'Cost Structure')
    }

    def action_product_costs(self, cr, uid, ids, context=None):
        """calls to simplified traceability wizard"""
        if context is None: context = {}

        value=self.pool.get('product.costs.line').get_product_costs(cr,uid,ids,context)
        return value

    def _calculate_cost_pmc(self, cr, uid, ids, product=False, context=None):
        if product:
            prod = self.pool.get('product.product').browse(cr,uid, product, context)
            cost_ldm_pmp = self.pool.get('product.costs.line')._get_cost_raw_material(cr, uid, ids, prod, False,context)
            return cost_ldm_pmp or 0.0 

    def action_update_cost_product(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        prod_cost = self.pool.get('product.cost')
        line = self.pool.get('product.cost.lines')
        product = self.pool.get('product.product')
        if context.get('product_id', False):
            cost_ids = prod_cost.search(cr, uid, [('product_id','=', context['product_id'])], order="date desc")
            if cost_ids:
                lines = line.search(cr, uid, [('product_cost','=',cost_ids[0]), ('total','=',True)], order="sequence desc")
                line_warehouse = line.search(cr, uid, [('product_cost','=',cost_ids[0]), ('sequence','=',4)])
                if lines and line_warehouse:
                    line_cost = line.browse(cr, uid, lines[0])
                    pmc_raw_material = self._calculate_cost_pmc(cr, uid, ids, context['product_id'], context)
                    pmc_warehouse = line.browse(cr, uid, line_warehouse[0]).theoric_cost
                    if product.browse(cr, uid, context['product_id']).cost_method == 'calc_average':
                        product.write(cr, uid, context['product_id'], {'standard_price': pmc_raw_material + pmc_warehouse,
                                                                       'theoric_cost': line_cost.theoric_cost})
                    else:
                        product.write(cr, uid, context['product_id'], {'standard_price': line_cost.real_cost,
                                                                       'theoric_cost': line_cost.theoric_cost})


                else:
                    raise osv.except_osv(_('Warning !'), _('Could not update costs. No cost lines were found for this product!'))
            else:
                raise osv.except_osv(_('Warning !'), _('Could not update costs. There are no costs associated with this product!'))
        return True

product_product()

class product_cost(osv.osv):
    _name = 'product.cost'
    _rec_name = "product_id"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product Cost',
                                      required=True),
        'product_cost_lines': fields.one2many('product.cost.lines',
                                              'product_cost', 'Costs'),
        'date': fields.datetime('Date', required=True)
    }
product_cost()

class product_cost_lines(osv.osv):
    _name = 'product.cost.lines'
    _columns = {
        'product_cost': fields.many2one('product.cost', 'Cost'),
        'sequence': fields.integer('Sequence', required=True),
        'name': fields.char('Name', size=255, required=True),
        'theoric_cost': fields.float('Theoric Cost', required=True, digits_compute=dp.get_precision('Purchase Price'),),
        'real_cost': fields.float('Real Cost', required=True, digits_compute=dp.get_precision('Purchase Price'),),
        'total': fields.boolean('Total')
    }
    _defaults = {
        'theoric_cost': 0.00,
        'real_cost': 0.00
    }
product_cost_lines()

class product_pricelist_item(osv.osv):
    _inherit = "product.pricelist.item"

    def _price_field_get(self, cr, uid, context=None):
        res = super(product_pricelist_item, self)._price_field_get(cr, uid, context)
        res.append((-3, _('Cost Structure')))
        return res

    _columns = {
        'base': fields.selection(_price_field_get, 'Based on', required=True, size=-1, help="The mode for computing the price for this rule."),
        'cost_type_id': fields.many2one('cost.type', 'Cost type')
    }
product_pricelist_item()


class product_pricelist(osv.osv):
    _inherit = "product.pricelist"

    def price_get_multi(self, cr, uid, pricelist_ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param pricelist_ids:
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """

        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst
        # _create_parent_category_list

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        product_template_obj = self.pool.get('product.template')
        product_category_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        price_type_obj = self.pool.get('product.price.type')

        # product.pricelist.version:
        if not pricelist_ids:
            pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [], context=context)

        pricelist_version_ids = self.pool.get('product.pricelist.version').search(cr, uid, [
                                                        ('pricelist_id', 'in', pricelist_ids),
                                                        '|',
                                                        ('date_start', '=', False),
                                                        ('date_start', '<=', date),
                                                        '|',
                                                        ('date_end', '=', False),
                                                        ('date_end', '>=', date),
                                                    ])
        if len(pricelist_ids) != len(pricelist_version_ids):
            raise osv.except_osv(_('Warning !'), _("At least one pricelist has no active version !\nPlease create or activate one."))

        # product.product:
        product_ids = [i[0] for i in products_by_qty_by_partner]
        #products = dict([(item['id'], item) for item in product_obj.read(cr, uid, product_ids, ['categ_id', 'product_tmpl_id', 'uos_id', 'uom_id'])])
        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_dict = dict([(item.id, item) for item in products])

        # product.category:
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        results = {}
        for product_id, qty, partner in products_by_qty_by_partner:
            for pricelist_id in pricelist_ids:
                price = False

                tmpl_id = products_dict[product_id].product_tmpl_id and products_dict[product_id].product_tmpl_id.id or False

                categ_id = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                if categ_ids:
                    categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                    categ_where_i = '(i.categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'
                    categ_where_i = '(i.categ_id IS NULL)'

                if partner:
                    partner_where = 'base <> -2 OR %s IN (SELECT name FROM product_supplierinfo WHERE product_id = %s) '
                    partner_args = (partner, tmpl_id)
                else:
                    partner_where = 'base <> -2 '
                    partner_args = ()
                  
                query = (  
                'SELECT '
                    'i.*, pl.currency_id , p.* '
                'FROM '
                    'product_pricelist_item AS i '
                    'JOIN product_pricelist_version AS v '
                        'ON i.price_version_id = v.id '
                    'JOIN product_pricelist AS pl '
                        'ON v.pricelist_id = pl.id '
                    'LEFT OUTER JOIN ( '
                        'WITH RECURSIVE subtree(depth, categ_id, parent_id, name) AS ( '
                                'SELECT 0, id, parent_id, name FROM product_category WHERE parent_id is NULL '
                            'UNION '
                                'SELECT depth+1, m.id, m.parent_id, m.name '
                                'FROM subtree t, product_category m '
                                'WHERE m.parent_id = t.categ_id '
                        ') '
                        'SELECT * '
                        'FROM subtree '
                        'WHERE (' + categ_where + ' OR (categ_id IS NULL)) ' 
                    ') AS p '
                        'on i.categ_id = p.categ_id '
                'WHERE '
                    '(product_tmpl_id IS NULL OR product_tmpl_id = %s) ' 
                    'AND (product_id IS NULL OR product_id = %s) '
                    'AND (' + categ_where_i + ' OR (i.categ_id IS NULL)) ' 
                    'AND (' + partner_where + ') ' 
                    'AND price_version_id = %s ' 
                    'AND (min_quantity IS NULL OR min_quantity <= %s) '
                'ORDER BY ' 
                    'sequence, depth desc '  
                ) % ((tmpl_id, product_id) + partner_args + (pricelist_version_ids[0], qty))
                              
                cr.execute(query)
                res1 = cr.dictfetchall()
                uom_price_already_computed = False
                for res in res1:
                    if res:
                        if res['base'] == -1:
                            if not res['base_pricelist_id']:
                                price = 0.0
                            else:
                                price_tmp = self.price_get(cr, uid,
                                        [res['base_pricelist_id']], product_id,
                                        qty, partner=partner, context=context)[res['base_pricelist_id']]
                                ptype_src = self.browse(cr, uid, res['base_pricelist_id']).currency_id.id
                                uom_price_already_computed = True
                                price = currency_obj.compute(cr, uid, ptype_src, res['currency_id'], price_tmp, round=False)
                        elif res['base'] == -2:
                            # this section could be improved by moving the queries outside the loop:
                            where = []
                            if partner:
                                where = [('name', '=', partner) ]
                            sinfo = supplierinfo_obj.search(cr, uid,
                                    [('product_id', '=', tmpl_id)] + where)
                            price = 0.0
                            if sinfo:
                                qty_in_product_uom = qty
                                product_default_uom = product_template_obj.read(cr, uid, [tmpl_id], ['uom_id'])[0]['uom_id'][0]
                                supplier = supplierinfo_obj.browse(cr, uid, sinfo, context=context)[0]
                                seller_uom = supplier.product_uom and supplier.product_uom.id or False
                                if seller_uom and product_default_uom and product_default_uom != seller_uom:
                                    uom_price_already_computed = True
                                    qty_in_product_uom = product_uom_obj._compute_qty(cr, uid, product_default_uom, qty, to_uom_id=seller_uom)
                                cr.execute('SELECT * ' \
                                        'FROM pricelist_partnerinfo ' \
                                        'WHERE suppinfo_id IN %s' \
                                            'AND min_quantity <= %s ' \
                                        'ORDER BY min_quantity DESC LIMIT 1', (tuple(sinfo),qty_in_product_uom,))
                                res2 = cr.dictfetchone()
                                if res2:
                                    price = res2['price']
                        elif res['base'] == -3:
                                if not res['cost_type_id']:
                                    price = 0.0
                                else:
                                    cost_type = self.pool.get('cost.type').browse(cr, uid, res['cost_type_id'])
                                    cr.execute(
                                        "SELECT line.theoric_cost "
                                        "FROM product_cost_lines AS line "
                                        "INNER JOIN product_cost AS cost "
                                        "ON cost.id = line.product_cost "
                                        "WHERE cost.product_id =" + str(product_id) + " "
                                        "AND line.total=True AND line.name='"+ cost_type.name + "' "
                                        "ORDER BY cost.date desc")
                                    r = cr.dictfetchall()
                                    if r:
                                        #Ver si es necesaria esta linea (uom_price_already_computed). Originalmente no estaba puesta por pexego pero 
                                        #la pongo porque creo que debe estar. Falta probarlo cuando funcione el theoric_cost
                                        uom_price_already_computed = True 
                                        price = r[0]['theoric_cost']
                        else:
                            price_type = price_type_obj.browse(cr, uid, int(res['base']))
                            uom_price_already_computed = True
                            price = currency_obj.compute(cr, uid,
                                    price_type.currency_id.id, res['currency_id'],
                                    product_obj.price_get(cr, uid, [product_id],
                                    price_type.field, context=context)[product_id], round=False, context=context)

                        if price is not False:
                            surcharge = res['price_surcharge'] or 0.0 
                            if 'uom' in context: 
                                product = products_dict[product_id]
                                #uom = product.uos_id or product.uom_id 
                                #Comento esta linea anterior porque sino dividia siempre el precio unidad entre las unidades caja y era erróneo
                                #y añado la linea siguiente sin el uos_id
                                uom = product.uom_id
                                surcharge = product_uom_obj._compute_price(cr, uid, uom.id, surcharge, context['uom'])
                            
                            price_limit = price
                            price = price * (1.0+(res['price_discount'] or 0.0))
                            price = rounding(price, res['price_round']) #TOFIX: rounding with tools.float_rouding
                            price += surcharge
                            
                            if res['price_min_margin']:
                                price = max(price, price_limit+res['price_min_margin'])
                            if res['price_max_margin']:
                                price = min(price, price_limit+res['price_max_margin'])
                            break

                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        price = False

                if price:
                    results['item_id'] = res['id']
                    if 'uom' in context and not uom_price_already_computed:
                        product = products_dict[product_id]
                        uom = product.uos_id or product.uom_id
                        price = product_uom_obj._compute_price(cr, uid, uom.id, price, context['uom'])

                if results.get(product_id):
                    results[product_id][pricelist_id] = price
                else:
                    results[product_id] = {pricelist_id: price}

        return results

product_pricelist()
