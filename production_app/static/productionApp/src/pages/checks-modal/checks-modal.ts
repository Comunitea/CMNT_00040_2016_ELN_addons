import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { HomePage } from '../../pages/home/home';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ChecksModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

declare var OdooApi: any;

@IonicPage()
@Component({
  selector: 'page-checks-modal',
  templateUrl: 'checks-modal.html',
})
export class ChecksModalPage {
    product_id;
    quality_type;
    quality_checks;

    constructor(public navCtrl: NavController, public navParams: NavParams, public viewCtrl: ViewController, 
                private storage: Storage, public alertCtrl: AlertController, private prodData: ProductionProvider) {
        this.product_id = this.navParams.get('product_id');
        this.quality_type = this.navParams.get('quality_type');
        this.quality_checks = []
        this.getQualityChecks(this.quality_type)
    }
    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    getQualityChecks(quality_type) {
        if (quality_type == 'start') {
            this.quality_checks = this.prodData.start_checks;
        }
        else{
            this.quality_checks = this.prodData.freq_checks;
        }
    }
     
    ionViewDidLoad() {
        console.log('ionViewDidLoad ChecksModalPage');
    }
    closeModal() {
        this.viewCtrl.dismiss(this.quality_checks);
    }

}
