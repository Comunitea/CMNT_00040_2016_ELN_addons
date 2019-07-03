import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ReasonsModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-reasons-modal',
  templateUrl: 'reasons-modal.html',
})
export class ReasonsModalPage {
    reasons: Object[];
    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                private prodData: ProductionProvider) {
        this.reasons = [];
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ReasonsModalPage');
    }
    closeModal() {
        this.viewCtrl.dismiss(0);
    }
    reasonSelected(reason) {
        if (reason.reason_type == 'organizative'){
            this.viewCtrl.dismiss({'reason_id': reason.id, 'create_mo': false});
        }
        else{
            let confirm = this.alertCtrl.create({
                  title: '¿Crear orden de mantenimiento?',
                  message: "Se creará una orden de mantenimiento asociada al registro de la aplicación",
                  buttons: [
                    {
                      text: 'No',
                      handler: () => {

                        this.viewCtrl.dismiss({'reason_id': reason.id, 'create_mo': false});
                      }
                    },
                    {
                      text: 'Si',
                      handler: () => {
                        this.viewCtrl.dismiss({'reason_id': reason.id, 'create_mo': true});
                      }
                    }
                  ]
            });
            confirm.present();
        }
    }
    selectOrganizative(reason){
        this.reasons = this.prodData.organizative_reasons
    }
    selectTechnical(reason){
        this.reasons = this.prodData.technical_reasons
    }

}
