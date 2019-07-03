import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';


@IonicPage()
@Component({
  selector: 'page-finish-modal',
  templateUrl: 'finish-modal.html',
})
export class FinishModalPage {

    qty = 0;
    uos_qty = 0;
    lot: string;
    date: string;
    lots: Object[];
    items: Object[];
    mode: string = 'default';
    mode_step: string = 'start';
    ctrl: string = 'do';
    allow_zero: boolean = false;

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                private prodData: ProductionProvider) {
        this.lots = [];
        this.items = [];
        this.mode_step = this.navParams.get('mode_step');
        this.date = this.prodData.product_use_date;
        this.ctrl = 'do'
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad FinishModalPage');
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    confirm() {
        var res = {};
        if (this.mode_step === 'clean') {
            if (this.qty == 0 && !this.allow_zero) {
                this.presentAlert("Error", "Es obligatorio indicar una cantidad mayor que 0");
		return;
            };
            if (!isNaN(this.qty) && this.qty >= 0) {
                res['qty'] = +this.qty;
            } else {
                this.presentAlert("Error", "Es obligatorio indicar una cantidad");
                return;
            }
        } else {
            if (isNaN(Date.parse(this.date))) {
                this.presentAlert("Error", "La fecha indicada no es válida");
                return;
            }
            if (!(this.lot)) {
                this.presentAlert("Error", "Es obligatorio indicar un lote");
                return;
            }
            res['lot'] = this.lot
            res['date'] = this.date
        }
        this.viewCtrl.dismiss(res);
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

    showLots() {
        this.mode = 'show'
        if (this.prodData.product_id in this.prodData.lotsByProduct) {
            this.lots = this.prodData.lotsByProduct[this.prodData.product_id]
            this.items = this.prodData.lotsByProduct[this.prodData.product_id]
        }
    }

    lotSelected(lot_obj) {
        this.mode = 'default';
        this.lot = lot_obj.name
        if (lot_obj.use_date) {
            this.date = lot_obj.use_date.split(" ")[0]
        }
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

    onchange_uom() {
        if (this.ctrl !== 'not do') {
            var uos_coeff = this.prodData.uos_coeff;
            this.uos_qty = parseFloat((this.qty * uos_coeff).toFixed(2));
            this.ctrl = 'not do';
        } else {
            this.ctrl = 'do';
        }
    }

    onchange_uos() {
        if (this.ctrl !== 'not do') {
            var uos_coeff = this.prodData.uos_coeff;
            if (uos_coeff == 0) {
                uos_coeff = 1;
            }
            this.qty = parseFloat((this.uos_qty / uos_coeff).toFixed(2))
            this.ctrl = 'not do';
        } else {
            this.ctrl = 'do';
        }  
    }

}
