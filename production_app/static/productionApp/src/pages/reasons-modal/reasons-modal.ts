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
    reason_button_selected: string;
    type;

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                private prodData: ProductionProvider) {
        this.reasons = [];
        this.reason_button_selected = 'none';
        this.type = this.navParams.get('type');
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ReasonsModalPage');
    }

    closeModal() {
        this.viewCtrl.dismiss(0);
    }

    reasonSelected(reason) {
        this.viewCtrl.dismiss({'reason_id': reason.id, 'reason_type': reason.reason_type});
    }

    selectOrganizative(reason) {
        if (this.type == 'all' || this.type == 'organizative') {
            this.reasons = this.prodData.organizative_reasons;
            this.reason_button_selected = 'organizative';
        }
    }

    selectTechnical(reason) {
        if (this.type == 'all' || this.type == 'technical') {
            this.reasons = this.prodData.technical_reasons;
            this.reason_button_selected = 'technical';
        }
    }

}
