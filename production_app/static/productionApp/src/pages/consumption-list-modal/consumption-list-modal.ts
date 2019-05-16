import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController } from 'ionic-angular';

/**
 * Generated class for the ConsumptionListModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-consumption-list-modal',
  templateUrl: 'consumption-list-modal.html',
})
export class ConsumptionListModalPage {
    allowed_lines: Object[];
    type: string = 'in';

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController) {
        this.type = this.navParams.get('type');
        this.allowed_lines = this.navParams.get('allowed_lines');
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ConsumptionListModalPage');
    }

    confirmModal() {
        this.viewCtrl.dismiss();
    }

    closeModal() {
        this.viewCtrl.dismiss([]);
    }

    add_line(line){
        this.viewCtrl.dismiss({
           'product_name': line.product,
           'product_id': line.product_id,
           'qty': line.qty,
           'uom_name': line.uom,
           'uom_id': line.uom_id,
           'lot_id': line.lot_id,
           'state': line.state,
           'type': this.type,
           'id': false
       });
    }


}
