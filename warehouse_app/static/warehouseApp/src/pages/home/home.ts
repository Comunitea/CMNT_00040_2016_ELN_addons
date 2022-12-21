import { NavController, NavParams, AlertController } from 'ionic-angular';
import { Component } from '@angular/core';
import { Storage } from '@ionic/storage';
import { TreepickPage } from '../../pages/treepick/treepick';
//import { AuxProvider } from '../../providers/aux/aux';
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';

declare var OdooApi: any;

@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})

export class HomePage {
    CONEXION_local = {
        url: 'http://',
        db: '',
        username: '',
        password: '',
        user: {},
    };
    CONEXION = {
        url: '',
        db: '',
        username: '',
        password: '',
        user: {},
    }

    cargar = false;
    mensaje = '';
    login_server: boolean = false

    constructor(public navCtrl: NavController, public navParams: NavParams,
        private storage: Storage, public alertCtrl: AlertController,
        private odoo: OdooProvider) {

        this.login_server = false
        if (this.navParams.get('login')) {
            this.CONEXION.username = this.navParams.get('login')
        };

        this.check_storage_conexion(this.navParams.get('borrar'))
        if (this.navParams.get('borrar') == true) {
            this.cargar = false;
        } else {
            // Autologin al cargar app
            this.cargar = true;
            this.conectarApp(false);
        }
    }

    check_storage_conexion(borrar) {
        borrar = borrar || false
        // Fijamos siempre a false el parámetro borrar para no tener que teclear usuario y contraseña siempre
        borrar = false
        if (borrar) {
            this.storage.clear()
            this.CONEXION = this.CONEXION_local;
        } else {
            this.storage.get('CONEXION_WH').then((val) => {
                if (val && val['username']) {
                    this.CONEXION = val
                } else {
                    this.CONEXION = this.CONEXION_local;
                    this.storage.set('CONEXION_WH', this.CONEXION).then(() => {
                    })
                }
            })
        }
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

    conectarApp(verificar) {
        this.cargar = true;
        if (verificar) {
            this.storage.set('CONEXION_WH', this.CONEXION).then(() => {
                this.check_conexion(this.CONEXION)
            })
        } else {
            this.storage.get('CONEXION_WH').then((val) => {
                var con;
                if (val == null) {
                    con = this.CONEXION;
                    this.storage.set('CONEXION_WH', con).then(() => {
                        this.check_conexion(con)
                        this.cargar = false
                    })
                } else {
                    con = val;
                    this.check_conexion(con)
                    this.cargar = false
                }
            })
        }
    }

    check_conexion(con) {
        var model = 'res.users'
        var domain = [['login', '=', con.username]]
        var fields = ['id', 'login', 'image', 'name', 'company_id']
        this.odoo.login(con.username, con.password).then((uid) => {
            this.odoo.uid = uid
            con.uid = uid
            this.storage.set('CONEXION_WH', con).then(() => {
                this.odoo.searchRead(model, domain, fields).then((value) => {
                    if (value) {
                        if (!con.user || value[0].id != con.user['id'] || value[0].company_id[0] != con.user['company_id']) {
                            con.user = value[0];
                            con.uid = value[0].id;
                        }
                        this.storage.set('CONEXION_WH', con).then(() => {
                            this.navCtrl.setRoot(TreepickPage);
                        })
                    }
                })
                    .catch(() => {
                        this.cargar = false;
                        this.presentAlert('Error!', 'No se pudo encontrar el usuario:' + con.username);
                    })
            })
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo conectar a Odoo');
                this.cargar = false;
            })
    }

    check_conexion_2(con) { // esta es como funciona en production_app
        var model = 'res.users'
        var domain = [['login', '=', con.username]]
        var fields = ['id', 'login', 'image', 'name', 'company_id']
        var odoo = new OdooApi(con.url, con.db, con.uid, con.password);
        odoo.login(con.username, con.password).then((uid) => {
            con.uid = uid
            this.storage.set('CONEXION_WH', con).then(() => {
                this.navCtrl.setRoot(TreepickPage);
            })
            odoo.search_read(model, domain, fields).then((value) => {
                if (value) {
                    if (!con.user || value[0].id != con.user['id'] || value[0].company_id[0] != con.user['company_id']) {
                        con.user = value[0];
                        con.uid = value[0].id;
                    }
                    this.storage.set('CONEXION_WH', con).then(() => {
                        this.navCtrl.setRoot(TreepickPage);
                    })
                }
            })
                .catch(() => {
                    this.cargar = false;
                    this.presentAlert('¡Error!', 'No se pudo encontrar el usuario: ' + con.username);
                });
        })
            .catch(() => {
                this.presentAlert('¡Error!', 'No se pudo conectar a Odoo');
                this.cargar = false;
            })
    }
}
