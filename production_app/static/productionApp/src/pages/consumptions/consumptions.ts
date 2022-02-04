import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ModalController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';
import { CalculatorModalPage } from '../../pages/calculator/calculator';
import es from '@angular/common/locales/es';
import { registerLocaleData } from '@angular/common';

/**
 * Generated class for the ConsumptionsPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-consumptions',
  templateUrl: 'consumptions.html',
})
export class ConsumptionsPage {
    allowed_lines: Object[];
    qty_to_calculate;
    navbarColor: string = 'primary';
    
    constructor(public navCtrl: NavController, private storage: Storage,
                public navParams: NavParams,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        registerLocaleData(es);
        this.qty_to_calculate = this.prodData.production_qty;
   }

    ionViewDidLoad() {
        this.allowed_lines = this.prodData.consumptions;
    }

    openCalculatorModal() {
        var mydata = {}
        let calculatorModal = this.modalCtrl.create(CalculatorModalPage, mydata);
        calculatorModal.present();
    }

}
