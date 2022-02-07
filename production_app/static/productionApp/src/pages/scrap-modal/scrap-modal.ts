import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ScrapModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-scrap-modal',
  templateUrl: 'scrap-modal.html',
})
export class ScrapModalPage {
    navbarColor: string = 'primary';
    qty;
    uos_qty;
    ctrl;
    reason_id: number;
    reason_name: string;
    reasons: Object[];

    constructor(public navCtrl: NavController, private storage: Storage,
              public navParams: NavParams,
              public viewCtrl: ViewController, public alertCtrl: AlertController,
              private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        this.qty = 0.0;
        this.uos_qty = 0.0;
        this.ctrl = 'do';
        this.reason_id = 0;
        this.reasons = this.prodData.scrap_reasons;
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ScrapModalPage');
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    confirm() {
        var res = {};
        if (!isNaN(this.qty) && this.qty != '' && this.qty > 0) {
            res['qty'] = +this.qty;
        } else {
            this.presentAlert("Error", "Es obligatorio indicar una cantidad mayor que 0");
            return;
        }
        if (this.reason_id) {
            res['reason_id'] = this.reason_id;
        } else {
            this.presentAlert("Error", "Es obligatorio indicar un motivo");
            return;
        }
        res['reason_id'] = this.reason_id;
        this.viewCtrl.dismiss(res);
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

    reasonSelected(reason) {
        this.reason_id = reason.id
        this.reason_name = reason.name
    }

}
