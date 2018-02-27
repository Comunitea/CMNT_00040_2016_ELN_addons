import { Component } from '@angular/core';
import { NavController, NavParams, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ProductionPage } from '../../pages/production/production';

declare var OdooApi: any;

@Component({
  selector: 'page-list',
  templateUrl: 'list.html'
})
export class ListPage {
    lines = [];

    constructor(public navCtrl: NavController, private storage: Storage, public alertCtrl: AlertController){
        this.lines = [];
        this.getLines();
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    getLines(){
        this.storage.get('CONEXION').then((con_data) => {
            var odoo = new OdooApi(con_data.url, con_data.db);
            if (con_data == null) {
                this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
            } else {
                odoo.login(con_data.username, con_data.password).then( (uid) => {
                    var domain = [];
                    var fields = ['id', 'name'];
                    odoo.search_read('mrp.workcenter', domain, fields, 0, 0).then((lines) => {
                        this.lines = lines;
                    });
                });
            }
        });
    }
    lineSelected(line) {
        this.presentAlert('Ok!', line.name);
        this.navCtrl.setRoot(ProductionPage, {line:line});
    }


}
