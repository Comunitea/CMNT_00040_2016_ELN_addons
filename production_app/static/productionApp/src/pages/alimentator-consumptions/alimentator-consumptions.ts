import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ModalController } from 'ionic-angular';
import { ConsumeModalPage } from '../../pages/consume-modal/consume-modal';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the AlimentatorConsumptionsPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-alimentator-consumptions',
  templateUrl: 'alimentator-consumptions.html',
})
export class AlimentatorConsumptionsPage {

    consumptions_in: Object[];
    consumptions_out: Object[];
    constructor(public navCtrl: NavController, 
                public navParams: NavParams,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider) {

    }

    ionViewDidLoad() {
        this.consumptions_in = this.prodData.consumptions_in;
        this.consumptions_out = this.prodData.consumptions_out;
    }

    consume_click(line){
        var mydata = {'line': line}
        let consumeModal = this.modalCtrl.create(ConsumeModalPage, mydata);
        consumeModal.present();

         // When modal closes
         consumeModal.onDidDismiss(res => {
            this.prodData.saveConsumptionLine(res)
        });
    }

}
