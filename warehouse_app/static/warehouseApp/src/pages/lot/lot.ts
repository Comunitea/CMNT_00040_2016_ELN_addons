import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
//import { ViewChild } from '@angular/core';
//import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
//import { HostListener } from '@angular/core';
import { Storage } from '@ionic/storage';

//*Pagians
import { HomePage } from '../home/home';
//import { LotPage } from '../lot/lot';
import { LocationPage } from '../location/location';
import { ProductPage } from '../product/product';

/**
 * Generated class for the ProductPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

declare var OdooApi: any

@IonicPage()
@Component({
    selector: 'page-lot',
    templateUrl: 'lot.html',
})

export class LotPage {
    model
    id
    item
    cargar
    constructor(public navCtrl: NavController, public toastCtrl: ToastController, public storage: Storage, public navParams: NavParams, public alertCtrl: AlertController) {
        this.model = this.navParams.data.model;
        this.id = this.navParams.data.id;
        this.item = []
        this.cargar = false
        this.loaditem()
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad LotPage');
    }

    loaditem() {
        var self = this
        var model = 'warehouse.app'
        var method = 'get_info_object'
        var values = { 'model': this.model, 'id': this.id };
        self.storage.get('CONEXION_WH').then((val) => {
            if (val == null) {
                console.log('No hay conexión');
                self.navCtrl.setRoot(HomePage, { borrar: true, login: null });
            } else {
                console.log('Hay conexión');
                var con = val;
                var odoo = new OdooApi(con.url, con.db, con.uid, con.password);
                odoo.login(con.username, con.password).then(
                    function (uid) {
                        odoo.call(model, method, values).then(
                            function (value) {
                                self.cargar = Boolean(value['id'])
                                self.item = value['values']
                                console.log(self.item)
                                //AQUI DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO
                                //self.openinfo(value)
                            },
                            function () {
                                self.presentAlert('TODO!', 'DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO');
                            }
                        );
                    },
                    function () {

                        self.presentAlert('Falla!', 'Imposible conectarse');
                    }
                );
            }
        });
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    open(model, id) {
        var page
        switch (model) {
            case 'stock.production.lot':
                page = LotPage;
                break
            case 'stock.location':
                page = LocationPage;
                break
            case 'product.product':
                page = ProductPage;
                break
        }
        if (page && id) {
            this.navCtrl.push(page, { model: model, id: id });
        }
    }

}
