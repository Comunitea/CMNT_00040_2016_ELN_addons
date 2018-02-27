import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

/**
 * Generated class for the ProductionPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-production',
  templateUrl: 'production.html',
})
export class ProductionPage {

    constructor(public navCtrl: NavController, public navParams: NavParams) {
        // this.exist_line = false;
        this.line = this.navParams.get('line');
        // if (this.line) {
        //     this.exist_line = true;
        // }
    }


}
