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

    searchQuery: string = '';
    items: Object[];
    items2: Object[] = [];
    mode: string = 'out';

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController,
                private prodData: ProductionProvider) {
        this.initializeItems();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad UsersModalPage');
    }

    closeModal() {
        this.viewCtrl.dismiss();
    }
    setActive(operator){
        this.prodData.setActiveOperator(operator.id);
    }
    logInOperator(operator) {
        this.prodData.logInOperator(operator.id);

        //Remove from loged out list
        this.items = this.items.filter(obj => obj['id'] !== operator.id);

        // Push to loged in list
        this.items2.push(operator);
    }
    logOutOperator(operator) {
        this.prodData.logOutOperator(operator.id);

        //Remove from loged in list
        this.items2 = this.items2.filter(obj => obj['id'] !== operator.id);

        // Push to loged out list
        this.items.push(operator);


    }
    initializeItems() {
        this.items = this.prodData.operators.filter(obj => this.prodData.operatorsById[obj.id]['log'] == 'out');
        this.items2 = this.prodData.operators.filter(obj => this.prodData.operatorsById[obj.id]['log'] == 'in');
    }
    getItems(ev: any) {
        // Reset items back to all of the items
        this.initializeItems();

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                if ('name' in item)
                    return (item['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }
    getLogedOut() {
        return this.items;
    }
    getLogedIn() {
        return this.items2;
    }


}
