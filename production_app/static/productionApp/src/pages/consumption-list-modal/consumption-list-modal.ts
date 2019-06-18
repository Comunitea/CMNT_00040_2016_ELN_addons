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
           'product_id': line.product_id,
           'product_name': line.product_name,
           'uom_id': line.uom_id,
           'uom_name': line.uom_name,
           'qty': line.qty,
           'location_id': line.location_id,
           'location_name': line.location_name,
           'lot_id': line.lot_id,
           'type': this.type,
           'state': line.state,
           'id': false
       });
    }


}
