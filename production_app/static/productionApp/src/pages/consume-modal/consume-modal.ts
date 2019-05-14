import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController} from 'ionic-angular';
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
    line;
    lots: Object[];
    items: Object[];

    mode: string = 'default';

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                private prodData: ProductionProvider) {
        this.line = this.navParams.get('line');
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ConsumeModalPage');
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    showLots(){
        this.mode = 'show'
        if (this.line.product_id in this.prodData.lotsByProduct){
            this.lots = this.prodData.lotsByProduct[this.line.product_id]
            this.items = this.prodData.lotsByProduct[this.line.product_id]
        }
    }
    lotSelected(lot_obj){
        this.mode = 'default';
        this.line.lot_name = lot_obj.name
        this.line.lot_id = lot_obj.id
    }

    getItems(ev: any) {
        // Reset items back to all of the items
       this.items = this.prodData.lotsByProduct[this.prodData.product_id]

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                return (item['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }

    confirmModal() {
        this.viewCtrl.dismiss(this.line);
    }


    closeModal() {
        this.viewCtrl.dismiss([]);
    }

}
