import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
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

    moves: Object[];
    constructor(public navCtrl: NavController, public navParams: NavParams, private prodData: ProductionProvider) {

    }

    ionViewDidLoad() {
        // this.prodData.getConsumptions();
        this.moves = this.prodData.consumptions;
    }

}
