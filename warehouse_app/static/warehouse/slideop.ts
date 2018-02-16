import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { Slides } from 'ionic-angular';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
import { PROXY } from '../../providers/constants/constants';
/**
 * Generated class for the SlideopPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

import { HostListener } from '@angular/core';
import { HomePage } from '../home/home';
import { TreeopsPage } from '../treeops/treeops';
import { Storage } from '@ionic/storage';
import { AuxProvider } from '../../providers/aux/aux'

declare var OdooApi: any

@IonicPage()
@Component({
  selector: 'page-slideop',
  templateUrl: 'slideop.html',
})
export class SlideopPage {
  
  @ViewChild('slides') slides: Slides;
  @ViewChild('scan') myScan ;
  @ViewChild('qty') myQty ;

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) { 
    if (!this.myScan._isFocus && !this.myQty._isFocus){this.myScan.setFocus()};
     }
  op = {}
  op_id = 0
  model = 'stock.pack.operation'
  op_fields = ['id', 'pda_checked', 'picking_id', 'pda_done', 'product_id', 'location_id_name', 'location_id', 'location_dest_id_name', 'location_dest_id', 'product_uom_name', 'lot_id', 'package_id', 'result_package_id', 'result_package_id_name', 'package_id_name', 'lot_id_name', 'total_qty', 'qty_done', 'product_id_name']
  domain = []
  isPaquete: boolean = true;
  isProducto: boolean = false;
  cargar = true;
  scan = ''
  scan_id = {}
  credentialsForm: FormGroup;
  qtyForm: FormGroup;
  Home = HomePage
  package_id_change: number = 0
  package_dest_id_change: number = 0
  location_id_change: number = 0
  qty_change: boolean = false
  origin: boolean = false
  op_state = ['origin', 'qty', 'dest', 'confirm']
  ops = []
  index:number = 0
  pick_id = 0
  pick_name = ''
  message = ''

  constructor(public navCtrl: NavController, public toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, public alertCtrl: AlertController, private storage: Storage) {
    this.op = {};
    this.op_id = 0;
    this.message = '';  
    this.op_id = this.navParams.data.op_id;
    this.ops = this.navParams.data.ops;
    if (!this.ops){this.presentAlert('Aviso', 'No hay operaciones')}
    
    this.index = Number(this.navParams.data.index || this.get_op_index());
    this.domain = [['id', '=', this.op_id]];
    this.model =  'stock.pack.operation';
    this.scan = ''
    this.credentialsForm = this.formBuilder.group({scan: ['']});
    this.qtyForm = this.formBuilder.group({qty: ['']});
    this.scan_id = {}
    this.cargarOP();
    
    this.origin = this.navParams.data.origin || false
    this.package_dest_id_change = 0;
    this.package_id_change = 0;
    this.qty_change = false;
    this.location_id_change = 0;
    
    this.get_slide();
  } 

  get_slide(){

    if (this.origin)
      {setTimeout(() => {this.goToSlide(1);}, 150);}
    else {setTimeout(() => {this.goToSlide(0);}, 150);}
  }
  get_op_index(){
    var self = this;
    for (var index in self.ops){
      if (self.ops[index]['id'] == self.op_id) {return index}
    return 0
    }



  }
  goToSlide(index, del=0) {
    var self = this;

    self.slides.slideTo(index, del);
    self.slideChanged();
  }

  slideChanged() {
   this.myScan.setFocus()
  }

  cargarOP(){
    var self = this;
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
          self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          var con = val;
          var odoo = new OdooApi(PROXY, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.search_read(self.model, self.domain, self.op_fields, 0, 0).then(
                function (value) {
                  self.op = value[0];
                  self.pick_id = self.op['picking_id'][0]
                  self.pick_name = self.op['picking_id'][1]
                  self.cargar = false;
                  self.storage.set('stock.pack.operation', value);
                  self.storage.set('stock.picking', self.op['picking_id'])
                  self.myScan.setFocus();
                  if (!self.op['pda_checked']){self.change_op_value(self.op_id, 'pda_checked', true);}
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
  
  submitQty (){
    var self = this
    var values = {'model':  ['stock.qty'], 'qty' : this.qtyForm.value['qty']};
    self.submit(values);
  }
  submitScan(){
    var values = {'model':  ['stock.quant.package', 'stock.production.lot', 'stock.location'], 'search_str' : this.credentialsForm.value['scan']};
    this.credentialsForm.reset();
    this.submit(values);
  }

  get_id(val){
    return (val && val[0]) || false
    
  }

  submit (values){
    var self = this
    var model = 'warehouse.app'
    var method = 'get_object_id'
    var slide = self.slides.getActiveIndex();
    self.storage.get('CONEXION').then((val) => {
      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(PROXY, con.db);
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
                  
                  if (slide==0) {
                     // CASO 1. ORIGEN + PAQUETE = package_id => siguiente slide 
                     
                     if ((value.model == 'stock.production.lot' && value.id == lot_id ) || (value.model == 'stock.quant.package' && value.id == package_id)) {
                      self.package_id_change = 0;
                      self.origin = true;
                      self.goToSlide(1);
                    }
                    // CASO 2. ORIGEN + UBICACION y no package_id = suioguiente slide
                    else if (value.model == 'stock.location' && package_id == false && self.package_id_change == 0 && value.id == location_id){
                      self.origin = true;
                      self.goToSlide(1);
                    }
                    // CASO 3. ORIGEN + <> PAQUETE => CONFIRMAR PAQUETE
                    else if (value.model == 'stock.quant.package' && value.id != package_id && self.package_id_change == 0){
                      self.package_id_change = value.id;
                      self.myScan.setFocus();
                    }
                    // CASO 4. ORIGEN + ESPERANDO NUEVO PAQUETE E = NUEVO PAQUETE >> CAMBIO PAQUETE EN OP + CARGAR OP + CARGAR SLIDES
                    else if (value.model == 'stock.quant.package' && self.package_id_change == value.id){
                      self.package_id_change = 0;
                      self.change_op_value(self.op_id, 'package_id', value.id);
                      
                    }
                    else if (value.model == 'stock.quant.package' && self.package_id_change != 0 && self.package_id_change != value.id){
                      self.package_id_change = 0;
                      self.presentToast('Cancelado cambio de paquete')
                    }
                    // CASO 4.1. ORIGEN + LOCAT DEST ID
                    else if (value.model == 'stock.location' && self.origin && self.package_id_change == 0 && value.id == location_dest_id){
                      self.doOp (self.op['id']);
                      
                    }
                    
                  }    
                  else if (slide==1 && self.origin) {
                    // CASO 5. CANTIDAD + PAQUETE DESTINO => CONFIRMA OPERACION
                    if (value.model == 'stock.quant.package' && self.package_dest_id_change == 0 && value.id == result_package_id) {
                      self.doOp (self.op['id']);
                    }
                    // CASO 6. CANTIDAD + UBICACION DESTINO => CONFIRMA OPERACION
                    else if (value.model == 'stock.location' && self.package_dest_id_change == 0 && value.id == location_dest_id) {
                      self.doOp (self.op['id']);

                    }
                    // CASO 7. CANTIDAD + NUMERO => CAMBIA CANTIDAD EN OPERACION
                    else if (value.model == 'stock.qty') {
                      self.change_op_value(self.op_id, 'qty_done', values.qty);

                    }
                    else if (value.model == 'stock.location' && self.origin && value.id == location_dest_id){
                      self.doOp (self.op['id']);

                    }
                  }
                  // CASO 8. DESTINO + PAQUETE DESTINO (=)  => CONFIRMA OPERACION
                  else if (slide==2 && self.origin){
                    // CASO 9. DESTINO + PAQUETE DESTINO (<>)  => CONFIRMA PAQUETE DESTINO >> CAMBIO PAQUETE EN OP + CARGAR OP + CARGAR SLIDES
                    if (value.model == 'stock.quant.package' && value.id == result_package_id && self.package_dest_id_change == 0) {
                      self.doOp (self.op['id']);

                    }
                    // CASO 10. DESTINO + UBICACION DESTINO (=) => CONFIRMA OPERACION
                    else if (value.model == 'stock.location' && value.id == location_dest_id && self.package_dest_id_change == 0) {
                      self.doOp (self.op['id']);
                    }
                    // CASO 11. DESTINO + UBICACION DESTINO (<>) => CONFIRMA NUEVO UBICACION DESTINO >> CAMBIO DESTINO EN OP + CARGAR OP + CARGAR SLIDES
                    else if (value.model == 'stock.location' && value.id != location_dest_id && self.location_id_change == 0) {
                      self.location_id_change = value.id;
                      self.myScan.setFocus();
                    }

                    else if (value.model == 'stock.location' && value.id == self.location_id_change) {
                      self.location_id_change = 0 
                      self.change_op_value(self.op_id, 'location_dest_id', value.id);
                    }
                    else if (value.model == 'stock.location' && value.id == self.location_id_change && self.location_id_change != 0) {
                      self.location_id_change = 0 
                      self.presentToast('Cancelado cambio de destino')
                    }
                    // CASO 12. DESTINO + CAMBIO RESULT_PACKAGE_ID
                    else if (value.model == 'stock.quant.package' && value.id != result_package_id && self.package_dest_id_change== 0){
                      self.package_dest_id_change = value.id;
                      self.myScan.setFocus();
                    }
                    // CASO 13. CONFIRMAR CASO 12
                    else if (value.model == 'stock.quant.package' && self.package_dest_id_change == value.id){
                      self.package_dest_id_change = 0;
                      self.change_op_value(self.op_id, 'result_package_id', value.id);
                    }       
                    
                    else if (value.model == 'stock.quant.package' && self.package_dest_id_change != 0 && self.package_id_change != value.id){
                      self.package_dest_id_change = 0;
                      self.presentToast('Cancelado cambio de paquete')
                    } 

                  }
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
          var odoo = new OdooApi(PROXY, con.db);
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



    change_op_value(id, field, value){
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
            var odoo = new OdooApi(PROXY, con.db);
            odoo.login(con.username, con.password).then(
              function (uid) {
                odoo.call(model, method, values).then(
                  function (value) {
                    if (field=='pda_checked'){return;}
                    if (value['new_op']){
                      let showClose = !value['result'];
                      self.presentToast(value['message'], showClose);
                      self.navCtrl.push(TreeopsPage, {picking_id: self.pick_id, move_to_op: value['new_op']});
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
            var odoo = new OdooApi(PROXY, con.db);
            odoo.login(con.username, con.password).then(
              function (uid) {
                odoo.call(model, method, values).then(
                  function (value) {
                    {setTimeout(() => {
                      self.ops[self.index]['pda_done'] = true
                      self.cargar = false;
                      self.origin = false;
                      self.domain = self.get_next_op(id, self.index);
                      if (self.domain.length == 0){
                        self.navCtrl.push(TreeopsPage, {picking_id: self.pick_id});
                        }
                      else{
                        self.get_slide();
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
}