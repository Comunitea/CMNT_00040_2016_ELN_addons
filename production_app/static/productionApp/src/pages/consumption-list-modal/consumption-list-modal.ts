import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController } from 'ionic-angular';
import { Storage } from '@ionic/storage';

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
    navbarColor: string = 'primary';
    allowed_lines: Object[];
    type: string = 'in';

    constructor(public navCtrl: NavController, private storage: Storage,
                public navParams: NavParams,
                public viewCtrl: ViewController) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
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

    add_line(line) {
        let qty = line.qty;
        let scrap_type = 'losses';
        if (this.type !== 'in') {
            qty = 0
        }
        if (this.type !== 'scrapped') {
            scrap_type = ''
        }
        this.viewCtrl.dismiss({
           'product_id': line.product_id,
           'product_name': line.product_name,
           'uom_id': line.uom_id,
           'uom_name': line.uom_name,
           'qty': qty,
           'location_id': line.location_id,
           'location_name': line.location_name,
           'lot_id': line.lot_id,
           'type': this.type,
           'scrap_type': scrap_type,
           'state': line.state,
           'id': false
       });
    }


}
