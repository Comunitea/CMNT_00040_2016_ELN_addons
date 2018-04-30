import { Component } from '@angular/core';
import { IonicPage, ViewController, NavParams, AlertController} from 'ionic-angular';
//import { ViewChild } from '@angular/core';
//import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
//import { HostListener } from '@angular/core';


@IonicPage()
@Component({
  selector: 'page-select-lot',
  templateUrl: 'select-lot.html',
})
export class SelectLotPage {

  op
  lot_ids
  cargar
  constructor(public viewCtrl: ViewController, public toastCtrl: ToastController, public storage: Storage, public navParams: NavParams, public alertCtrl: AlertController) {
    
    this.op = this.navParams.data.op;
    this.lot_ids =  this.navParams.data.lot_ids;
  }

  guardar(return_quant_id){
    let return_data = {'return_quant_id': return_quant_id}
    this.viewCtrl.dismiss(return_data);
  }
  cancelar() {
    this.viewCtrl.dismiss();
  } 
  aplicar_lote(){
    this.click_lot(this.op['lot_id']['id'])
  }
  click_lot(id){
    let return_data = {'new_lot_id': id}
    this.viewCtrl.dismiss(return_data);
   
  }


  ionViewDidLoad() {
    console.log('ionViewDidLoad SelectLotPage');
  }

}
