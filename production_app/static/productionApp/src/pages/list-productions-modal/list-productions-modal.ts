import { Component } from '@angular/core';    
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the ListProductionsModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
    selector: 'page-list-productions-modal',
    templateUrl: 'list-productions-modal.html'
})
export class ListProductionsModalPage {
    items: Object[];
    workcenter_name = '';
    mode = '';
    navbarColor: string = 'primary';

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController, private storage: Storage,
		public alertCtrl: AlertController,
                private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.mode = con_data.mode;
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
	this.items = this.prodData.worklines;
        this.workcenter_name = this.prodData.workcenter['name'];
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ListProductionsModalPage');
    }

    closeModal() {
        this.viewCtrl.dismiss(0);
    }

    worklineSelected(workline) {
        this.viewCtrl.dismiss(workline);
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            enableBackdropDismiss: false,
            buttons: ['Ok']
        });
        alert.present();
    }

    initializeItems() {
	this.items = this.prodData.worklines;
    }

    getItems(ev: any) {
        // Reset items back to all of the items
        this.initializeItems();

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                let item_name = item['production_id'][1] + '-->' + item['name']
                return (item_name.toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }

}
