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
    workcenters = []
    selected_workcenter = false;

    constructor(public navCtrl: NavController, private storage: Storage, public alertCtrl: AlertController){
        this.workcenters = [];
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
                console.log('No hay conexión');
                this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
            } else {
                odoo.login(con_data.username, con_data.password).then( (uid) => {
                    var domain = [];
                    var fields = ['id', 'name'];
                    odoo.search_read('mrp.workcenter', domain, fields, 0, 0).then((workcenters) => {
                        this.workcenters = workcenters;
                    });
                });
            }
        });
    }
    workcenterSelected(workcenter) {
        this.loadProduction(workcenter)
        
    }
    loadProduction(workcenter) {
        this.storage.set('workcenter', workcenter);
        this.storage.get('CONEXION').then((con_data) => {
            var odoo = new OdooApi(con_data.url, con_data.db);
            if (con_data == null) {
                console.log('No hay conexión');
                this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
            } else {
                odoo.login(con_data.username, con_data.password).then( (uid) => {
                    var model = 'app.registry'
                    var method = 'app_get_registry'
                    var values = {'workcenter_id': workcenter.id}
                    odoo.call(model, method, values).then(
                        (reg) => {
                        console.log(reg)
                        this.navCtrl.setRoot(ProductionPage, reg);
                        },
                        () => {
                            console.log('ERROR EN METHODO app_get_registry DE app.regustry:')
                            this.presentAlert('Falla!', 'Ocurrio un error al obtener el registro de la aplicación');
                        }
                    );
                });
            }
        });
    }
}
