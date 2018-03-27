import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController } from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';


@IonicPage()
@Component({
  selector: 'page-finish-modal',
  templateUrl: 'finish-modal.html',
})
export class FinishModalPage {

    qty: number;
    lot: string;
    date: string;
    constructor(public navCtrl: NavController, public navParams: NavParams, 
                public viewCtrl: ViewController,
                private prodData: ProductionProvider) {
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad FinishModalPage');
    }

    confirm() {
        var res = {'qty': this.qty, 'lot': this.lot, 'date':this.date}
        console.log("res")
        console.log(res);
        this.viewCtrl.dismiss(res);
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

}
