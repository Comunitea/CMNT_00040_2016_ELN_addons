import { Component } from '@angular/core';
import { IonicPage,  NavParams, ViewController, AlertController} from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';
import * as $ from 'jquery';

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
        this.quality_checks = this.initQualityChecks();
    }

    initQualityChecks(){
        var qc_list = this.navParams.get('quality_checks');
        var new_list = []
        for (var index in qc_list){
            var qc = qc_list[index];
            var new_ = {};
            $.extend(new_, qc);
            new_list.push(new_); 
        }
        return new_list;
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
                if ( qc.value !== 'OK'){
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que ser <b>OK</b');
                    error = true;
                    // break;
                }
            }
            if (qc.value_type == 'text'){
                if (qc.required_text != '' && qc.required_text.toUpperCase() != qc.value.toUpperCase()){
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que ser <b>' + qc.required_text + '</b');
                    error = true;
                    // break;
                }
            }
            else if (qc.value_type == 'numeric'){
                if (qc.min_value != 0 &&  qc.value < qc.min_value ){
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que ser mayor que <b>' + qc.min_value + '</b');
                    error = true;
                    // break;
                }
                else if (qc.max_value != 0 &&  qc.value > qc.max_value ){
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que ser menor que <b>' + qc.max_value + '</b');
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
