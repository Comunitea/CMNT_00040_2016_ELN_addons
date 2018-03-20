import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController } from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the UsersModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-users-modal',
  templateUrl: 'users-modal.html',
})
export class UsersModalPage {

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController,
                private prodData: ProductionProvider) {
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad UsersModalPage');
    }

    closeModal() {
        this.viewCtrl.dismiss();
    }
    setActive(user){
        console.log(user.name);
    }
    logIn(user) {
        console.log(user.name);
    }

}
