import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController } from 'ionic-angular';
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

    qty: number;

    constructor(public navCtrl: NavController, public navParams: NavParams,
              public viewCtrl: ViewController,
              private prodData: ProductionProvider) {
        this.qty = 0.0;
    }

    ionViewDidLoad() {
    console.log('ionViewDidLoad ScrapModalPage');
    }

    confirm() {
        var res = {};
        res['qty'] = this.qty;
        this.viewCtrl.dismiss(res);
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

}
