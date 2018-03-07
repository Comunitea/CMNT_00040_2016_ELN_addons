import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { Slides } from 'ionic-angular';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/

import { HostListener } from '@angular/core';
import { HomePage } from '../home/home';
import { TreeopsPage } from '../treeops/treeops';
import { Storage } from '@ionic/storage';
import { AuxProvider } from '../../providers/aux/aux'
/**
 * Generated class for the ManualPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

declare var OdooApi: any

@IonicPage()
@Component({
  selector: 'page-manual',
  templateUrl: 'manual.html',
})

export class ManualPage {

  @ViewChild('scan') myScan ;
  


  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) { 
    if (!this.myScan._isFocus && this.input!=1){this.myScan.setFocus()};
     }

  
  
  move_id = 0
  model = 'stock.move'
  move_fields = ['id', 'product_id', 'lot_id', 'restrict_package_id', 'result_package_id', 'restrict_lot_id', 'package_qty', 'location_id', 'location_dest_id']
  move = ['id', 'product_id', 'product_id_name', 'restrict_package_id', 'restrict_package_id_name', 'result_package_id', 'result_package_id_name', 'restrict_lot_id', 'restrict_lot_id_name', 'package_qty', 'location_id', 'location_dest_id', 'location_id_name', 'location_dest_id_name']
  domain = []
  package_qty: boolean = true;
  message = ''
  state: number = 0; /* 0 origen 1 destino 2 validar */
  scan_id: string = ''
  restrict_package_id = 0;
  restrict_package_id_name = '';
  restrict_lot_id = 0;
  restrict_lot_id_name = '';
  result_package_id = 0;
  result_package_id_name = '';
  location_id = 0;
  location_id_name = '';
  location_dest_id = 0;
  location_dest_id_name = '';
  product_qty = 0;
  product_id = 0;
  product_id_name = '';
  uom = '';
  total_package_qty = 0;
  models = []
  last_scan = ''
  input: number = 0;
  barcodeForm: FormGroup;
  
  constructor(public navCtrl: NavController, public toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, public storage: Storage,  public alertCtrl: AlertController) {
    this.move['restrict_package'] ="Restrict package";
    this.reset_form();
    this.input = 0;
    this.models =  ['stock.quant.package', 'stock.production.lot', 'stock.location', 'product.product']
    
  }

  reset_form(){
    this.state = 0;
    this.scan_id = '';
    this.last_scan = ''
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    this.restrict_package_id = 0;
    this.restrict_package_id_name = '';
    this.restrict_lot_id = 0;
    this.restrict_lot_id_name = '';
    this.product_qty = 0;
    this.total_package_qty = 0;
    this.package_qty = false;
    this.result_package_id = 0;
    this.result_package_id_name = '';
    this.location_id = 0;
    this.location_id_name = '';
    this.location_dest_id = 0;
    this.location_dest_id_name = '';
    this.product_id = 0;
    this.product_id_name = '';
    this.uom = '';
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad ManualPage');
  }
  submitScan(){
    if (this.state == 2 && this.last_scan == this.barcodeForm.value['scan']){
      this.process_move();
    }
    else {
      var values = {'model': this.models, 'search_str' : this.barcodeForm.value['scan'], 'return_object': true};
      this.barcodeForm.reset();
      this.submit(values);
    }
  }

  get_id(val){
    return (val && val[0]) || false
    
  }
  include(arr,obj) {
    return (arr.indexOf(obj) != -1);
  }
  presentAlert(titulo, texto) {
    const alert = this.alertCtrl.create({
        title: titulo,
        subTitle: texto,
        buttons: ['Ok']
    });
    alert.present();
  }
  check_state(state){
    var self = this;
    if (self.restrict_lot_id * self.product_qty * self.location_id * self.product_id != 0){self.state=1}
    else if (self.restrict_lot_id * self.location_id * self.product_id != 0){self.state=1}
    if (self.state==1 && self.location_dest_id!=0){self.state=2}

  }

  submit (values){
    var self = this
    var model = 'warehouse.app'
    var method = 'get_object_id'
    var origenModels = self.models
    var destModels = ['stock.quant.package', 'stock.location']
    if (self.state == 0){
      values['model']=origenModels
    }
    else {values['model']=destModels}
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
                  //AQUI DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO
                  //Estoy scaneando ORIGEN
                  if (value['id'] == 0){
                    self.presentToast(value['message'], false);
                    return value;
                }
                  else if (self.state==0) {
                    if (origenModels.indexOf(value.model)!=-1){                      
                      if (value.model == 'stock.quant.package'){self.set_package(self.state, value['fields'])}
                      else if (value.model == 'stock.location'){self.set_location(self.state, value['fields'])}
                      else if (value.model == 'stock.production.lot'){self.set_lot(self.state, value['fields'])}
                      else if (value.model == 'product.product'){self.set_lot(self.state, value['fields'])}
                      
                      } 
                    }
                  else if (self.state>=1) {
                    if (destModels.indexOf(value.model)!=-1){
                      self.last_scan = values['search_str']    
                      if (value.model == 'stock.quant.package'){self.set_package(self.state, value['fields'])}
                      else if (value.model == 'stock.location'){self.set_location(self.state, value['fields'])}
                      
                    } 
                  }
                  self.scan_id = value['id'];
                  self.check_state(self.state);
                  self.myScan.setFocus();
                  return value;
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
  
  set_state() {
    var self = this;
    //self.state = 1
  }

  set_package(state, values){
    var self = this;
    if (self.state==0){
      self.reset_form();
      self.restrict_lot_id = values['lot_id'];
      self.restrict_lot_id_name = values['lot_id_name'];
      self.restrict_package_id = values['id'];
      self.restrict_package_id_name = values['name'];
      self.product_qty = values['package_qty'];
      self.total_package_qty = values['package_qty'];
      self.package_qty = true;
      self.location_id = values['location_id'];
      self.location_id_name = values['location_id_name'];
      self.product_id = values['product_id'];
      self.product_id_name = values['product_id_name'];
      self.uom = values['uom'];
      self.result_package_id = values['id'];
      self.result_package_id_name = values['name'];
      }
    else if (self.state==1){
      if (!values['multi'] && values['lot_id'] && values['lot_id'] != self.restrict_lot_id){
        self.presentToast('Paquete no válido. Lote distinto al inicial', true);
        self.result_package_id = 0;
        self.location_dest_id = 0;
        self.result_package_id_name = '';
        self.location_dest_id_name = '';
        return;
      }
      self.result_package_id = values['id'];
      self.result_package_id_name = values['name'];}
  }

  no_result_package(reset=true){
    var self = this;
    if (reset){
      self.result_package_id = 0;
      self.result_package_id_name = '';
      }
    else {
      if (self.product_qty == self.total_package_qty){
        self.result_package_id = self.restrict_package_id;
        self.result_package_id_name = self.restrict_package_id_name;}
      else {
        self.result_package_id = -1;
        self.result_package_id_name = 'Nuevo';}
    }
  }

  set_lot(state, values){
    var self = this;
    self.reset_form();
    if (self.state==0){
      self.restrict_lot_id = values['id'];
      self.restrict_lot_id_name = values['name'];
      self.location_id = values['location_id'];
      self.location_id_name = values['location_id_name'];
      self.product_id = values['product_id'];
      self.product_id_name = values['product_id_name'];
      self.uom = values['uom'];}
  }

  set_location(state, values){
      var self = this;
    if (self.state==0){
      self.location_id = values['id'];
      self.location_id_name = values['name'];
    }

    else if (self.state==1){
      self.location_dest_id = values['id'];
      self.location_dest_id_name = values['name'];}
    }

  change_package_qty(){
    var self = this;
    if (self.package_qty){
      self.product_qty = self.total_package_qty;
      }
  }


  inputQty() {
    var self = this;
    if (self.state==0){return}
    let alert = this.alertCtrl.create({
      title: 'Qty',
      message: 'Cantidad a mover',
      inputs: [
        {
          name: 'qty',
          placeholder: self.product_qty.toString()
        },
      ],
      buttons: [
        {
          text: 'Cancel',
          handler: () => {
            console.log('Cancel clicked');
          }
        },
        {
          text: 'Save',
          handler: (data) => {
            console.log('Saved clicked');
            console.log(data.qty);
            if (self.restrict_package_id != 0 && data.qty>self.total_package_qty ){
              self.presentAlert('Error!', 'La cantidad debe ser menor que la contenida en el paquete');
            }
            else if (data.qty<0){
              self.presentAlert('Error!', 'La cantidad debe ser mayor que 0');
            }
            else if (data.qty) {
              self.product_qty = data.qty
              self.check_state(0);
            }
            self.input = 0;

          }
        }
      ]
    });

    self.input = alert._state;
    alert.present();
  }

  presentToast(message, showClose=false) {
    var self = this;
    let duration = 3000;
    let toastClass = 'toastOk';
    if (showClose){let toastClass = 'toastNo'};
    let toast = this.toastCtrl.create({
      message: message,
      duration: duration,
      position: 'top',
      showCloseButton: showClose,
      closeButtonText: 'Ok',
      cssClass: toastClass
    });
    toast.onDidDismiss(() => {
      self.myScan.setFocus();
    });
    toast.present();
  }


  process_move(){




    /* CREAR Y PROCESAR UN MOVIMEINTO */
    var self = this
    var values = {'restrict_package_id': self.restrict_package_id,
                  'product_id': self.product_id,
                  'restrict_lot_id': self.restrict_lot_id,
                  'location_id': self.location_id,
                  'result_package_id': self.result_package_id,
                  'location_dest_id': self.location_dest_id,
                  'package_qty': self.package_qty,
                  'product_uom_qty': self.product_qty}
    values ['origin'] = 'PDA move'
    var field = ''
    var fields = ['restrict_package_id', 'result_package_id', 'product_id', 'lot_id', 'result_package_id', 'location_id', 'location_dest_id']
    for (var key in fields){
      field = fields[key];
      if (self[field]!= 0) {values[field] = self[field]}}
    values['package_qty'] = self.package_qty;
    values['product_qty'] = self.product_qty;

    var model = 'stock.move'
    var method = 'pda_move'
    console.log(values)


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
                  if (value['id']!=0){
                    self.presentToast(value['message'], false);
                    self.reset_form();
                    return
                  }
                  else {
                    self.presentToast(value['message'], true);
                    return
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

}
