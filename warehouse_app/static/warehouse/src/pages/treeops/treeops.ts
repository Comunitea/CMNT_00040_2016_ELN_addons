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

declare var OdooApi: any


@IonicPage()
@Component({
  selector: 'page-treeops',
  templateUrl: 'treeops.html',
})
export class TreeopsPage {

  @ViewChild('scanPackage') myScanPackage;

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) { 
    this.myScanPackage.setFocus();
     }
  
  
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
  
  scan = ''
  treeForm: FormGroup;
  model_fields = {'stock.quant.package': 'package_id', 'stock.location': 'location_id', 'stock.production.lot': 'lot_id'}
  whatOps: string
  aux: AuxProvider
  constructor(public navCtrl: NavController, public navParams: NavParams,  private formBuilder: FormBuilder,public alertCtrl: AlertController, private storage: Storage) {
    this.aux = new AuxProvider
    this.pick = {};
    this.pick_id = this.navParams.data.picking_id;
    this.record_count = 0;    
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
  }
  ops
  seeAll(){
    if (this.whatOps=='Todas'){
      this.whatOps='Pendientes'
    }
    else
      {this.whatOps='Todas'}
    this.storage.set('WhatOps', this.whatOps); 
  }

  ionViewLoaded() {
    
    setTimeout(() => {
      this.myScanPackage.setFocus();
    },150);
    
     }
  goHome(){this.navCtrl.setRoot(TreepickPage, {borrar: true, login: null});}
  
  loadList(id = 0){
    
    var self = this
    var model = 'warehouse.app'
    var method = 'get_object_id'
    if (id==0){
      id = this.pick_id
    }
    var values = {'id': id, 'model': 'stock.picking'}

    self.storage.get('CONEXION').then((val) => {
      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.call(model, method, values).then(
                function (res) {
                  //AQUI DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO
                  //Estoy scaneando ORIGEN
                  
                  if (res['id']!=0){
                    
                    self.pick = res['values']
                    self.record_count = self.pick['pack_operation_count']
                    return true;
                  }
                },
                function () {
                  
                  self.presentAlert('Falla!', 'Imposible conectarse');
                  }
                );
              },
            function () {
              
              self.presentAlert('Falla!', 'Imposible conectarse');
              }
            );
        }
      
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

  openOp(op_id, op_id_index){
    this.navCtrl.push(SlideopPage, {op_id: op_id, index: op_id_index, ops: this.pick['pack_operation_ids']})
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
    
    self.storage.get('CONEXION').then((val) => {
      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.call(model, method, values).then(
                function (value) {

                  
                  setTimeout(() => {
                    var res = self.findId(value);
                    if (res) {
                      self.navCtrl.push(SlideopPage, res);}
                  },150);
                  
                  
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
            
              }
              
              
          });
    
      
        }

      
  doTransfer(id){
    var self = this;
    var model = 'stock.picking'
    var method = 'doTransfer'
    var values = {'id': id}
    var object_id = {}

    
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.call(model, method, values).then(
                function (value) {
                  object_id = value;
                  self.cargar = false;
                  self.loadList()
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
                  self.cargar = false;

             
              }
              this.navCtrl.push(TreepickPage);
              
          });
    
      }

  
  doOp(id, do_id){
    var self = this;
    var model = 'stock.pack.operation'
    var method = 'doOp'
    var values = {'id': id, 'do_id': do_id}
    var object_id


    this.storage.get('CONEXION').then((val) => {

      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.call(model, method, values).then(
                function (value) {
                  object_id = value;
                  /*self.ionViewLoaded()*/
                  self.loadList();
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
                  self.cargar = false;

             
              }
          });
  }


}
