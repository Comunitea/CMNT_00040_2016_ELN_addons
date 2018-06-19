import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { HostListener } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/

import { Storage } from '@ionic/storage';
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector'
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

  
  max_qty = 0.00
  
  model = 'stock.move'
  move = {}
  domain = []
  package_qty: boolean = true;
  message = ''
  state: number = 0; /* 0 origen 1 destino 2 validar */
  scan_id: string = ''
  cargar
  models = []
  last_scan = ''
  input: number = 0;
  barcodeForm: FormGroup;
  tracking = 'none'
  
  constructor(public navCtrl: NavController, public toastCtrl: ToastController, public navParams: NavParams, private formBuilder: FormBuilder, public storage: Storage,   private odoo: OdooProvider, public alertCtrl: AlertController) {

    this.input = 0;
    this.models =  ['stock.quant.package', 'stock.production.lot', 'stock.location', 'product.product']
    this.cargar=false
    
    this.reset_form();
   
    this.tracking = 'lot';
  }

  reset_form(){
    
    this.state = 0;
    this.scan_id = '';
    this.last_scan = ''
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    this.move = {};
    this['move']['product_qty'] = 0;

  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad ManualPage');
  }
  submitScan(){
    this.cargar=true
    let values
    if (this.state == 2 && this.last_scan == this.barcodeForm.value['scan']){
      this.process_move();
    }
    else if (this.state==1){
      values = {'model': ['stock.location', 'stock.quant_package'], 'search_str' : this.barcodeForm.value['scan'], 'return_object': true};
      this.barcodeForm.reset();
      this.submit(values);
    }
    else {
      values = {'model': this.models, 'search_str' : this.barcodeForm.value['scan'], 'return_object': true};
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
  get_lot_location_ids(id){
    let model = 'stock.production.lot'
    let method = 'get_location_ids'
    let values = {'id': id}
    
    this.odoo.execute(model, method, values).then((val)=>{
      this.move['location_ids'] = val
    })
    .catch(() =>{
      this.presentToast("Error al recuperar las ubicaciones del lote: " + this.move['lot_id'], false);
      return false;
    })
  }

  submit (values, models=[]){
    
    //BUSCO LOS IDS Y EL MODELO
    if (! models){
      models = this.models
    }
    var model = 'warehouse.app'
    var method = 'get_ids'
      this.odoo.execute(model, method, values).then((val)=>{
        this.check_val(val)
      })
      .catch(() =>{
        this.presentToast("Error al recuperar los ids", false);
        return false;
      })
    

  }
  ret_m2o(val, field){
    return {'id': val[field][0], 'name': val[field][1]} 
  }
  get_state() {
    if (this.state == 0 && this.move['product_id']['id'] && this.move['location_id']['id'] && this.move['restrict_lot_id']['id']){return 1}
    if (this.state > 0 && this.move['location_dest_id'] && this.move['product_qty'] > 0.00){return 2}
    return 0
  }

  check_val(val){
    let product_id={}
    let uom_id = {}
    let location_id ={}
    let lot_id = {}
    let location_Dest_id = {}
    let qty = -1
    if (val['model']=='stock.production.lot'){
      qty = 0.00
      if (val['id']){
        this.move['restrict_lot_id'] = val['values'][0]
        this.move['restrict_lot_ids'] = false
        product_id = this.ret_m2o(val['values'][0], 'product_id')
        location_id = this.ret_m2o(val['values'][0], 'location_id')
        uom_id = this.ret_m2o(val['values'][0], 'uom_id')
        this.max_qty = this.move['restrict_lot_id']['qty_available']
        qty = 0.00
        if (!location_id['id']){
          this.get_lot_location_ids(val['id'])
        }
      }
      else {
        this.move['restrict_lot_ids'] = val['values']
        product_id = false
        uom_id = false
        location_id = false
      }
    }
    else if (val['model']=='stock.quant_package'){
      qty = 0.00
      if (val['id']){
        this.move['restrict_package_id'] = val['values'][0]
        this.move['restrict_package_ids'] = false
        lot_id = this.ret_m2o(val['values'][0], 'lot_id')
        product_id = this.ret_m2o(val['values'][0], 'product_id')
        location_id = this.ret_m2o(val['values'][0], 'location_id')
        uom_id = this.ret_m2o(val['values'][0], 'uom_id')
        qty = 0.00
      }
      else {
        this.move['restrict_package_ids'] = val['values']
        product_id = false
        uom_id = false
        location_id = false
      }
    }
    else if (val['model']=='product.product'){
      qty = 0.00
      if (val['id']){
        this.move['product_id'] = val['values'][0]
        this.move['product_ids'] = []
        lot_id = {}
        product_id = {}
        location_id = {}
        uom_id = this.ret_m2o(val['values'][0], 'uom_id')
      }
      else {
        this.move['product_ids'] = val['values']
        product_id = false
        uom_id = false
        location_id = false
      }
      
      }
    else if (val['model']=='stock.location' && this.state==0){
      this.move['location_id'] = this.ret_m2o(val['values'][0], 'location_id')
    }  
    else if (val['model']=='stock.location' && this.state==1){
      this.move['location_dest_id'] = val['values'][0]

    }  
    if (this.state==0){
      if (qty >=0) {this.move['product_qty']=qty}
      this.move['product_id'] = product_id
      this.move['location_id'] = location_id  
      this.move['uom_id'] = uom_id
    }
    this.state = this.get_state()

  }
  
  select_lot (lot_id){
    this.cargar = true
    this.move['restrict_lot_ids']=[]
    this.move['restrict_lot_id']={}
    var values = {'model': 'stock.production.lot', 'id': lot_id, 'return_object': true};
    this.submit(values)
  }

  select_location(location_id){
    let id = location_id[0]
    let name = location_id[1]
    let max_qty = location_id[2]
    let loc = {'location_id': [id, name]}
    let model = 'stock.location'
    let val = {'model': model, 'values': [loc] }
    this.move['location_id'] = this.ret_m2o(val['values'][0], 'location_id')
    this.move['company_id'] = this.ret_m2o(val['values'][4], 'location_id')
    this.max_qty = max_qty
    this.move['product_qty'] = 0
    this.state = this.get_state()
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
              return
            }
            else if (data.qty > this.max_qty){
              this.presentAlert('Error!', 'La cantidad debe ser menor que la disponible');
              return
            }
            
            this['move']['product_qty'] = data.qty
            this.get_state();
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
    var values = {'restrict_package_id': move['restrict_package_id'] && move['restrict_package_id']['id'] || false,
                  'product_id': move['product_id']['id'],
                  'product_qty': move['product_qty'] || 0,
                  'restrict_lot_id': move['restrict_lot_id'] && move['restrict_lot_id']['id'] || false,
                  'location_id': move['location_id']['id'],
                  'result_package_id': move['result_package_id'] && move['result_package_id']['id'] ||false,
                  'location_dest_id': move['location_dest_id']['id'],
                  'package_qty': move['package_qty'] || 0,
                  'product_uom_qty': move['product_qty'] || 0,
                  'company_id': move['company_id'] || false,
                  'origin': 'PDA move'}
    return values
  }

  process_move(){
    /* CREAR Y PROCESAR UN MOVIMEINTO */
    
    var values = this.get_move_values(this['move'])
    var model = 'stock.move'
    var method = 'pda_move'
    this.odoo.execute(model, method, values).then((val)=>{
      if (val['id']!=0){
        this.presentToast(val['message'], false);
        this.reset_form();
        return
      }
      else {
        this.presentToast(val['message'], true);
        return
      }
    })
    .catch(() =>{
      this.presentToast("Error al recuperar los ids", false);
      return false;
    })

  }
  

}
