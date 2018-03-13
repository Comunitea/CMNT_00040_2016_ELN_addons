import { Component } from '@angular/core';
import { NavController, NavParams, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ProductionPage } from '../../pages/production/production';
import { ProductionProvider } from '../../providers/production/production';

declare var OdooApi: any;

@Component({
  selector: 'page-list',
  templateUrl: 'list.html'
})
export class ListPage {
    workcenters = []

    constructor(public navCtrl: NavController, private storage: Storage, 
                public alertCtrl: AlertController, 
                private prodData: ProductionProvider){
        this.workcenters = [];
        this.getLines();
    }

    logOut(){
        let confirm = this.alertCtrl.create({
          title: 'Salir de la Aplicación?',
          message: 'Estás seguro que deseas salir de la aplicación?',
          buttons: [
            {
              text: 'No',
              handler: () => {
                console.log('Disagree clicked');
              }
            },
            {
              text: 'Si',
              handler: () => {
                this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
              }
            }
          ]
        });
        confirm.present();
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
                odoo.login(con_data.username, con_data.password).then(
                    (uid) => {
                        var model = 'app.registry'
                        var method = 'app_get_registry'
                        var values = {'workcenter_id': workcenter.id}
                        odoo.call(model, method, values).then(
                            (reg) => {
                                console.log(reg)
                                if (reg.id) {
                                    // Init data in provider, so can serve to production page
                                    this.prodData.initData(reg);
                                    this.navCtrl.setRoot(ProductionPage);
                                }
                                else{
                                    this.presentAlert('Aviso!', 'No hay órdenes de trabajo planificadas');
                                }
                            },
                            () => {
                                console.log('ERROR EN METHODO app_get_registry DE app.regustry:')
                                this.presentAlert('Falla!', 'Ocurrio un error al obtener el registro de la aplicación');
                            }
                        );
                    },
                )
                .catch( () => {
                    this.presentAlert('Error!', 'No se pudo conectar contra odoo');
                });
            }
        });
    }
}
