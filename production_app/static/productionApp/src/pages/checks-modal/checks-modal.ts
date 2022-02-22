import { Component } from '@angular/core';
import { IonicPage,  NavParams, ViewController, AlertController} from 'ionic-angular';
import { Storage } from '@ionic/storage';
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
    navbarColor: string = 'primary';
    product_id;
    quality_type;
    quality_checks;

    constructor(private storage: Storage,
        public navParams: NavParams,
        public viewCtrl: ViewController,
        private prodData: ProductionProvider,
        public alertCtrl: AlertController) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        this.product_id = this.prodData.product_id
        this.product_id = this.navParams.get('product_id');
        this.quality_type = this.navParams.get('quality_type');
        this.quality_checks = this.initQualityChecks();
    }

    initQualityChecks() {
        var qc_list = this.navParams.get('quality_checks');
        var new_list = []
        for (var index in qc_list) {
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
            enableBackdropDismiss: false,
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
            if (qc.value_type == 'check') {
                if (qc.value !== 'OK') {
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que ser <b>OK</b>');
                    error = true;
                }
            } else if (qc.value_type == 'text') {
                if (qc.required_text != '' && qc.required_text.toUpperCase() != qc.value.toUpperCase()) {
                    if ((qc.required_text.length == 13 || qc.required_text.length == 14) && qc.value != '??') {
                        this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> no es correcto');
                    } else {
                        this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que ser <b>' + qc.required_text + '</b>');
                    }
                    error = true;
                } else if (!(qc.value.length > 0)) {
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> no puede estar vacío');
                    error = true;
                }
            } else if (qc.value_type == 'numeric') {
                if (qc.value == '') {
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> no puede estar vacío');
                    error = true;
                } else if (qc.value < qc.min_value || qc.value > qc.max_value) {
                    this.presentAlert('Error de validación', 'El valor para <b>' + qc.name + '</b> tiene que estar entre <b>' + qc.min_value + '</b>' + ' y ' + '<b>' + qc.max_value + '</b>');
                    error = true;
                }
            }
	    this.quality_checks[indx]['error'] = error;
        }
        // Si el tipo de control es final, permitimos continuar aunque haya respuestas erróneas
        // En este caso, se grabará el resultado erróneo y se bloqueará el lote
        // Ojo, porque es el único caso que espera recibir el ERP con error = True y provocará el bloqueo del lote
        if (!error || this.quality_type == 'end') {
            this.viewCtrl.dismiss(this.quality_checks);
        }
    }

}
