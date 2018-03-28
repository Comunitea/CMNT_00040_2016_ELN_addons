import { Component } from '@angular/core';
import { IonicPage,  NavParams, ViewController, AlertController} from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ChecksModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */


@IonicPage()
@Component({
  selector: 'page-checks-modal',
  templateUrl: 'checks-modal.html',
})
export class ChecksModalPage {
    product_id;
    quality_type;
    quality_checks;

    constructor(public navParams: NavParams, public viewCtrl: ViewController, 
                private prodData: ProductionProvider, public alertCtrl: AlertController) {
        this.product_id = this.prodData.product_id
        this.product_id = this.navParams.get('product_id');
        this.quality_type = this.navParams.get('quality_type');
        this.quality_checks = this.navParams.get('quality_checks');
    }
     
    ionViewDidLoad() {
        console.log('ionViewDidLoad ChecksModalPage');
    }
    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }
    closeModal() {
        this.viewCtrl.dismiss([]);
    }
    confirmModal() {
        var error = false;
        for (let indx in this.quality_checks) {
            var qc = this.quality_checks[indx];
             if (qc.value_type == 'check'){
                if ( qc.value !== 'Si'){
                    this.presentAlert('Error de validación', 'El valor para ' + qc.name + ' tiene que ser: Si');
                    error = true;
                    // break;
                }
            }
            if (qc.value_type == 'text'){
                if ( qc.required_text != '' && qc.required_text != qc.value){
                    this.presentAlert('Error de validación', 'El valor para ' + qc.name + ' tiene que ser: ' + qc.required_text);
                    error = true;
                    // break;
                }
            }
            else if (qc.value_type == 'numeric'){
                if (qc.min_value != 0 &&  qc.value < qc.min_value ){
                    this.presentAlert('Error de validación', 'El valor para ' + qc.name + ' tiene que ser mayor que  ' + qc.min_value);
                    error = true;
                    // break;
                }
                else if (qc.max_value != 0 &&  qc.value > qc.max_value ){
                    this.presentAlert('Error de validación', 'El valor para ' + qc.name + ' tiene que ser mayor que  ' + qc.min_value);
                    error = true;
                    // break;
                }
            }
        }
        if (!error){
            this.viewCtrl.dismiss(this.quality_checks);
        }
    }

}
