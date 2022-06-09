import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ModalController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the StockInfoPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
    selector: 'page-stock-info',
    templateUrl: 'stock-info.html',
})
export class StockInfoPage {
    navbarColor: string = 'primary';
    product_id;
    location_id;
    product_name;
    uom_name;
    lots: Object[];
    items: Object[];

    constructor(public navCtrl: NavController, private storage: Storage,
        public navParams: NavParams,
        public modalCtrl: ModalController,
        private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        this.product_id = this.navParams.get('product_id');
        this.location_id = this.navParams.get('location_id');
        this.product_name = this.navParams.get('product_name');
        this.uom_name = this.navParams.get('uom_name');
    }

    ionViewDidLoad() {
        if (this.product_id in this.prodData.lotsByProduct) {
            this.items = this.prodData.lotsByProduct[this.product_id].filter(
                lot_id => lot_id.location_id === this.location_id);
        }
        console.log(this.items)
        console.log(this.prodData.lotsByProduct)
        console.log(this)
    }

}
