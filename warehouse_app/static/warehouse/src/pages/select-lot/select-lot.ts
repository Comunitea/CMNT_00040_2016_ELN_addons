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
  constructor(public viewCtrl: ViewController, public toastCtrl: ToastController, public navParams: NavParams, public alertCtrl: AlertController) {
    this.op = this.navParams.data.op;
    this.lot_ids =  this.navParams.data.lot_ids;
  }

  cancelar() {
    this.viewCtrl.dismiss();
  } 

  click_lot(id, location_id = false){
    
    let return_data = {'new_lot_id': id, 'location_id': location_id}
    this.viewCtrl.dismiss(return_data);
   
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad SelectLotPage');
  }

}
