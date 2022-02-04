import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';
import { OdooProvider } from '../../providers/odoo/odoo';

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
    navbarColor: string = 'primary';
    searchQuery: string = '';
    items: Object[];
    items2: Object[] = [];
    mode: string = 'out';

    constructor(public navCtrl: NavController, private storage: Storage,
                public navParams: NavParams,
                public viewCtrl: ViewController,
                private prodData: ProductionProvider,
                public alertCtrl: AlertController,
                private odooCon: OdooProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        this.initializeItems();
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad UsersModalPage');
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok'],
        });
        alert.present();
    }

    closeModal() {
        this.viewCtrl.dismiss();
    }

    setActive(operator) {
        if (!operator.let_active) {
            this.presentAlert('¡Error!', 'No se puede activar este usuario ya que no está en el listado de operarios del centro de trabajo asociado.')
        } else {
            this.prodData.setActiveOperator(operator.id);
        }
    }

    logInOperator(operator) {
        if (this.items2.length === 0) {
            this.setActive(operator);
        }

        this.prodData.logInOperator(operator.id);

        // Remove from logged out list
        this.items = this.items.filter(obj => obj['id'] !== operator.id);

        // Push to logged in list
        this.items2.push(operator);
    }

    logOutOperator(operator) {
        this.prodData.logOutOperator(operator.id);

        // Remove from logged in list
        this.items2 = this.items2.filter(obj => obj['id'] !== operator.id);

        // Push to logged out list
        this.items.push(operator);
    }

    initializeItems() {
        this.items = this.prodData.operators.filter(obj => this.odooCon.operatorsById[obj.id]['log'] == 'out');
        this.items2 = this.prodData.operators.filter(obj => this.odooCon.operatorsById[obj.id]['log'] == 'in');
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

    getLoggedOut() {
        return this.items;
    }

    getLoggedIn() {
        return this.items2;
    }

}
