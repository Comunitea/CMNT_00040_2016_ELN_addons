import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';

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
    moves: Object[];
    constructor(public navCtrl: NavController, public navParams: NavParams, private prodData: ProductionProvider) {

    }

    ionViewDidLoad() {
        // this.prodData.getConsumptions();
        this.moves = this.prodData.consumptions;
    }

}
