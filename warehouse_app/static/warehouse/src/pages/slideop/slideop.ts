import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { Slides } from 'ionic-angular';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/
/**
 * Generated class for the SlideopPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

import { HostListener } from '@angular/core';
import { HomePage } from '../home/home';
import { TreeopsPage } from '../treeops/treeops';
import { TreepickPage } from '../treepick/treepick';
import { Storage } from '@ionic/storage';
import { AuxProvider } from '../../providers/aux/aux'

declare var OdooApi: any

@IonicPage()
@Component({
  selector: 'page-slideop',
  templateUrl: 'slideop.html',
})
export class SlideopPage {


  @ViewChild('scan') myScan ;
  @ViewChild('qty') myQty ;

  //@HostListener('document:keydown', ['$event'])
  //handleKeyboardEvent(event: KeyboardEvent) { 
  //  if (!this.myScan._isFocus){this.myScan.setFocus()};
  //   }
  
  op = {}
  op_selected = {};
  model = 'stock.pack.operation'
  op_fields = ['id', 'pda_checked', 'picking_id', 'pda_done', 'product_id', 'pda_product_id', 'location_id', 'location_id_barcode', 'location_dest_id_barcode', 'location_dest_id', 'product_uom', 'lot_id', 'package_id', 'result_package_id', 'product_qty', 'total_qty', 'qty_done']
  pick_fields = ['id', 'state','user_id']
  domain = []
  isPaquete: boolean = true;
  isProducto: boolean = false;
  cargar = true;
  scan = ''
  scan_id = {}
  barcodeForm: FormGroup;
  Home = HomePage

  package_id_change: number = 0;
  package_dest_id_change: number = 0;
  location_id_change: number = 0;
  lot_id_change: number = 0;
  qty_change: boolean = false
  result_package_id: number;
  ops = []
  index:number = 0
  message = ''
  new_qty_done = 0
  state: number = 0/* 0 espera origen, 1 cantidad yo destino 2 destino*/
  input: number = 0
  op_id: number = 0
  last_read: number = 0
  reconfirm: boolean 
  waiting: number = 0
  pick = []

  constructor(public navCtrl: NavController, public toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, public alertCtrl: AlertController, private storage: Storage) {
    
    this.op_id = this.navParams.data.op_id;
    this.pick = []
    this.reconfirm = false
    this.ops = this.navParams.data.ops;
    if (!this.ops){
      this.presentToast('Aviso:No hay operaciones', false)
      }
    this.index = Number(this.navParams.data.index || 0);
    this.result_package_id = 0
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    this.state = this.navParams.data.origin || 0;
    this.resetForm()

    }
  
  resetValues(){
    this.waiting=0;
    this.package_dest_id_change = 0;
    this.package_id_change = 0;
    this.lot_id_change = 0;
    this.qty_change = false;
    this.location_id_change = 0;
    this.message = '';
    this.op = {};
    this.domain = [['id', '=', this.op_id]];
    this.model =  'stock.pack.operation';
    this.scan = ''
    this.state = 0;
    this.new_qty_done = 0;
    this.last_read = 0;
    this.op_selected = {'lot_id': 0, 'package_id': 0, 'location_id': 0, 'product_id': 0, 'location_dest_id': 0, 'result_package_id': 0}
    
    this.input = 0;
  }  
  
  no_result_package(reset=true){
    var self = this;
    if (reset){self.op_selected['result_package_id'] = self.op_selected['result_package_id']}
    else {self.op_selected['result_package_id'] = [-1, 'Nuevo'];}
  }
  resetForm(){
    this.resetValues();
    this.cargarOP();
   

  }
  get_op_selected(){
    var field
    for (field in ['id', 'package_id', 'lot_id', 'product_id', 'qty_done', 'product_qty', 'result_package_id', 'location_dest_id', 'pda_product_id']){
    }
  }
  goHome(){this.navCtrl.setRoot(TreepickPage, {borrar: true, login: null});}

  cargarPick(){
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
          this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } 
      else {
        var self = this
        var con = val;
        var odoo = new OdooApi(con.url, con.db);
        odoo.login(con.username, con.password).then(
          function (uid) {
          var model = 'stock.picking';
          var fields = self.pick_fields;
          var domain = [['id','=', self.op['picking_id'][0]]];
          odoo.search_read(model, domain, fields, 0, 1).then((value) => {
            self.pick = value[0];}
            ); 
          },
          function () {
            self.cargar = false;
            self.presentAlert('Falla!', 'Imposible conectarse');
          });
      }});
    }

  cargarOP(){
    var self = this;
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
          self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.search_read(self.model, self.domain, self.op_fields, 0, 0).then(
                function (value) {
                  self.op = value[0];
                  if (self.op['picking_id']){self.cargarPick()}
                  self.cargar = false;
                  if (self.op['result_package_id'])
                    { self.result_package_id = 0;
                      self.op_selected['result_package_id'] = self.op['result_package_id'];}
                  if (!self.op['pda_checked'])
                    {self.change_op_value(self.op_id, 'pda_checked', true);}
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
          
  presentAlert(titulo, texto) {
    const alert = this.alertCtrl.create({
        title: titulo,
        subTitle: texto,
        buttons: ['Ok']
    });
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


  change_op_value(id, field, value){
    if (this.check_changes()){return}
    var self = this;
    var model = 'stock.pack.operation';
    var method = 'change_op_value';
    var values = {'id': id, 'field': field, 'value': value};
    var object_id = {};
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
                  if (field=='pda_checked'){return;}
                  if (value['new_op']){
                    let showClose = !value['result'];
                    self.presentToast(value['message'], showClose);
                    self.navCtrl.push(TreeopsPage, {picking_id: self.op['picking_id'][0], move_to_op: value['new_op']});
                    return
                  } 
                  let showClose = !value['result'];
                  self.presentToast(value['message'], showClose);
                  self.cargar = false;
                  self.cargarOP();
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

submitScan(){
  if (this.check_changes()){return}
  var values = {'model':  ['stock.quant.package', 'stock.production.lot', 'stock.location'], 'search_str' : this.barcodeForm.value['scan']};
  this.barcodeForm.reset();
  this.submit(values);
  }

check_changes(){
  var res = false;
  if (this.op['pda_done']){
    this.presentToast ("Ya está hecha. No puedes modificar");
    res = true
    }
  if (!Boolean(this.pick['user_id'])) {
    this.presentToast ("No está asignado el picking");
    res = true
    }
  return res
}
scanValue(model, scan){
    if (this.check_changes()){return}
    var domain
    var values
    if (model=='stock.production.lot'){
      domain = [['product_id', '=', this.op['product_id'][0]]];
      values = {'model':  [model], 'search_str' : scan, 'domain': domain};
    }
    else {
      values = {'model':  [model], 'search_str' : scan}
    }
    this.submit(values);
}
  get_id(val){
    return (val && val[0]) || false
    
  }
check_state(){
  var self = this;
  self.state = 0;
  /* state == 0 si es la operacion tiene pacquete y se selecciona paquete // si no lo tiene y tienen lote se selecciona lote y ubicación o si no tiene lote producto más ubicación*/
  if (self.op['package_id']){
      if (self.op_selected['package_id'] != 0){
        self.state = 1
      }
  }
  else if (self.op['lot_id']){
    if (self.op_selected['lot_id'] != 0 && self.op_selected['location_id'] != 0){
      self.state = 1
    }
  else if (self.op_selected['product_id'] != 0 && self.op_selected['location_id'] != 0){
      self.state = 1
    }
  }
  /* si state ==1 y hay paquete de destino o ubicacion de destino se puede confirmar*/
  
  if (self.state == 1 && (self.last_read !=0 || self.op_selected['result_package_id'] != 0 || self.op_selected['location_dest_id'] != 0)) {
    self.state = 2;
    }

  /*WAITING*/
  if (self.op['package_id']){
    if (self.op_selected['package_id']==0){
      self.waiting = 1
    }
    else {self.waiting = 4}
  }  
  if (!self.op['package_id']){
    if (self.op_selected['lot_id']==0){
      self.waiting = 2
    }
    else if (self.op_selected['lot_id']>0){
      if (self.op_selected['location_id']==0){
        self.waiting = 3
      }
      else {
        self.waiting = 4
      }
    }
  }
  if (self.waiting == 4 && ((self.op['result_package_id'] && self.op_selected['result_package_id'] > 0) || (self.op_selected ['result_package_id']>0))){self.waiting = 6}
  if (self.waiting==4 && (!self.op['result_package_id'] && self.op_selected['location_dest_id']==0)){self.waiting = 5}
  
  if (self.op_selected['result_package_id'] > 1 || self.op_selected['location_dest_id']){self.waiting = 6}
  
  if (self.waiting < 4){self.state=0}
  else if (self.waiting < 6){self.state=1}
  else if (self.last_read !=0) {self.state=2}
  
}


submit (values){
  if (this.check_changes()){return}
  var self = this
  var model = 'warehouse.app'
  var method = 'get_object_id'
  var confirm = false
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
                var lot_id = self.get_id(self.op['lot_id'])
                var package_id = self.get_id(self.op['package_id'])
                var result_package_id = self.get_id(self.op['result_package_id'])
                var location_id = self.get_id(self.op['location_id'])
                var location_dest_id = self.get_id(self.op['location_dest_id'])
                //AQUI DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO
                confirm = self.reconfirm || (self.last_read==value.id)
                self.last_read = value.id
                if (self.state==0) {
                    // CASO 0.LOTE. LOTE SELECCIONADO
                  if (value.model == 'stock.production.lot' && self.lot_id_change == 0 && value.id == lot_id){
                      self.op_selected['lot_id'] = value.id;
                      
                  }
                  // CASO 0.LOTE.. CAMBIO LOTE
                  else if (value.model == 'stock.production.lot' && self.lot_id_change == 0 && value.id != lot_id ){
                    self.lot_id_change == value.id;
                    self.presentToast('Cambiando lote. Repite scan para confirmar');
                  }
                  // CASO 0.LOTE.. CAMBIO LOTE ONFIRMADO/CANCELADO
                  else if (value.model == 'stock.production.lot' && self.lot_id_change != 0){
                    if (value.id != self.lot_id_change) {
                      self.op_selected['lot_id'] = value.id;
                      self.presentToast('Lote cambiado');
                      self.lot_id_change = 0;
                    }
                    else {
                      self.lot_id_change = 0;
                      self.presentToast('Cancelado el cambio de lote')}
                  }


                  //CASO 0. PAQUETE. CONFIRMADO
                  else if (value.model == 'stock.quant.package' && value.id == package_id) {
                    self.package_id_change = 0;
                    self.op_selected['lot_id'] = self.op['lot_id']
                    self.op_selected['package_id'] = value.id;  
                    self.op_selected['location_id'] = self.op['location_id']                    
                  }
                  //CASO 0. PAQUETE. CAMBIO
                  else if (value.model == 'stock.quant.package' && self.package_id_change == 0 && value.id != package_id) {
                    self.package_id_change = value.id;
                    self.op_selected['lot_id'] = 0;
                    self.op_selected['package_id'] = 0;                      
                  }
                  //CASO 0. PAQUETE. CAMBIO CONFIRMADO
                  else if (value.model == 'stock.quant.package' && self.package_id_change == value.id) {
                    self.package_id_change = value.id;
                    self.change_op_value(self.op_id, 'package_id', value.id);
                    // Reiniciamos la configuración completa  ...
                  }
                  //CASO 0. PAQUETE. CAMBIO CANCELADO/NUEVO CAMBIO
                  else if (value.model == 'stock.quant.package' && self.package_id_change != 0 && self.package_id_change != value.id){
                    if (value.id==self.op['package_id']){
                      self.package_id_change = 0;
                      self.op_selected['lot_id'] = self.op['lot_id']
                      self.op_selected['location_id'] = self.op['location_id']
                      self.presentToast('Cancelado cambio de paquete')
                    }
                    else {
                      self.package_id_change = value.id;
                      self.presentToast('Nuevo cambio de paquete.  Repite scan para confirmar')
                    }

                  }
                    
                  // SI HAY PAQUETE SE IGNORA
                  // CASO 0. UBICACION. CONFIRMADA

                  else if (value.model == 'stock.location' && value.id == location_id && self.location_id_change == 0){
                    self.op_selected ['location_id'] = value.id;
                  }

                  // CASO 3. CAMIO DE UBICACION
                  else if (value.model == 'stock.location' && package_id == false && self.location_id_change == 0 && value.id != location_id) {
                    self.location_id_change = value.id;
                    self.presentToast('Cambio de ubicación de origen. Repite scan para confirmar')

                  }

                  else if (value.model == 'stock.location' && self.location_id_change != 0){
                    if (self.location_id_change == value.id) {
                    self.presentToast('Cambio de ubicación de origen confirmado');
                    self.change_op_value(self.op_id, 'location_id', value.id);
                    self.location_id_change = 0;}
                    else {
                      self.presentToast('Cambio de ubicación de origen cancelado');
                      self.location_id_change = 0;
                    }
                    
                  }
                // STATE = 1
                }
                

                // YA HAY ORIGEN  
                else if (self.state!=0) {
                  // CASO 5. CANTIDAD + PAQUETE DESTINO => CONFIRMA OPERACION
                  if (value.model == 'stock.location'){
                    if (value.id == location_dest_id && self.location_id_change == 0){
                      if (confirm) {
                        self.doOp(self.op['id']);
                      }  
                      else {
                        self.presentToast('ReScan para confirmar')
                      }
                    }

                    else if (value.id != location_dest_id && self.location_id_change == 0) {
                      self.location_id_change = value.id;
                      self.presentToast('Cambiando de ubiucación')
                    }
                    else if (value.id == self.location_id_change) {
                      self.change_op_value(self.op_id, 'location_dest_id', value.id);
                      self.location_id_change = 0 
                      self.presentToast('Cambio de ubicación de destino confirmado')
                    }

                    else if (value.id == self.location_id_change && self.location_id_change != 0) {
                      self.location_id_change = 0 
                      self.presentToast('Cancelado cambio de destino')
                    }
                    
                  }
                  else if (value.model == 'stock.quant.package'){
                    if (value.id == result_package_id && self.package_dest_id_change == 0){
                      if (confirm) {
                        self.doOp(self.op['id']);
                      }  
                      else {
                        self.presentToast('ReScan para confirmar')
                      }
                    }

                    else if (value.id != result_package_id && self.package_dest_id_change== 0){
                      self.package_dest_id_change = value.id;
                      self.presentToast('Cambiando de paquete de destino')
                    }
                  // CASO 13. CONFIRMAR CASO 12
                    else if (self.package_dest_id_change == value.id){
                      self.package_dest_id_change = 0;
                      self.change_op_value(self.op_id, 'result_package_id', value.id);
                      self.presentToast('Confirmado cambio de paquete de destino')
                    }       
                  
                    else if (self.package_dest_id_change != 0 && self.package_id_change != value.id){
                      self.package_dest_id_change = 0;
                      self.presentToast('Cambio de paquete de destino cancelado')
                    }
                  }

                  
                  
                  // CASO 11. DESTINO + UBICACION DESTINO (<>) => CONFIRMA NUEVO UBICACION DESTINO >> CAMBIO DESTINO EN OP + CARGAR OP + CARGAR SLIDES
                  

            


                }
                self.check_state();
                self.scan_id = value;
                self.myScan.setFocus();
                return value;
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


  getObjectId(values){
    var self = this;
    var model = 'warehouse.app'
    var method = 'get_object_id'
    
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
                  self.scan_id = value; 
                  return value;
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
 
    get_next_op(id, index){
      var self = this;
      let domain = []
      
      var ops = self.ops.filter(function (op) {
        return op.pda_done == false && op.id != id}
      )

      if (ops.length==0) {return []}
      index = index + 1;
      if (index > (self.ops.length-1)) {index = 0;};
      if (self.ops[index].pda_done) {return self.get_next_op(id, index)}
      return [['id', '=', self.ops[index]['id']]];
      
    }

    doOp(id){
      if (this.check_changes()){return}
      var self = this;
      var model = 'stock.pack.operation'
      var method = 'doOp'
      var values = {'id': id}
      var object_id;
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
                    {setTimeout(() => {
                      self.ops[self.index]['pda_done'] = true
                      self.cargar = false;
                      self.domain = self.get_next_op(id, self.index);
                      if (self.domain.length == 0){
                        self.navCtrl.push(TreeopsPage, {picking_id: self.op['picking_id'][0]});
                        }
                      else{
                        self.cargarOP();             
                        }                  
                    }, 150);}

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
  

  inputQty() {
    if (this.check_changes()){return}
    var self = this;
    if (self.state == 0) {return}
    let alert = this.alertCtrl.create({
      title: 'Qty',
      message: 'Cantidad a mover',
      inputs: [
        {
          name: 'qty',
          placeholder: self.op['total_qty'].toString()
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
              self.presentAlert('Error!', 'La cantidad debe ser mayor que 0');
            }
            else if (data.qty) {
              self.op['qty_done'] = data.qty
              self.check_state();
            }
            self.input = 0;

          }
        }
      ]
    });

    self.input = alert._state;
    alert.present();
  }
        
    
}