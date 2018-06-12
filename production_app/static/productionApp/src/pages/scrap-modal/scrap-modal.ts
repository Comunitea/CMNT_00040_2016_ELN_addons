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

    qty;
    uos_qty;
    ctrl;
    reason_id: number;
    reason_name: string;
    reasons: Object[];

    constructor(public navCtrl: NavController, public navParams: NavParams,
              public viewCtrl: ViewController,
              private prodData: ProductionProvider) {
        this.qty = 0.0;
        this.uos_qty = 0.0;
        this.ctrl = 'do';
        this.reason_id=0;
        this.reasons = this.prodData.scrap_reasons;
    }

    ionViewDidLoad() {
    console.log('ionViewDidLoad ScrapModalPage');
    }

    confirm() {
        var res = {};
        res['qty'] = this.qty;
        res['reason_id'] = this.reason_id;
        this.viewCtrl.dismiss(res);
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

    reasonSelected(reason) {
        this.reason_id = reason.id
        this.reason_name = reason.name
    }

    // Diable second unit
    // onchange_uom() {
    //     console.log(this.prodData.uom)
    //     if (this.ctrl !== 'not do'){
    //         var uos_coeff = this.prodData.uos_coeff;
    //         if (uos_coeff == 0){
    //             uos_coeff = 1
    //         }
    //         this.uos_qty = (this.qty / uos_coeff).toFixed(2);
    //         this.ctrl = 'not do'
    //     }
    //     else{
    //         this.ctrl = 'do'
    //     }
    // }

    // onchange_uos() {
    //     console.log("b")
    //     if (this.ctrl !== 'not do'){
    //         this.qty = (this.uos_qty * this.prodData.uos_coeff).toFixed(2);
    //         this.ctrl = 'not do'
    //     } 
    //     else{
    //         this.ctrl = 'do'
    //     }  
    // }

}
