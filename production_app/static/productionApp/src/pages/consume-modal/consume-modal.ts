import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController } from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ConsumeModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
      selector: 'page-consume-modal',
      templateUrl: 'consume-modal.html',
})
export class ConsumeModalPage {

    lot: string;
    lots: Object[];
    items: Object[];

    constructor(public navCtrl: NavController, public navParams: NavParams, 
                public viewCtrl: ViewController,
                private prodData: ProductionProvider) {
        this.lots = [];
        this.items = [];
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ConsumeModalPage');
        this.lots = this.prodData.lotsByProduct[this.prodData.consume_product_id]
        this.items = this.prodData.lotsByProduct[this.prodData.consume_product_id]
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

    confirm() {
        var res = {
            'id': this.prodData.change_lot_qc_id,
            'max_value': 0,
            'min_value': 0,
            'name': 'Cambio de lote',
            'quality_type': 'freq',
            'repeat': 0,
            'required_text': false,
            'value': this.lot,
            'value_type': 'text'

        }
        console.log("res");
        console.log(res);
        this.viewCtrl.dismiss(res);
    }

    lotSelected(lot_obj){
        this.lot = lot_obj.name
    }
    getItems(ev: any) {
        // Reset items back to all of the items
       this.items = this.prodData.lotsByProduct[this.prodData.consume_product_id]

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                return (item['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }

}
