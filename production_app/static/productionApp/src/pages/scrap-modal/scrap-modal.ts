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
    ctrl

    constructor(public navCtrl: NavController, public navParams: NavParams,
              public viewCtrl: ViewController,
              private prodData: ProductionProvider) {
        this.qty = 0.0;
        this.uos_qty = 0.0;
        this.ctrl = 'do';
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

    onchange_uom() {
        console.log(this.prodData.uom)
        if (this.ctrl !== 'not do'){
            var uos_coeff = this.prodData.uos_coeff;
            if (uos_coeff == 0){
                uos_coeff = 1
            }
            this.uos_qty = (this.qty / uos_coeff).toFixed(2);
            this.ctrl = 'not do'
        }
        else{
            this.ctrl = 'do'
        }
    }

    onchange_uos() {
        console.log("b")
        if (this.ctrl !== 'not do'){
            this.qty = (this.uos_qty * this.prodData.uos_coeff).toFixed(2);
            this.ctrl = 'not do'
        } 
        else{
            this.ctrl = 'do'
        }  
    }

}
