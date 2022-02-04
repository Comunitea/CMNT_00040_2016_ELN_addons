import { Component } from '@angular/core';    
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the NoteModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
    selector: 'page-note-modal',
    templateUrl: 'note-modal.html'
})
export class NoteModalPage {
    note: string;
    navbarColor: string = 'primary';

    constructor(public navCtrl: NavController, private storage: Storage,
        public navParams: NavParams,
        public viewCtrl: ViewController,
        public alertCtrl: AlertController,
        private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
	this.note = this.prodData.note;
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad NoteModalPage');
    }

    closeModal() {
        this.viewCtrl.dismiss(0);
    }

    confirm() {
        var res = {};
        res['note'] = this.note
        this.viewCtrl.dismiss(res);
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }


}
