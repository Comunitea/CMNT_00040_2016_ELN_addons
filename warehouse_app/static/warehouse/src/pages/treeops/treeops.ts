import { Component, ViewChild} from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/
import {FormBuilder, FormGroup } from '@angular/forms';

import { HostListener } from '@angular/core';
import { AuxProvider } from '../../providers/aux/aux'


/**
 * Generated class for the TreepickPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
import { HomePage } from '../home/home';
import { SlideopPage } from '../slideop/slideop';
import { Storage } from '@ionic/storage';
import { TreepickPage } from '../treepick/treepick'
import  { LocationPage } from '../location/location'
//import { ComponentsModule } from '../../components/components.module'
import { ProductProductComponent} from '../../components/product-product/product-product'
import { StockPickingComponent} from '../../components/stock-picking/stock-picking'
import { StockOperationComponent} from '../../components/stock-operation/stock-operation'


import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';
import { BarcodeScanner } from '../../providers/odoo-connector/barcode_scanner';

@IonicPage()
@Component({
  selector: 'page-treeops',
  templateUrl: 'treeops.html',
})
export class TreeopsPage {

  @ViewChild('scanPackage') myScanPackage;
  @ViewChild(StockOperationComponent) pack_operation: StockOperationComponent;


  pick

  cargar = true;
  pick_id = 0
  limit = 25
  offset = 0
  order = 'picking_order, product_id asc'
  model = 'stock.pack.operation'
  domain = []
  pick_domain = []
  record_count = 0
  isPaquete: boolean = true;
  isProducto: boolean = false;
  info_pick: boolean
  scan = ''
  treeForm: FormGroup;
  model_fields = {'stock.quant.package': 'package_id', 'stock.location': 'location_id', 'stock.production.lot': 'lot_id'}
  whatOps: string
  aux: AuxProvider

  constructor(public Scanner: BarcodeScanner, public navCtrl: NavController, public navParams: NavParams,  private formBuilder: FormBuilder,public alertCtrl: AlertController, private storage: Storage, private odoo: OdooProvider) {
    this.aux = new AuxProvider
    this.info_pick = true
    this.pick = {};
    this.pick_id = this.navParams.data.picking_id;
    this.model = this.navParams.data.model || this.model;
    this.record_count = 0;
    this.cargar = true;
    this.scan = '';
    this.storage.get('WhatOps').then((val) => {
      if (val==null) {
        this.whatOps='Todas'}
      else {
        this.whatOps = val}
      })
    this.treeForm = this.formBuilder.group({
      scan: ['']
    });
  }

  ionViewWillEnter(){
    this.loadList();
    this.pick['whatOps'] = this.whatOps
  }
  seeAll2(){
    this.aux.filter_user = this.whatOps
  }
  
  infopick(val){
    this.info_pick = val
  }
  ionViewLoaded() {

    setTimeout(() => {
      this.myScanPackage.setFocus();
    },150);

     }
  goHome(){this.navCtrl.setRoot(TreepickPage, {borrar: true, login: null});}
  loadOp(id=0){
  }
  loadList(id=0){
    this.cargar = true;
    var model = 'warehouse.app'
    var method = 'get_object_id'
    if (id==0){
      id = this.pick_id
    }
    var values = {'id': id, 'model': this.model}
    this.odoo.execute(model, method, values).then((res)=>{
      this.cargar = false
      if (res['id']!=0){
        this.pick = res['values']
        this.record_count = this.pick['pack_operation_count']
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
  loadNext(){
    this.offset = Math.max(this.offset + this.limit, this.record_count - this.limit);
    this.loadList();
  }
  loadPrev(){
    this.offset = Math.min(0, this.offset - this.limit);
    this.loadList();
  }

  notify_do_op(op_id){
    console.log("Do op")
  }
  reorder_picks(){
    this.cargar = true
    var ops = []
    ops = this.pick['pack_operation_ids']
    var len1 = ops.length -1
    var new_picks = []
    var index = 0
    for (var op in ops) {
      index = len1 - Number(op)
      new_picks.push(ops[index])
    }
    this.pick['pack_operation_ids'] = new_picks
    this.cargar = false
  }
  filter_picks(){
    let filter: boolean
    let filter_picks = []
    if (this.whatOps=='Todas') {
      filter_picks = this.pick['pack_operation_ids']
      return filter_picks
    }
    else if (this.whatOps=='Realizadas'){
      filter=true
    }
    else {
      filter=false
    }
    filter_picks = this.pick['pack_operation_ids'].filter(op => op.pda_done == filter)
    return filter_picks

  }
  openLocation(id){
    return
    //this.navCtrl.push(LocationPage, {location_id: id})
  }

  openOp(op_id, op_id_index){
    this.navCtrl.push(SlideopPage, {op_id: op_id, index: op_id_index, ops: this.filter_picks()})
  }

  submitScan (){
    this.getObjectId({'model': ['stock.location', 'stock.quant.package', 'stock.production.lot'], 'search_str' : this.treeForm.value['scan']})
    this.treeForm.reset();
  }

  findId (value){

    for (var op in this.pick['pack_operation_ids']){

      var opObj = this.pick['pack_operation_ids'][op];
      console.log(opObj);
      if (opObj[this.model_fields[value['model']]][0] == value['id']){
        return {'op_id': opObj['id'], 'index': op, 'ops': this.pick['pack_operation_ids'], 'origin': true}
      }
    }
    return false
  }

  getObjectId(values){
    var self = this;

    
    var object_id = {}
    var model = 'warehouse.app'
    var method = 'get_object_id'
    this.odoo.execute(model, method, values).then((value)=>{
      var res = self.findId(value);
                    if (res) {
                      self.navCtrl.push(SlideopPage, res);}
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
    });

  }


  doAssign(id, do_assign){
    this.cargar = true;
    var values = {'id': id, 'action': do_assign}
    var method = 'pda_do_assign_from_pda'
    this.odoo.execute(this.model, method, values).then((value)=>{
      if (value){
        if (value){
          this.aux.filter_user='Assigned';
          this.loadList()
        }
        else {
          this.aux.filter_user=''
        }
        this.navCtrl

      }
      else {
        this.presentAlert('Error!', 'Error al escribir en Odoo');
      }
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar el usuario');
    });

  }

  doPreparePartial(id){
    this.cargar = true;
    var method = 'pda_do_prepare_partial_from_pda'
    var values = {'id': id}
    this.odoo.execute(this.model, method, values).then((value)=>{
      if (value) {
        this.loadList()
      }
      else {
        this.presentAlert('Error!', 'No se ha podido preparar el albarán');
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


  doTransfer(id){
    this.cargar = true;
    var method = 'pda_do_transfer_from_pda'
    var values = {'id': id}
    var object_id = {}
    this.cargar = true;
    this.odoo.execute(this.model, method, values).then((value)=>{
      object_id = value;
      this.navCtrl.push(TreepickPage)
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
    });
  }

  doOp(index, id, do_id){

    var self = this;
    var model = 'stock.pack.operation'
    var method = 'doOp'
    var values = {'id': id, 'do_id': do_id}
    var object_id

    this.odoo.execute(model, method, values).then((value)=>{
      object_id = value;
      let op = self.pick['pack_operation_ids'][index]
      op['pda_done'] = true,
      op['qty_done'] = op['product_qty']
      //self.loadList()
    })
    .catch(() => {
      this.presentAlert('Error!', 'Error al marcar la operacion como realizada');
    });
  }




find_op (scan){
  let val: {}
  for (var op in this.pick['pack_operation_ids']){
    var opObj = this.pick['pack_operation_ids'][op];
    console.log(opObj);
    //Busco por lote
    if (opObj['lot_id'] && opObj['lot_id']['name'] == scan || opObj['pda_product_id'] && opObj['pda_product_id']['ean13'] == scan){
      val = {op_id: opObj['id'], index: op, ops: this.pick['pack_operation_ids'], origin: true}
      return val
    }

  }

  }
Scan(scan){
  let val = this.find_op(scan)
  if (val){
    this.navCtrl.push(SlideopPage, val)
  }
  else{
    this.presentAlert('Aviso!', 'No he </hr> encontrado\n nada\n <' + scan + '>');
  }
}
}
