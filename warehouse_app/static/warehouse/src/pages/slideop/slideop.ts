import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController } from 'ionic-angular';
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
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector'

//Modal

import { SelectLotPage } from '../select-lot/select-lot'
import { SelectPackagePage } from '../select-package/select-package';

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
    
  model = 'stock.pack.operation'
  isPaquete: boolean = true;
  cargar = true;
  scan = ''
  scan_id = {}
  last_read: number = 0
  last_scan: ''
  reconfirm: boolean 
  WAITING: ['package_id', 'location_dest_id', 'product_id', 'lot_id', 'location_id', 'location_dest_id']
  waiting: number

  barcodeForm: FormGroup;
  Home = HomePage
  
  package_change: number = 0;
  location_change: number = 0;
  lot_id_change: number = 0;
  
  index:number = 0
  message = ''
  
  op_id: number = 0
  op = {}
  pick = []
  ops = []
  input: number = 0
  last_id: number = 0
  op_ready: boolean = false
  auto: boolean = false
  uom_to_uos: number = 1
  advance: boolean = false

  constructor(public navCtrl: NavController,  private modalCtrl: ModalController, private toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, private alertCtrl: AlertController, private aux: AuxProvider , private odoo: OdooProvider, private storage: Storage) {
    this.cargar = true
    this.advance= false
    this.op_id = this.navParams.data.op_id;
    this.op_ready = false
    this.last_id = 0
    this.ops = this.navParams.data.ops;
    this.pick = this.navParams.data.pick;
    this.reconfirm = false
    if (!this.ops){
      this.presentToast('Aviso:No hay operaciones', false)
      }
    this.index = Number(this.navParams.data.index || 0);
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    this.waiting = this.navParams.data.origin || 0;
    this.resetValues()
    this.cargarOp(this.op_id)
    }
  

  move_index(cont1){
    this.cargar=true
    this.index += cont1
    if (this.index<0){this.index=this.ops.length-1}
    if (this.index==this.ops.length){this.index=0}
    this.op_id = this.ops[this.index]['id']
    this.resetValues()
    this.cargarOp(this.op_id)

  }
  resetForm(){
    this.cargar=true
    let orig_id = this.op_id
    this.resetOPValues()    
    this.cargarOp(orig_id)
  }

  reverse_ops(){
    this.cargar=true
    this.resetValues()
    this.ops = this.ops.reverse()
    this.op_id = this.ops[0]['id']
    this.cargarOp(this.op_id)
  }
 
  resetOPValues(){ 
    this.waiting=0;
    this.package_change = 0;
    this.lot_id_change = 0;
    this.location_change = 0;
    this.scan = ''
    this.last_read = 0;
    this.input = 0;
  }
  
  resetValues(){
   
    this.message = '';
    this.op = {};
    this.model =  'stock.pack.operation';
    this.resetOPValues()
  }  
  
  no_result_package(reset=true){
    var self = this;
    if (reset){
      self.op['result_package_id_selected'] = self.op['result_package_id']
    }
    else {
      self.op['result_package_id_selected'] = [-1, 'Nuevo'];
    }
  }
 
  goHome(){this.navCtrl.setRoot(TreepickPage, {borrar: true, login: null});}


  
  check_needs(){
    let reset = false
    if (this.op['pda_done']){reset = true}
    if (this.op['package_id']) {this.op['package_id']['checked'] = reset}
    if (this.op['result_package_id']) {this.op['result_package_id']['checked'] = reset}
    if (this.op['lot_id']) {this.op['lot_id']['checked']  = reset}
    this.op['location_id']['checked'] = !this.op['location_id']['need_check'] || reset
    this.op['location_dest_id']['checked'] = !this.op['location_dest_id']['need_check'] || reset
  }

  get_op_ready () {
    
    this.op_ready = (!this.op['package_id'] || (this.op['package_id'] && this.op['package_id']['checked'])) && (!this.op['result_package_id'] || (this.op['result_package_id'] && this.op['result_package_id']['checked'])) && (!this.op['lot_id'] || (this.op['lot_id'] && this.op['lot_id']['checked'])) && this.op['location_id']['checked'] && this.op['location_dest_id']['checked'] && (this.op['qty_done']>0)
    if (this.op_ready && this.op['need_confirm']){
      this.doOp(this.op_id, true)
    }
    
  }
  convert_uom_to_uos(qty){
    return (qty/this.uom_to_uos).toFixed(2)
  }
  convert_uos_to_uom(qty){
    return (qty*this.uom_to_uos).toFixed(2)
  }
  cargarOp(id=0){ 
    if (id==0){
      return
    }
    
    var qty_done = this.op['qty_done']

    var model = 'warehouse.app'
    var method = 'get_object_id'
    var values = {'id': id, 'model': this.model}

    this.odoo.execute(model, method, values).then((res)=>{
      if (res['id']!=0){
        this.pick = res['values']['picking_id']
        this.op = res['values']

        if (id = this.last_id){
          this.op['qty_done'] = qty_done
        }
        this.check_needs()
        this.get_op_ready()
        this.cargar = false
        this.last_id = id
        this.uom_to_uos = this.op['product_qty']/this.op['uos_qty']
        this.op['qty_done'] = this.op['qty_done'].toFixed(2)
        this.op['uos_qty_done'] = this.convert_uom_to_uos(this.op['qty_done'])
        return true;
      }
      else {
        this.presentAlert('Error!', 'No se pudo recuperar las operaciones');
      }
    })
    .catch(() => {
      this.presentAlert('Error!', 'Error al conectarse a odoo');
    });

  }
  showPackage(product_id, qty, dest=false){
    if (this.op['pda_done']){return}
    var method = 'get_available_package'
    var values = {'product_id': product_id, 'qty': qty, 'op_id': this.op_id}
    var object_id;
    
    this.odoo.execute('stock.quant.package', method, values).then((pack_ids: Array<{}>)=>{
    
      if (!(pack_ids && pack_ids.length)) {
        pack_ids[0]={'display_name': this.op['pack_id']['name'], 'location_id': this.op['location_id']['name'], 'virtual_available': this.op['product_qty'], 'qty_available': this.op['product_qty'], 'id': this.op['pack_id']['id']}
      }
      let myModal = this.modalCtrl.create(SelectPackagePage, {'op': this.op, 'pack_ids': pack_ids, 'dest': dest}); 
      myModal.present();
      myModal.onDidDismiss(data => 
      {
        if (!data) {return}
        if (!dest){
          if (data['new_pack_id'] = this.op['package_id']['id']){
            this.op['package_id']['checked'] = true
            this.op['lot_id']['checked'] = true
            this.op['location_id']['checked'] = true
            this.get_op_ready()
           }
           else {
             this.change_package(data['new_pack_id'], dest)
           }
          }
        else {
          if (data['new_pack_id'] = this.op['result_package_id']['id']){
            this.op['result_package_id']['checked'] = true
            this.op['location_dest_id']['checked'] = true
            this.get_op_ready()
           }
           else {
             this.change_package(data['new_pack_id'], dest)
           }
        }
      })
      })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
    });
  }    
  
  showSerial(product_id, qty){
    if (this.op['pda_done']){return}
    var method = 'get_available_lot'
    var values = {'product_id': product_id, 'qty': qty, 'op_id': this.op_id}
    var object_id;
    
    this.odoo.execute('stock.production.lot', method, values).then((lot_ids: Array<{}>)=>{

      if (!(lot_ids && lot_ids.length)) {
         lot_ids[0]={'display_name': this.op['lot_id']['name'], 'location_id': this.op['location_id']['name'], 'virtual_available': this.op['product_qty'], 'qty_available': this.op['product_qty'], 'id': this.op['lot_id']['id']}
      }
      let myModal = this.modalCtrl.create(SelectLotPage, {'op': this.op, 'lot_ids': lot_ids}); 
      myModal.present();
      myModal.onDidDismiss(data => 
        {
          if (data) {
            if (data['new_lot_id'] = this.op['lot_id']['id']){
              this.op['lot_id']['checked']=true
              this.op['location_id']['checked']=true
              this.get_op_ready()
            }
            else {
              this.change_lot(data['new_lot_id'])
            }
        }
        
      })
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
    });
  }      
    
  change_package(new_package_id, dest=false){
    this.cargar = true
    var model = 'stock.pack.operation'
    var method = 'pda_change_package'
    var values = {'package_id': new_package_id, 'id': this.op_id}
    this.odoo.execute(this.model, method, values).then((res)=>{
      if (res['return']) {
        if (res != 0){
          this.resetValues()
          this.cargarOp(this.op_id)
        }
        else {
         this.presentAlert('Error', 'Error al cambiar el paquete en la operacion');
        }
      }
      else {
        this.presentAlert('Error', 'Error en Odoo al cambiar el paquete en la operacion');
      }
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo conectar con Odoo');
    });
  }

    
    
  change_lot(new_lot_id){
    this.cargar = true
    var model = 'stock.pack.operation'
    var method = 'change_lot'  
    var values = {'lot_id': new_lot_id, 'id': this.op_id}
    this.odoo.execute(this.model, method, values).then((res)=>{
      if (res) {
        if (res['id'] != 0){
          this.resetValues()
          this.cargarOp(this.op_id)          
        }
        else {
         this.presentAlert('Error', 'Error al cambiar el lote en la operacion');
        }
      }
      else {
        this.presentAlert('Error', 'Error en Odoo al cambiar el lote en la operacion');
      }
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo conectar con Odoo');
    });
  }

  
  /*
  cargarOP2(){
    
    var self = this;
    var last_id = self.op['id']
    var qty_done = self.op_selected['qty_done']
    var last_picking_id = self.op['picking_id']
    self.resetOPValues();
    
    
    odoo.search_read(self.model, self.domain, self.op_fields, 0, 0).then(
                function (value) {
                  //self.resetValues()
                  self.op = value[0];
                  if (self.op['id'] == last_id){
                    self.op['qty_done'] = qty_done
                  } else {
                    self.op['qty_done'] = self.op['product_qty']
                  }
                  
                  if (self.op['picking_id'] != last_picking_id){
                    self.cargarPick()
                  }

                  self.cargar = false;
                  if (self.op['result_package_id']){
                    self.result_package_id = 0;
                    self.op_selected['result_package_id'] = self.op['result_package_id'];
                  }
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Error !', 'Se ha producido un error al recargar la operacion');
                }
                );
        }
  */

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

submitScan(){
  if (this.op['pda_done']){return}
  if (this.check_changes()){return}
  var values = {'model':  ['stock.quant.package', 'stock.production.lot', 'stock.location'], 'search_str' : this.barcodeForm.value['scan']};
  this.barcodeForm.reset();
  this.submit(values);
  }

check_changes(do_id=true){
  var res = false;
  if (this.op['pda_done'] && do_id){
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


submit (values)  {
  if (this.op['pda_done']){return}
  if (this.check_changes()){return}
  var model = 'warehouse.app'
  var method = 'get_object_id'  
  this.odoo.execute(this.model, method, values).then((res)=>{
    if (res) {
      if (res['id']== 0){
        this.presentAlert('Scan', res['message']);
      }
      else {
        this.check_scan_value(res)
      }
    }
    else {
      this.presentAlert('Scan', 'Error al buscar values ' + ['search_str']);
    }
  })
  .catch(() => {
    this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
  });

}

check_scan_value(res){

}


badge_checked(object){
  if (this.op['pda_done']){return}
  object.checked = !object.checked
  this.get_op_ready()
}
/*
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
                    self.cargar = true;
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
                      self.cargar = true;
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
                        self.cargar = true;
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
                      self.cargar = true;
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
                        self.cargar = true;
                        self.doOp(self.op['id']);
                        
                      }  
                      else {('stock.quant.package', op.package_id.id)
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
                      self.cargar = true;
                      self.presentToast('Confirmado cambio de paquete de destino')
                    }       
                  
                    else if (self.package_dest_id_change != 0 && self.package_id_change != value.id){
                      self.package_dest_id_change = 0;
                      self.presentToast('Cambio de paquete de destino cancelado')
                    }
                  }
                  else if (self.op['location_dest_id_need_check'] && !Boolean(self.op['result_package_id']))
                    { self.cargar = true;
                      self.doOp(self.op['id']);
                    }
                  // CASO 11. DESTINO + UBICACION DESTINO (<>) => CONFIRMA NUEVO UBICACION DESTINO >> CAMBIO DESTINO EN OP + CARGAR OP + CARGAR SLIDES
                }
                self.check_state();
                if (self.waiting>=4 && self.op['location_dest_id_need_check'] && !self.cargar){
                    self.doOp(self.op['id']);
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

*/
  get_next_op(id, index){
    var self = this;
    let domain = []
    var ops = self.ops.filter(function (op) {
      return op.pda_done == false && op.id != id}
    )
    if (ops.length==0) {
      return false
    }

    index = index + 1;
    if (index > (self.ops.length-1)) {
      index = 0;
    };
    if (self.ops[index].pda_done) {
      return self.get_next_op(id, index)
    }
    this.index = index
    this.op_id = self.ops[index]['id']
    return self.ops[index]['id'];
  }
  

  doOp(id, do_id=true){
    if (this.check_changes(do_id)){return}
    
    
    this.cargar = true;
    
    var method = 'doOp'
    var values = {'id': id, 'qty_done': this.op['qty_done'], 'do_id': do_id}
    var object_id;
    
    this.odoo.execute(this.model, method, values).then((res)=>{
      if (res) {
        this.ops[this.index]['pda_done'] = do_id
        if (do_id) {
        this.get_next_op(id, this.index)}
        this.cargarOp(this.op_id)

      }
      else {
        this.presentAlert('Falla!', 'Error al marcar la operación como realizada');
      }
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
    });
    
  }
  

  inputQty2() {
    if (this.op['pda_done']){return}
    if (this.check_changes()){return}
    
    var self = this;
    
    let alert = this.alertCtrl.create({
      title: 'Qty',
      message: 'Cantidad a mover',
      inputs: [
        {
          name: 'qty',
          placeholder: self.op['qty_done'].toString()
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
          text:'Qty Ok',
          handler:(data)=>{
            self.op['qty_done'] =  self.op['product_qty'];
            self.input = 0;
            this.get_op_ready()
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
              this.get_op_ready()
              /*self.check_state();*/
            }
            self.input = 0;

          }
        }
      ]
    });

    self.input = alert._state;
    alert.present();
  }
  inputUomQty(){
    this.inputQty(this.op['product_uom_id']['name'], this.op['product_qty'], this.op['qty_done'], false, 'Cantidades')
  }
  inputUosQty(){
    this.inputQty(this.op['uos_id']['name'], this.op['uos_qty'], this.convert_uom_to_uos(this.op['qty_done']), true, 'Cantidades')
  }
  inputQty(uom_name, ordered_qty, qty_done, uos=false, title ="Qty") {
    if (this.op['pda_done']){return}
    if (this.check_changes()){return}
    
    var self = this;
    
    let alert = this.alertCtrl.create({
      title: title,
      message: uom_name,
      inputs: [
        {
          name: 'qty',
          placeholder: qty_done.toString()
        },
       
      
      ],
      buttons: [
        {
          text: 'Cancelar',
          handler: () => {
            console.log('Cancel clicked');
          }
        },
        {
          text:'Qty Ok',
          handler:(data)=>{
            this.get_uom_uos_qtys(uos, ordered_qty)
            self.input = 0;
            this.get_op_ready()
          }
        },
      
        {
          text: 'Guardar',
          handler: (data) => {
            console.log('Saved clicked');
            console.log(data.qty);

            if (data.qty<0){
              self.presentAlert('Error!', 'La cantidad debe ser mayor que 0');
            }
            else if (data.qty) {
              this.get_uom_uos_qtys(uos, data.qty)
              this.get_op_ready()
              /*self.check_state();*/
            }
            self.input = 0;

          }
        }
      ]
    });

    self.input = alert._state;
    alert.present();
  }

  get_uom_uos_qtys(uos, qty: number){
    if (uos){
      this.op['qty_done'] =  this.convert_uos_to_uom(qty);
      this.op['uos_qty_done'] = qty.toFixed(2);
    }
    else {
      this.op['qty_done'] = qty.toFixed(2);
      this.op['uos_qty_done'] = this.convert_uom_to_uos(qty);
    }
  }
}