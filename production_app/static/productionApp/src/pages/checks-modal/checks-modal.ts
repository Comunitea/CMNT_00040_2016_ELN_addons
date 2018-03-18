import { Component } from '@angular/core';
import { IonicPage,  NavParams, ViewController} from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ChecksModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */


@IonicPage()
@Component({
  selector: 'page-checks-modal',
  templateUrl: 'checks-modal.html',
})
export class ChecksModalPage {
    product_id;
    quality_type;
    quality_checks;

    constructor(public navParams: NavParams, public viewCtrl: ViewController, 
                private prodData: ProductionProvider) {
        this.product_id = this.navParams.get('product_id');
        this.quality_type = this.navParams.get('quality_type');
        this.quality_checks = this.navParams.get('quality_checks');
    }
     
    ionViewDidLoad() {
        console.log('ionViewDidLoad ChecksModalPage');
    }
    closeModal() {
        this.viewCtrl.dismiss(this.quality_checks);
    }

}
