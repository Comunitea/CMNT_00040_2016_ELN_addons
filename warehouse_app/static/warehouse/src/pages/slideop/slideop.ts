import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController, ToastController } from 'ionic-angular';
import { ViewChild } from '@angular/core';

import { FormBuilder, FormGroup } from '@angular/forms';

/*import { PROXY } from '../../providers/constants/constants';*/
/**
 * Generated class for the SlideopPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
import { HostListener } from '@angular/core';

import { HomePage } from '../home/home';
import { TreepickPage } from '../treepick/treepick';
import { TreeopsPage } from '../treeops/treeops';
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
  
  

  @HostListener('document:keyup', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    this.presentToast(event.key)
    if (!event.shiftKey){
      if (event.key=='ArrowLeft'){
        this.move_index(-1)
        
      }
      if (event.key=='ArrowRight'){
        this.move_index(1)
      }
    }
    else{
      if (event.key=='ArrowLeft'){
        /*FORM*/
        this.goHome()
      }
      if (event.key=='ArrowRight'){
        /*LISTADO DE PICKS*/
        if (!this.op['pda_done'] && this.op_ready) {
          this.doOp(this.op_id, true)
        }
        else {
          this.presentToast("No puedes procesarla")
        }
      }
    }

  }
  
  model = 'stock.pack.operation'
  isPaquete: boolean = true;
  cargar = true;
  scan = ''
  scan_id = {}
  last_read: number = 0
  last_scan: ''
  WAITING: ['package_id', 'location_dest_id', 'product_id', 'lot_id', 'location_id', 'location_dest_id']
  waiting: number

  barcodeForm: FormGroup;
  Home = HomePage
  
  package_change: number = 0;
  location_change: number = 0;
  lot_id_change: number = 0;
  
  index
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
  
  constructor(public navCtrl: NavController,  private modalCtrl: ModalController, private toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, private alertCtrl: AlertController, private aux: AuxProvider , private odoo: OdooProvider) {
    this.op_id = this.navParams.data.op_id;
    this.ops = this.navParams.data.ops;
    if (!this.ops){
      this.presentToast('Aviso:No hay operaciones', false)
      }
    this.index = Number(this.navParams.data.index || 0);
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    
    this.waiting = this.navParams.data.origin || 0;
    
    this.cargarOp(this.op_id)
  
    }
  

  move_index(cont1){
    this.cargar=true
    this.index += cont1
    if (this.index<0){this.index=this.ops.length-1}
    if (this.index==this.ops.length){this.index=0}
    this.op_id = this.ops[this.index]['id']
    
    this.cargarOp(this.op_id)

  }
  resetForm(){
    this.cargar=true
    let orig_id = this.op_id
    
    this.cargarOp(orig_id)
  }

  reverse_ops(){
    this.cargar=true
    this.ops = this.ops.reverse()
    this.op_id = this.ops[0]['id']
    this.cargarOp(this.op_id)
  }
 

  
  resetValues(){
    this.advance = false
    this.op_ready = false
    this.last_id = 0
    this.cargar = true
    this.message = '';
    this.op = {};
    this.model =  'stock.pack.operation';
    this.waiting=0;
    this.package_change = 0;
    this.lot_id_change = 0;
    this.location_change = 0;
    this.scan = ''
    this.last_read = 0;
    this.input = 0;
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
 
  goHome(){
    this.navCtrl.setRoot(TreeopsPage, {picking_id: this.pick['id'], model: this.pick['model'], info_pick:false})
     //this.navCtrl.setRoot(TreepickPage, {borrar: true, login: null});
  }


  
  check_needs(reset=false){
    
    if (this.op['pda_done']){reset = true}
    if (this.op['package_id']) {this.op['package_id']['checked'] = this.navParams.data.package_id ||reset; this.navParams.data.package_id = false}
    if (this.op['result_package_id']) {this.op['result_package_id']['checked'] = reset}
    if (this.op['lot_id']) {this.op['lot_id']['checked'] = this.navParams.data.lot_id || reset; this.navParams.data.lot_id = false }
    this.op['location_id']['checked'] = !this.op['location_id']['need_check'] || reset
    this.op['location_dest_id']['checked'] = !this.op['location_dest_id']['need_check'] || reset

  }

  get_op_ready () {    
    // Lista para confirmación ????
    this.op_ready = (!this.op['package_id'] || (this.op['package_id'] && this.op['package_id']['checked'])) 
                      && (!this.op['result_package_id'] || (this.op['result_package_id'] && this.op['result_package_id']['checked'])) 
                      && (!this.op['lot_id'] || (this.op['lot_id'] && this.op['lot_id']['checked'])) 
                      && this.op['location_id']['checked'] 
                      && this.op['location_dest_id']['checked'] 
                      && (this.op['qty_done']>0)
    
    // Miro confirmación automática
    if (this.op_ready 
        && this.op['need_confirm'] 
        // Solo se confirman automaticamente las que qty_done  = a lo que se pide
        && this.op['qty_done'] == this.op['product_qty']){
      this.doOp(this.op_id, true)
      }
    this.show_scan()
    
  }

  // Valorar traer el número de decimales de la unidad de Odoo
  convert_uom_to_uos(qty){
    return (qty/this.uom_to_uos).toFixed(2)
  }
  convert_uos_to_uom(qty){
    return (qty*this.uom_to_uos).toFixed(2)
  }
  convert_to_fix(qty){
    return (qty*1).toFixed(2)
  }

  check_loaded_op(res, id){

    // Comprobaciones una vez cargada la operacion con id
    
    let qty_done = this.op['qty_done'] || 0.00

    this.op = res
    id = res['id'] || 0
    this.pick = this.navParams.data.pick && this.navParams.data.pick
    
    if (id = this.last_id){
      this.op['qty_done'] = qty_done
    }
    if (this.navParams.data.lot_id){this.last_scan = this.op['lot_id']['name']}
    if (this.navParams.data.package_id){this.last_scan = this.op['package_id']['name']}
    
    this.check_needs()
    this.get_op_ready()
    
    this.last_id = id
    this.uom_to_uos = this.op['product_qty']/this.op['uos_qty']
    this.op['qty_done'] = this.op['qty_done'].toFixed(2)
    this.op['uos_qty_done'] = this.convert_uom_to_uos(this.op['qty_done'])
    this.get_index(this.ops, id)
    this.show_scan()

    return true;
  }


  cargarOp(id=0){ 
    if (id==0){
      return
    }
    
    var model = 'stock.pack.operation'
    var method = 'get_op_id'
    var values = {'id': id, 'model': this.model}
    this.odoo.execute(model, method, values).then((res)=>{
     
      if (res['id']!=0){
        this.resetValues()
        this.check_loaded_op(res, id)
        this.cargar = false
      }
      else {
        this.cargar = false
        this.presentAlert('Error!', 'No se pudo recuperar las operaciones');
      }
      this.show_scan()
    })
    .catch(() => {
      this.cargar = false
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
        pack_ids[0]={ 'display_name': this.op['pack_id']['name'], 
                      'location_id': this.op['location_id']['name'], 
                      'virtual_available': this.op['product_qty'], 
                      'qty_available': this.op['product_qty'], 
                      'id': this.op['pack_id']['id']}
      }
      let myModal = this.modalCtrl.create(SelectPackagePage, {'op': this.op, 'pack_ids': pack_ids, 'dest': dest}); 
      myModal.present();
      
      myModal.onDidDismiss(data => 
      {
      
        if (!data) {
          this.show_scan()
          return}
        if (!dest){
          if (data['new_pack_id'] == this.op['package_id']['id']){
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
          if (data['new_pack_id'] == this.op['result_package_id']['id']){
            this.op['result_package_id']['checked'] = true
            this.op['location_dest_id']['checked'] = true
            this.get_op_ready()
           }
           else {
             this.change_package(data['new_pack_id'], dest)
           }
        }
        this.show_scan()
      })
      })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
    });
  }    
  
  serial_ok(new_lot_id, location_id=false){

    if (new_lot_id == this.op['lot_id']['id']){
      this.op['lot_id']['checked']=true
      this.op['location_id']['checked']=true
      this.get_op_ready()
      this.cargar = false   
    }
    else {
      console.log(this.op['lot_id'])
      this.change_lot(new_lot_id, location_id)
    }
  }

  location_ok(id, field){
    if (this.op[field]['id'] == id){
      this.op[field]['checked']=true
      this.get_op_ready()
      this.cargar = false 
    }
    else
    {
      console.log(this[field])
    }
  }
  package_ok(package_id){
    if (package_id == this.op['package_id']['id']){
      this.op['package_id']['checked']=true
      this.op['lot_id']['checked']=true
      this.op['location_id']['checked']=true
      this.get_op_ready()
      this.cargar = false   
    }
    else {
      console.log(this.op['package_id'])
      //this.change_package(package_id)
    }
  }
  result_package_ok(package_id){
    if (package_id == this.op['result_package_id']['id']){
      this.op['result_package_id']['checked']=true
      this.op['location_dest_id']['checked']=true
      this.get_op_ready()
      this.cargar = false   
    }
    else {
      console.log(this.op['result_package_id'])
      //this.change_package(package_id)
    }
  }
  
  confirm_qties(){
    if (this.op['pda_done']){return}
    if (this.check_changes()){return}
    this.get_uom_uos_qtys(false, this.op['product_qty'])
    this.get_op_ready()
    this.cargar = false 
  }

  showSerial(product_id, qty){
    if (this.op['pda_done']){return}
    this.cargar = true
    var method = 'get_available_lot'
    var values = {'product_id': product_id, 'qty': qty, 'op_id': this.op_id, 'lot_id': this.op['lot_id']['id'], 'location_id': this.op['location_id']['id'], 'move_id': this.op['move_id']}
    var object_id;
    
    this.odoo.execute('stock.production.lot', method, values).then((lot_ids)=>{

      //if (!(lot_ids && lot_ids.length)) {
      //   lot_ids[0]={'display_name': this.op['lot_id']['name'], 'location_id': this.op['location_id']['name'], 'virtual_available': this.op['product_qty'], 'qty_available': this.op['product_qty'], 'id': this.op['lot_id']['id']}
         
      
      let myModal = this.modalCtrl.create(SelectLotPage, {'op': this.op, 'lot_ids': lot_ids}); 
      myModal.present();
      myModal.onDidDismiss(data => 
        { 
          

          if (data) {
            this.serial_ok(data['new_lot_id'], data['location_id'])
            this.last_scan = this.op['lot_id']['name']
          }
          else {
            this.cargar=false
          }
          
          this.show_scan()
      })
      
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
      this.show_scan()
    });
    this.show_scan()
  }      
    
  change_package(new_package_id, dest=false){
    this.cargar = true
    var model = 'stock.pack.operation'
    var method = 'pda_change_package'
    var values = {'package_id': new_package_id, 'id': this.op_id}
    this.odoo.execute(this.model, method, values).then((res)=>{
      if (res['return']) {
        if (res != 0){
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

    
    
  change_lot(new_lot_id, location_id){
    this.cargar = true
    var model = 'stock.pack.operation'
    var method = 'pda_change_lot'  
    var values = {'lot_id': new_lot_id, 'id': this.op_id, 'location_id':  location_id}
    console.log(values)
    this.odoo.execute(this.model, method, values).then((res)=>{
      if (res) {
        if (res['id'] != 0){
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
    this.show_scan()
  }


  presentAlert(titulo, texto) {
    const alert = this.alertCtrl.create({
        title: titulo,
        subTitle: texto,
        buttons: ['Ok']
    });
    alert.present();
    this.show_scan()
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
      this.show_scan()
    });
    toast.present();
  }

  Scan(scan){
    this.barcodeForm.reset()
    this.show_scan(200)
    if (this.op['pda_done']){
      return}
    if (this.check_changes()){
      return}
    // Compruebo si es algo de la operación lo que se ha escaneado
    if (!this.find_scanned_in_op(scan))
      {
        console.log('Busco en el server ' + scan);
        //this.find_in_server(scan)
      }
  }


  find_scanned_in_op(scan){
    let product_id = this.op['pda_product_id']
    let package_id = this.op['package_id'] || false
    let result_package_id = this.op['result_package_id'] || false
    let lot_id = this.op['lot_id'] || false
    let location_id = this.op['location_id']
    let location_dest_id = this.op['location_dest_id']

    //Escaneo producto >>> Muestra lotes
    if (product_id && product_id['ean_13'] == scan) {this.showSerial(product_id['id'], this['op']['product_qty'])}
    
    //Escaneo paquete >>
    else if (package_id && !package_id['checked'] && package_id['name'] == scan) {this.package_ok(package_id['id'])}
    else if (package_id && package_id['checked'] && package_id['name'] == scan && this.last_scan == scan && !this.op_ready && this.op['qty_done']==0) {this.confirm_qties()}
    else if (result_package_id && package_id['checked'] && result_package_id['name'] == scan) {this.package_ok(package_id['id'])}

    //Escaneo lote
    else if (lot_id && !lot_id['checked'] && lot_id['name'] == scan) {this.serial_ok(lot_id['id'], location_id['id'])}
    else if (lot_id && lot_id['checked'] && lot_id['name'] == scan && this.last_scan == scan && !this.op_ready && this.op['qty_done']==0) {this.confirm_qties()}
    
    //escaneo ubicaición
    else if (location_id && !location_id['checked'] && location_id['loc_barcode']==scan) {this.location_ok(this.op['location_id']['id'], 'location_id')}
    else if (location_id && lot_id['checked'] && location_id['checked'] && location_id['loc_barcode']==scan && this.op['qty_done'] == 0 && this.last_scan == scan) {this.confirm_qties()}
    else if (location_dest_id && !location_id['checked'] && !location_dest_id['checked'] && location_dest_id['loc_barcode']==scan) {this.location_ok(this.op['location_dest_id']['id'], 'location_dest_id')}
    
    //Si la operacion está lista y se repite el scan se hace la operacion
    else if (this.op_ready && this.last_scan == scan){
      this.doOp(this.op_id, true)
      this.last_scan = ''
      return false
      }
    
    else {
      this.last_scan = ''
      return false
    }
    this.last_scan = scan
    return true
  }

  submitScan(){
    
    let scan = this.barcodeForm.value['scan']
    let res = this.Scan(scan)
    this.show_scan()
    return res

  }

  find_in_server(str){
    var values = {'model':  ['stock.quant.package', 'stock.production.lot', 'stock.location', 'product.product'], 
                  'search_str' :str, 
                  'product_id': this.op['pda_product_id']['id']};
    //this.barcodeForm.reset();
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

  get_id(val){
    return (val && val[0]) || false
  }


  submit (values)  {
    if (this.op['pda_done']){return}
    if (this.check_changes()){return}
    var model = 'warehouse.app'
    var method = 'get_scanned_id'  
    console.log(values)
    this.odoo.execute(model, method, values).then((res)=>{
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
      this.show_scan()
    })
    .catch(() => {
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');

    });

  }

  check_scan_value(res){
    console.log(res)
  } 


  badge_checked(object){
    if (this.op['pda_done']){return}
    object.checked = !object.checked
    this.get_op_ready()
  }

  get_index(ops, id){
    let index
    for (index in ops){
      if (ops[index]['id'] == id){
        break
      }
    }
    return index
  }
  get_next_op(id, list_ops=this.ops, forward = true){
    // Devuelve el siguiente id con pda_done false, con forward hacia delante.

    let ops = list_ops.filter(function (op) {
      return op.pda_done == false
    })
    
    let min_index = -1
    if (forward){
      min_index = this.get_index(ops, id)
    }
  
    if (ops.length==0) {
      return 0
    }
    let next_id = 0
    this.index = -1
    for (let index in ops){
      if (!forward && !ops[index]['pda_done'] && ops[index]['id'] != id){
        next_id = ops[index]['id']
        break
      }
      if (this.index!=-1){
        next_id = ops[index]['id']
        break
      }
      if (ops[index]['id'] == id && parseInt(index) > min_index){
        this.index = index
      }
    }

    if (next_id || !forward){
      return next_id
    }
    else {
      return this.get_next_op(id, ops, false)}
  }


  doOp(id, do_id=true){
    if (this.check_changes(do_id)){return}
    
    this.cargar = true;
    var method = 'doOp'
    var values = {'id': id, 'qty_done': this.op['qty_done'], 'do_id': do_id, pick_id: this.pick['id'], pick_model: this.pick['model'], next_id: this.get_next_op(id)}
    
    this.odoo.execute(this.model, method, values).then((res)=>{
      if (res) {
        this.presentToast(res['aviso']||res['error'])
        
        if (res['id']!=0){
          this.check_loaded_op(res, res['id'])
          this.cargar=false
        }
        else {
          this.navCtrl.setRoot(TreepickPage);           
        }
      }
      else {
        this.cargar=false
        this.presentAlert('Falla!', 'Error al marcar la operación como realizada');
      }
    })
    .catch(() => {
      this.cargar=false
      this.presentAlert('Error!', 'No se pudo recuperar ejecutar la operación');
    });
    
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
          text:'Qty Ok',
          handler:(data)=>{
            this.get_uom_uos_qtys(uos, ordered_qty)
            self.input = 0;
            this.show_scan()
          }
        },
      
        {
          text: 'Guardar',
          handler: (data) => {
            if (data.qty<0){
              self.presentAlert('Error!', 'La cantidad debe ser mayor que 0');
            }
            else if (data.qty) {
              this.get_uom_uos_qtys(uos, data.qty)
            }
            self.input = 0;
            this.show_scan()  
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
      this.op['uos_qty_done'] = this.convert_to_fix(qty);
    }
    else {
      this.op['qty_done'] = this.convert_to_fix(qty);
      this.op['uos_qty_done'] = this.convert_uom_to_uos(qty);
    }
    this.get_op_ready()
  }

  show_scan(t1s=150){

    setTimeout(() => {
      this.myScan.setFocus();
    },t1s);
  }
}
