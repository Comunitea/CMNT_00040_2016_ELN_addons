-------------------------------------------------------------------------------- MIGRATION ----------------------------------------------------------------------------------------

-- No se encuentran fkeys de res partner en sale_order_line y en stock_move
update stock_move set partner_id=null where partner_id = 1993;
update sale_order_line set order_partner_id=null where order_partner_id = 455;
update sale_order_line set order_partner_id=null where order_partner_id = 1993;


-- Wrong value for product.template.cost_method: u'calc_average'
update product_template set openupgrade_legacy_8_0_cost_method = 'average' 
where id in
(select id from product_template where openupgrade_legacy_8_0_cost_method = 'calc_average');


-- DETAIL:  Key (code)=(crm.claim) already exists.
delete from ir_sequence_type where id in (select id from ir_sequence_type where code = 'crm.claim');


-- Invalid value 'validated' y también 'closed in the table 'mrp_production' for the field 'state'
-- LUEGO HAY QUE RESTABLECERLOS ACORDARSE DE HACER EL SELECT PRIMERO Y APUNTAR LOS IDS
update mrp_production set state = 'confirmed' where id in 
(select id from mrp_production where state = 'validated');

update mrp_production set state = 'confirmed' where id in 
(select id from mrp_production where state = 'cancelled');

-- insert or update on table "payment_mode" violates foreign key constraint "payment_mode_type_fkey"
alter table payment_mode drop column type;

--El campo `prodlot_id` no existe
delete from ir_ui_view where inherit_id in
(select id from ir_ui_view where arch like '%prodlot_id%');

delete from ir_ui_view where id in
(select id from ir_ui_view where arch like '%prodlot_id%');

--El campo `stock_journal_id` no existe
delete from ir_ui_view where inherit_id in
(select id from ir_ui_view where arch like '%stock_journal_id%');

delete from ir_ui_view where id in
(select id from ir_ui_view where arch like '%stock_journal_id%');

--El campo `real_date` no existe
delete from ir_ui_view where inherit_id in
(select id from ir_ui_view where arch like '%real_date%');

delete from ir_ui_view where id in
(select id from ir_ui_view where arch like '%real_date%');


-------------------------------------------------------------------------------- POSTMIGRATION ----------------------------------------------------------------------------------------
-- Restablecemos al estado validated si ya está metida por eln_production
update mrp_production set state = 'validated' where id in 
(8405,8399,8712,12121);

-- Restablecemos al estado closed
update mrp_production set state = 'closed' where id in 
(8664,8828,9026,10148,12107,12108,12117);


-- Quitamos la compañia a los productos que son de el nogal
update product_template set company_id = null where id in
(select id from product_template where company_id = 1);

-- ALMACEN QUIVAL (id 1) ubicacion stock (id 12)
-- QUIVAL: Recepciones
update stock_move set picking_type_id=1,warehouse_id=1 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_dest_id = 12);

-- QUIVAL Albaranes de salida
update stock_move set picking_type_id=2,warehouse_id=1 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 12);

-- QUIVAL: Transferencias Internas
update stock_move set picking_type_id=3,warehouse_id=1 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'internal' and location_id = 12);

-- ALMACEN EXCLUSIVAS APOLO (id 5) ubicacion stock (id 33)
-- EXCLUSIVAS APOLO: Recepciones
update stock_move set picking_type_id=16,warehouse_id=5 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_dest_id = 33);

-- EXCLUSIVAS APOLO Albaranes de salida
update stock_move set picking_type_id=17,warehouse_id=5 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 33);

-- EXCLUSIVAS APOLO: Transferencias Internas
update stock_move set picking_type_id=18,warehouse_id=5 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'internal' and location_id = 33);

-- ALMACEN DULCIVAPA PALENCIA (id 7) ubicacion stock (id 37)
-- ALMACEN DULCIVAPA PALENCIA: Recepciones
update stock_move set picking_type_id=26,warehouse_id=7 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_dest_id = 37);

-- ALMACEN DULCIVAPA PALENCIA Albaranes de salida
update stock_move set picking_type_id=27,warehouse_id=7 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 37);

-- ALMACEN DULCIVAPA PALENCIA: Transferencias Internas
update stock_move set picking_type_id=28,warehouse_id=7 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'internal' and location_id = 37);

-- ALMACEN VALQUIN (id 6) ubicacion stock (id 14)
-- ALMACEN DULCIVAPA PALENCIA: Recepciones
update stock_move set picking_type_id=21,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_dest_id = 14);

-- ALMACEN VALQUIN Albaranes de salida
update stock_move set picking_type_id=22,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 14);

-- ALMACEN VALQUIN: Transferencias Internas
update stock_move set picking_type_id=23,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'internal' and location_id = 14);

-- ALMACEN VALQUIN (id 4) ubicacion stock (id 15)
-- ALMACEN DULCIVAPA PALENCIA: Recepciones
update stock_move set picking_type_id=11,warehouse_id=4 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_dest_id = 15);

-- ALMACEN VALQUIN Albaranes de salida
update stock_move set picking_type_id=12,warehouse_id=4 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 15);

-- ALMACEN VALQUIN: Transferencias Internas
update stock_move set picking_type_id=13,warehouse_id=4 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'internal' and location_id = 15);

-- EL ALMACÉN DE EL NOGAL NO ES NECESARIO PUESTO QUE NO HAY MOVIMIENTOS CUYO COMPANY_ID=1

-- Averiguar que movimientos se quedaron sin picking type id e irlas corrigiendo, 
-- hay ubicacion de muestras (18) y reacondicionado (28) que hay que pensar si crear un nuevo tipo de operación
select stock_move.id, location_id, location_dest_id, stock_move.company_id, picking_id, stock_move.picking_type_id, stock_picking.openupgrade_legacy_8_0_type
from stock_move inner join stock_picking on stock_picking.id = stock_move.picking_id
where stock_move.picking_type_id is null and picking_id is not null;

update stock_move set picking_type_id=21,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_dest_id = 14 and stock_move.company_id=2);

update stock_move set picking_type_id=21,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_dest_id = 9 and location_id=9 and stock_move.company_id=2);

update stock_move set picking_type_id=1,warehouse_id=1 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_dest_id = 28 and stock_move.company_id=3);

update stock_move set picking_type_id=3,warehouse_id=1 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 18 and location_dest_id = 9 and stock_move.company_id=3);

update stock_move set picking_type_id=22,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.pickingAccount Payment y Purchase Payment deben desinstalarse._id 
where stock_picking.openupgrade_legacy_8_0_type = 'out' and location_id = 18 and location_dest_id = 9 and stock_move.company_id=2);

update stock_move set picking_type_id=22,warehouse_id=6 where id in 
(select stock_move.id from stock_move inner 
join stock_picking on stock_picking.id = stock_move.picking_id 
where stock_picking.openupgrade_legacy_8_0_type = 'in' and location_id = 14 and location_dest_id = 9 and stock_move.company_id=2);



-- ACTUALIZAMOS LOS TIPOS DE LOS ALBARANES
update stock_picking set picking_type_id = (select picking_type_id from stock_move where picking_id=stock_picking.id limit 1) 
where id in (select picking_id from stock_move where picking_type_id is not null group by picking_id)

-- QUERY PARA COPIAR LOS DATOS EDI DE LAS DIRECIOINES Y LA CIUDAD Y EL TLF.
-- CREAMOS UNA TABLA NUEVA PARA EVITAR RECURSIVIDAD
select * into aux_res_partner from res_partner;

-- COMPROBAR COMO ESTÁ A QUE VALORES SE VA A ACTUALIZAR
select rp.id, rp.name,
(arp.name || ' / ' || rcs.name || ' (' || rp.zip || ')') as new_name,
RP.CITY, rpa.city as new_city , rp.street,
rpa.gln_rf, rpa.gln_rm, rpa.gln_de, rpa.gln_co, rcs.name, rp.parent_id
from aux_res_partner rp
join res_country_state rcs on rcs.id = rp.state_id
join aux_res_partner arp on  arp.id = rp.parent_id
join res_partner_address rpa on rpa.openupgrade_7_migrated_to_partner_id = rp.id
where rp.name  = '/' and not rp.parent_id isnull

--HACEMOS EL UPDATE PARA LOS CAMPOS: NAME, CITY Y EDI
update res_partner rp
set
name = nt.new_name,
city = nt.new_city,
gln_rf = nt.gln_rf, gln_rm = nt.gln_rm, gln_de = nt.gln_de, gln_co = nt.gln_co
from
(
select rp.id, rp.name, rp.state_id, rcs.name, rp.parent_id,
(arp.name || ' / ' || rcs.name || ' (' || rp.zip || ')') as new_name,
rpa.city as new_city , rp.street,
rpa.gln_rf, rpa.gln_rm, rpa.gln_de, rpa.gln_co
from res_partner rp
join res_country_state rcs on rcs.id = rp.state_id
join aux_res_partner arp on  arp.id = rp.parent_id
join res_partner_address rpa on rpa.openupgrade_7_migrated_to_partner_id = rp.id
where rp.name  = '/' and not rp.parent_id isnull
)
as nt
where nt.id = rp.id


-- ARREGLAR VISTA CONTABILIDAD/PAGOS/EFECTOS
delete from ir_ui_view where id in (select id from ir_ui_view where name = 'Invoice Payments Select');
delete from ir_ui_view where id in (select id from ir_ui_view where name = 'Payments');