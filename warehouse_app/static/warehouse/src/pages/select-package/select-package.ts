import { Component } from '@angular/core';
import { IonicPage, ViewController, NavParams, AlertController} from 'ionic-angular';
import { ToastController } from 'ionic-angular';
/**
 * Generated class for the SelectPackagePage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-select-package',
  templateUrl: 'select-package.html',
})
export class SelectPackagePage {

  op
  pack_ids
  cargar
  constructor(public viewCtrl: ViewController, public toastCtrl: ToastController, public navParams: NavParams, public alertCtrl: AlertController) {

    this.op = this.navParams.data.op;
    this.pack_ids =  this.navParams.data.pack_ids;
  }

  guardar(return_quant_id){
    let return_data = {'return_quant_id': return_quant_id}
    this.viewCtrl.dismiss(return_data);
  }
  cancelar() {
    this.viewCtrl.dismiss();
  } 
  aplicar_pack(){
    this.click_pack(this.op['pack_id']['id'])
  }
  nuevo_pack(){
    this.click_pack(-1)
  }
  borrar_pack(){
    this.click_pack(0)
  }
  click_pack(id){
    let return_data = {'new_pack_id': id}
    this.viewCtrl.dismiss(return_data);
   
  }
  ionViewDidLoad() {
    console.log('ionViewDidLoad SelectPackagePage');
  }

}
