import { Component, ViewChild } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/
import { FormBuilder, FormGroup } from '@angular/forms';

//import { HostListener } from '@angular/core';
import { AuxProvider } from '../../providers/auxiliar/auxiliar'


/**
 * Generated class for the TreepickPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
//import { HomePage } from '../home/home';
import { SlideopPage } from '../slideop/slideop';
import { Storage } from '@ionic/storage';
import { TreepickPage } from '../treepick/treepick'
//import  { LocationPage } from '../location/location'
//import { ComponentsModule } from '../../components/components.module'
//import { ProductProductComponent} from '../../components/product-product/product-product'
//import { StockPickingComponent} from '../../components/stock-picking/stock-picking'
import { StockOperationComponent } from '../../components/stock-operation/stock-operation'


import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';
//import { BarcodeScanner } from '../../providers/odoo-connector/barcode_scanner';

@IonicPage()
@Component({
    selector: 'page-treeops',
    templateUrl: 'treeops.html',
})
export class TreeopsPage {

    @ViewChild('scan') myScan;
    @ViewChild(StockOperationComponent) pack_operation: StockOperationComponent;
    pick: {}
    cargar = true;
    pick_id = 0
    limit = 25
    offset = 0
    order = 'picking_order, product_id asc'
    model = 'stock.picking'
    domain = []
    pick_domain = []
    record_count = 0
    isPaquete: boolean = true;
    isProducto: boolean = false;
    info_pick: boolean
    scan = ''
    barcodeForm: FormGroup;
    model_fields = {'stock.location': 'location_id', 'stock.production.lot': 'lot_id'}
    whatOps: string
    aux: AuxProvider
    filter_user = ''

    constructor(public navCtrl: NavController, public navParams: NavParams,
        private formBuilder: FormBuilder, public alertCtrl: AlertController,
        private storage: Storage, private odoo: OdooProvider) {

        this.pick = {};
        this.pick_id = this.navParams.data.picking_id;
        this.model = this.navParams.data.model || this.model;
        this.record_count = 0;
        this.cargar = true;
        this.scan = '';
        this.storage.get('WhatOps').then((val) => {
            if (val == null) {
                this.whatOps = 'Todas'
            } else {
                this.whatOps = val
            }
        })
        this.barcodeForm = this.formBuilder.group({
            scan: ['']
        });
        if (this.navParams.data.info_pick != null) {
            this.info_pick = this.navParams.data.info_pick
        } else {
            this.info_pick = true
        }
        this.loadList();
    }

    seeAll2() {
        //this.filter_user = this.whatOps
    }

    infopick(val) {
        this.info_pick = val
        this.show_scan()
    }

    goHome() {
        this.navCtrl.setRoot(TreepickPage, { borrar: true, login: null });
    }

    show_scan() {
        setTimeout(() => {
            this.myScan.setFocus();
        }, 150);
    }

    loadList(id = 0) {
        this.cargar = true;
        var model = 'warehouse.app'
        var method = 'get_pick_id'
        if (id == 0) {
            id = this.pick_id
        }
        var values = { 'id': id, 'model': this.model }
        this.odoo.execute(model, method, values).then((res) => {
            this.cargar = false
            if (res['id'] != 0) {
                this.pick = res
                this.pick['whatOps'] = this.whatOps
                this.pick['model'] = this.model
                this.record_count = this.pick['pack_operation_count']
                this.show_scan()
                return true;
            }
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
            });
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    loadNext() {
        this.offset = Math.max(this.offset + this.limit, this.record_count - this.limit);
        this.loadList();
    }

    loadPrev() {
        this.offset = Math.min(0, this.offset - this.limit);
        this.loadList();
    }

    notify_do_op(op_id) {
        console.log("Do op")
    }

    reorder_picks() {
        this.cargar = true
        var ops = []
        ops = this.pick['pack_operation_ids']
        var len1 = ops.length - 1
        var new_picks = []
        var index = 0
        for (var op in ops) {
            index = len1 - Number(op)
            new_picks.push(ops[index])
        }
        this.pick['pack_operation_ids'] = new_picks
        this.cargar = false
        this.show_scan()
    }

    filter_picks() {
        let filter: boolean
        let filter_picks = []
        if (this.whatOps == 'Todas') {
            filter_picks = this.pick['pack_operation_ids']
            return filter_picks
        }
        else if (this.whatOps == 'Realizadas') {
            filter = true
        }
        else {
            filter = false
        }
        filter_picks = this.pick['pack_operation_ids'].filter(op => op.pda_done == filter)
        return filter_picks

    }

    openLocation(id) {
        return
        //this.navCtrl.push(LocationPage, {location_id: id})
    }

    submitScan() {
        let scan = this.barcodeForm.value['scan']
        return this.Scan(scan)
    }

    findId(value) {
        for (var op in this.pick['pack_operation_ids']) {
            var opObj = this.pick['pack_operation_ids'][op];
            console.log(opObj);
            if (opObj[this.model_fields[value['model']]][0] == value['id']) {
                return { 'op_id': opObj['id'], 'index': op, 'ops': this.pick['pack_operation_ids'], 'origin': true }
            }
        }
        return false
    }

    doAssign(id, do_assign) {
        this.cargar = true;
        var values = { 'id': id, 'action': do_assign }
        var method = 'pda_do_assign_from_pda'
        this.odoo.execute(this.model, method, values).then((value) => {
            console.log(this.model)
            if (value) {
                if (value) {
                    this.filter_user = 'assigned';
                    this.loadList()
                }
                else {
                    this.filter_user = ''
                    this.show_scan()
                }
            }
            else {
                this.presentAlert('Error!', 'Error al escribir en Odoo');
            }
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo recuperar el usuario');
            });
    }

    doPreparePartial(id) {
        this.cargar = true;
        var method = 'pda_do_prepare_partial_from_pda'
        var values = { 'id': id }
        this.odoo.execute(this.model, method, values).then((value) => {
            if (value) {
                this.loadList()
            }
            else {
                this.presentAlert('Error!', 'No se ha podido preparar el albarán');
                this.show_scan()
            }
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo preparar el albarán')
            });
    }

    ask_doTransfer(id) {
        let alert = this.alertCtrl.create({
            title: 'Confirmación',
            message: 'Finalizar albarán?',
            buttons: [
                {
                    text: 'No',
                    role: 'cancel',
                    handler: () => {
                        this.show_scan()
                    }
                },
                {
                    text: 'Si',
                    handler: () => {
                        this.doTransfer(id)
                    }
                }
            ]
        });
        alert.present();
    }

    treepick() {
        this.navCtrl.setRoot(TreepickPage);
    }

    doTransfer(id) {
        this.cargar = true;
        var method = 'pda_do_transfer_from_pda'
        var values = { 'id': id }
        //var object_id = {}
        this.cargar = true;
        this.odoo.execute(this.model, method, values).then((value) => {
            //object_id = value;
            this.navCtrl.setRoot(TreepickPage)
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
                this.show_scan()
            });
    }

    doOp(index, id, do_id) {
        var self = this;
        var model = 'stock.pack.operation'
        var method = 'doOp'
        var values = { 'id': id, 'do_id': do_id }
        //var object_id

        this.odoo.execute(model, method, values).then((value) => {
            //object_id = value;
            let op = self.pick['pack_operation_ids'][index]
            op['pda_done'] = true,
                op['qty_done'] = op['product_qty']
            this.show_scan()
            //self.loadList()
        })
            .catch(() => {
                this.presentAlert('Error!', 'Error al marcar la operacion como realizada');
                this.show_scan()
            });
    }

    find_op(scan) {
        let val: {}
        let pick = { 'id': this.pick_id, 'model': this.pick['model'], 'name': this.pick['name'], 'user_id': this.pick['user_id'] }
        for (var op in this.pick['pack_operation_ids']) {
            var opObj = this.pick['pack_operation_ids'][op];
            console.log(opObj);
            //Busco por lote
            if (opObj['lot_id'] && opObj['lot_id'][1] == scan) {
                val = { op_id: opObj['id'], index: op, ops: this.pick['pack_operation_ids'], origin: true, lot_id: true, pick: pick }
                return val
            }
            if (opObj['ean13'] && opObj['ean13'] == scan) {
                val = { op_id: opObj['id'], index: op, ops: this.pick['pack_operation_ids'], origin: true, pick: pick }
                return val
            }
        }

    }

    openOp_NOUSAR(op_id, op_id_index) {
        let val = { op_id: op_id, index: op_id_index, ops: this.filter_picks(), parent: { 'id': this.pick_id, 'model': this.model } }
        this.navCtrl.setRoot(SlideopPage, val)
    }

    getObjectId_NOUAR(values) {
        var model = 'warehouse.app'
        var method = 'get_object_id'
        this.odoo.execute(model, method, values).then((value) => {
            var res = this.findId(value);
            if (res) {
                res['parent'] = { 'id': this.pick_id, 'model': this.model }
                this.navCtrl.setRoot(SlideopPage, res);
            }
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
            });

    }

    Scan(scan) {
        //this.treeForm.value['scan'] = scan
        this.barcodeForm.reset()
        if (!scan) { return }
        let val = this.find_op(scan)
        this.barcodeForm.value['scan'] = ''
        if (val) {
            this.navCtrl.setRoot(SlideopPage, val)
        }
        else {
            this.presentAlert('Aviso!', 'No he encontrado nada para <' + scan + '>');
            this.show_scan()
        }
    }
}
