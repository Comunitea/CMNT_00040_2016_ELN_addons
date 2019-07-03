import { Component } from '@angular/core';
import { NavController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ListProductionsPage } from '../../pages/list-productions/list-productions';
import { ProductionPage } from '../../pages/production/production';
import { ProductionProvider } from '../../providers/production/production';

declare var OdooApi: any;

@Component({
  selector: 'page-list',
  templateUrl: 'list.html'
})
export class ListPage {
    workcenters = []
    searchQuery: string = '';
    mode = '';
    items: Object[];

    constructor(public navCtrl: NavController, private storage: Storage, 
                public alertCtrl: AlertController, 
                private prodData: ProductionProvider) {
        this.workcenters = [];
        this.items = [];
        this.storage.get('CONEXION').then((con_data) => {
            this.mode = con_data.mode
        })
        this.getLines();
    }

    logOut() {
        let confirm = this.alertCtrl.create({
          title: '¿Salir de la aplicación?',
          message: '¿Seguro que deseas salir de la aplicación?',
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

    getLines() {
        this.storage.get('CONEXION').then((con_data) => {
            var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
            if (con_data == null) {
                console.log('No hay conexión');
                this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
            } else {
                var domain = [];
                var fields = ['id', 'name'];
                odoo.search_read('mrp.workcenter', domain, fields, 0, 0).then((workcenters) => {
                    this.workcenters = workcenters;
                    this.initializeItems();
                });
            }
        });
    }

    workcenterSelected(workcenter) {
        var vals = {'workcenter_id': workcenter.id}
        if (this.mode == 'alimentator') {
            this.navCtrl.push(ListProductionsPage, {workcenter_id: workcenter.id, workcenter_name: workcenter.name});
        } else {
            this.prodData.loadProduction(vals).then( (res) => {
                this.prodData.getStopReasons(workcenter.id).then( (res) => {
                    this.navCtrl.setRoot(ProductionPage);
                })
                .catch( (err) => {
                    this.presentAlert("Error", "Fallo al cargar los motivos técnicos para el centro de trabajo actual.");
                }); 
            })
            .catch( (err) => {
                this.presentAlert(err.title, err.msg);
            }); 
            }
    }

    initializeItems() {
        this.items = this.workcenters
    }

    getItems(ev: any) {
        // Reset items back to all of the items
        this.initializeItems();

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                return (item['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }
}
