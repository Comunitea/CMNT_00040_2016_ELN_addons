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

  
  
  
  model = 'stock.move'
  move = {}
  domain = []
  package_qty: boolean = true;
  message = ''
  state: number = 0; /* 0 origen 1 destino 2 validar */
  scan_id: string = ''
  
  models = []
  last_scan = ''
  input: number = 0;
  barcodeForm: FormGroup;
  tracking = 'none'

  constructor(public navCtrl: NavController, public toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, public storage: Storage,  public alertCtrl: AlertController) {

    this.input = 0;
    this.models =  ['stock.quant.package', 'stock.production.lot', 'stock.location', 'product.product']
    this.reset_form();
    this.tracking = 'lot';
  }

  reset_form(){
    
    this.state = 0;
    this.scan_id = '';
    this.last_scan = ''
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    this.move = {};
    this['move']['product_qty'] =0;
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

  check_state(state=0){
    if (!Boolean(this.move)){
      state==0; 
      return
    }
    if (this.tracking == 'none') {
      if (Boolean(this.move['location_id']) && Boolean(this.move['product_id'])){
        this.state=1
      }
    }
    else if (this.tracking == 'serial') {
      if (Boolean(this.move['location_id']) && Boolean(this.move['restrict_lot_id'])){
        this.state=1
      }
    }
    else {
      if (Boolean(this.move['product_id']) && Boolean(this.move['location_id']) && Boolean(this.move['restrict_lot_id'])){
        this.state=1
      }
    }
    
    if (this.state==2 && !this['move']['location_dest_id']['need_check']){
      this.process_move()
    }
    if (this.state==1 && Boolean(this.move['location_dest_id']) && Boolean(this.move['product_qty'])){
      this.state=2
    }
    
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
                function (res) {
                  //AQUI DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO
                  //Estoy scaneando ORIGEN
                  if (res['id'] == 0){
                    self.presentToast(res['message'], false);
                    return false;
                }
                  else if (self.state==0) {
                    if (origenModels.indexOf(res.model)!=-1){                      
                      if (res.model == 'stock.quant.package'){self.set_package(res['values'])}
                      else if (res.model == 'stock.location'){self.set_location(res['values'])}
                      else if (res.model == 'stock.production.lot'){self.set_lot(res['values'])}
                      else if (res.model == 'product.product'){self.set_product(res['values'])}
                      
                      } 
                    }
                  else if (self.state>=1) {
                    if (destModels.indexOf(res.model)!=-1){
                      self.last_scan = values['search_str']    
                      if (res.model == 'stock.quant.package'){self.set_package(res['values'])}
                      else if (res.model == 'stock.location'){self.set_location(res['values'])}
                      
                    } 
                  }
                  self.scan_id = res['id'];
                  self.check_state();
                  self.myScan.setFocus();
                  return true;
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

  set_package(values){

    let obj = {'id': values['id'], 'name': values['name'], 'location_id': values['location_id'], 'multi': values['multi'], 'product_id': values['product_id'], 'package_qty': values['package_qty']}

    //ORIGEN IMPLICA RESET DEL MOVIMIENTO
    if (this.state==0){
      
      this.reset_form();
      this['move']['restrict_package_id'] = obj;
      this['move']['result_package_id'] = obj;
      this['move']['location_id'] = values['location_id'];
      this['move']['package_qty']= values['package_qty']
      this.package_qty = true;
      if (Boolean(obj.multi)){
        this['move']['total_package_qty'] = 1;
        this['move']['product_qty'] = 1;  
        this['move']['result_package_id'] = obj;
        this.tracking = 'none';
      }
      this['move']['total_package_qty'] = values['package_qty'];
      this['move']['product_qty'] = values['package_qty'];
      this['move']['restrict_lot_id'] = values['lot_id'];
      this['move']['product_id'] = values['product_id'];
      this['move']['uom_id'] = values['uom'];
      this.tracking = values['product_id']['tracking']
      }
    //DESTINO  
    else if (this.state==1) {
      if (this['move']['restrict_package_id']['multi']) {
        this.presentAlert("Error de paquete", "Es un paquete multi")
      }
      else if (Boolean(this['move']['restrict_lot_id']) && values['lot_id']['id'] != this['move']['restrict_lot_id']['id']){
        this.presentToast('Paquete no válido. Lote distinto al inicial', true);
        this['move']['result_package_id'] = {};
        this['move']['location_dest_id'] = {};
        return;
      }
      else {
        this['move']['result_package_id'] = obj;
        this['move']['location_dest_id'] = values['location_id']
      }
    }
      
  }

  no_result_package(reset=true){
    if (reset){
      this['move']['result_package_id'] = {};
      }
    else {
      if (this['move']['product_qty'] == this['move']['total_package_qty']){
        this['move']['result_package_id'] = this['move']['restrict_package_id'];
        }
      else {
        this['move']['result_package_id'] = {'id': -1, name: 'Nuevo', 'location_id': {}};
      }    
    }
  }
  set_lot(values){
    if (this.state != 0){
      this.presentAlert('Lote erróneo', 'Debes reiniciar para cambiar el lote');
      return;
    }
    let location_id
    let obj = {'id': values['id'], 'name': values['display_name'], 'product_id': values['product_id'], 'location_id': values['location_id'], 'qty_available': values['qty_available']}
    console.log (values)
    
    if (values['product_id']['tracking'] =='serial'){
      location_id = this['move']['location_id']
      this.reset_form();
    }
    
      
    this['move']['restrict_lot_id'] = obj;
    
    if (Boolean(values['location_id'])){
      this['move']['location_id'] = location_id;
      }
    
    this['move']['product_qty'] = values['qty_available'];
    this['move']['product_id'] = values['product_id'];
    this['move']['uom_id'] = values['uom_id'];
    this.tracking = values['product_id']['tracking'];
  }

  set_location(values){
    let obj = {'id': values['id'], 'name': values['name']}
    if (this.state==0){
      
      if (Boolean(this['move']['restrict_package_id']) && this['move']['location_id']!= obj) {
        this.presentAlert ('Error de paquete', 'La ubicación de origen debe ser la misma que la del paquete');
        return
      }
      if (Boolean(this['move']['restrict_lot_id']) && Boolean(this['move']['restrict_lot_id']['location_id']) && this['move']['location_id']!= obj) {
        this.presentAlert ('Error de lote', 'La ubicación de origen debe ser la misma que la del lote');
        return
      }
      this['move']['location_id'] = obj;
 
    }
    else if (this.state==1){
      if (!Boolean(this['move']['restrict_package_id']) && Boolean(this['move']['result_package_id']) && this['move']['result_package_id']['id']!=-1 && Boolean(this['move']['result_package_id']['location_id']) && this['move']['location_id']['id']!= obj['id']) {
        this.presentAlert ('Error de paquete', 'Si quieres empaquetar, la ubicación de destino debe ser la misma que la del paquete de destino');
        return
      }
      if (Boolean(this['move']['restrict_package_id']) && Boolean(this['move']['result_package_id']) && this['move']['result_package_id']['id']!=-1 && Boolean(this['move']['result_package_id']['location_id']) && this['move']['location_id']['id'] == obj['id']) {
        this.presentAlert ('Error de destino', 'Si quieres mover de un paquete, la ubicación de destino debe ser distinta del origen');
        return
      }
      this['move']['location_dest_id'] = obj;
    }
  }

  set_product(values){
    let obj = {'id': values['id'], 'name': values['display_name'], 'tracking': values['tracking'], 'qty_available': values['qty_available'] }

    if (this.state==0){
      if (Boolean(this['move']['restrict_package_id'])  && this['move']['restrict_package_id']['product_id'] && this['move']['restrict_package_id']['product_id']['id'] != obj['id']) {
        this.presentAlert ('Error de producto', 'El paquete seleccionado tiene producto');
        return
      }
      if (Boolean(this['move']['restrict_lot_id']) && this['move']['restrict_lot_id']['product_id'] && this['move']['restrict_lot_id']['product_id']['id'] != obj['id']) {
        this.presentAlert ('Error de producto', 'El lote seleccionado tiene producto');
        return
      }
      this['move']['product_id'] = obj;
      this.tracking = obj['tracking']
     }
  }  

  change_package_qty(){
    if (this['move']['package_qty']){
      this['move']['product_qty'] = this['move']['total_package_qty'];
      }
  }

  inputQty() {
    if (this.state==0){return}
    let alert = this.alertCtrl.create({
      title: 'Qty',
      message: 'Cantidad a mover',
      inputs: [
        {
          name: 'qty',
          placeholder: this['move']['product_qty'].toString()
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
            if (data.qty<0){
              this.presentAlert('Error!', 'La cantidad debe ser mayor que 0');
            }
            else if (Boolean(this['move']['restrict_package_id']) && data.qty > this['move']['restrict_package_id']['package_qty']){
              this.presentAlert('Error!', 'La cantidad debe ser menor que la contenida en el paquete');
            }
            else if (Boolean(this['move']['restrict_lot_id']) && data.qty > this['move']['restrict_lot_id']['qty_available']){
              this.presentAlert('Error!', 'La cantidad debe ser menor que la disponible para ese lote');
            }
            
            this['move']['product_qty'] = data.qty
            this.check_state(0);
            this.input = 0;

          }
        }
      ]
    });

    this.input = alert._state;
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
  get_move_values (move){
    var values = {'restrict_package_id': move['restrict_package_id'] && move['restrict_package_id']['id'],
                  'product_id': move['product_id']['id'],
                  'product_qty': move['product_qty'],
                  'restrict_lot_id': move['restrict_lot_id'] && move['restrict_lot_id']['id'],
                  'location_id': move['location_id']['id'],
                  'result_package_id': move['result_package_id'] && move['result_package_id']['id'],
                  'location_dest_id': move['location_dest_id']['id'],
                  'package_qty': move['package_qty'],
                  'product_uom_qty': move['product_qty'],
                  'origin': 'PDA move'}
    return values
  }

  process_move(){
    /* CREAR Y PROCESAR UN MOVIMEINTO */
    var self = this
    var values = self.get_move_values(self['move'])
    
    
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
