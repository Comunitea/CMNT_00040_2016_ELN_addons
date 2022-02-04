import { NavController, NavParams, AlertController } from 'ionic-angular';
import { Component } from '@angular/core';    
import { Storage } from '@ionic/storage';
import { ListPage } from '../../pages/list/list';

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
        company: 'qv',
        username_qv: '',
        password_qv: '',
        username_vq: '',
        password_vq: '',
        mode: 'production',
    };
    CONEXION = {
        url: '',
        db: '',
        username: '',
        password: '',
        company: 'qv',
        username_qv: '',
        password_qv: '',
        username_vq: '',
        password_vq: '',
        mode: 'production',
    };
    cargar = false;
    mensaje = '';

    constructor(public navCtrl: NavController, public navParams: NavParams, 
                private storage: Storage, public alertCtrl: AlertController) {
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

    set_company() {
        if (this.CONEXION.company == 'qv') {
            this.CONEXION.username = this.CONEXION.username_qv;
            this.CONEXION.password = this.CONEXION.password_qv;
        } else {
            this.CONEXION.username = this.CONEXION.username_vq;
            this.CONEXION.password = this.CONEXION.password_vq;
	}
    }

    change_company() {
        if (this.CONEXION.company == 'qv') {
            this.CONEXION.company = 'vq';
        } else {
            this.CONEXION.company = 'qv';
	}
        this.set_company();
    }

    check_storage_conexion(borrar) {
        // Fijamos siempre a false el parámetro borrar para no tener que teclear usuario y contraseña siempre
        borrar = false
        if (borrar) {
            this.CONEXION = this.CONEXION_local;
        } else {
            this.storage.get('CONEXION').then((val) => {
                if (val && val['username']) {
                    this.CONEXION = val
                } else {
                    this.CONEXION = this.CONEXION_local;
                    this.storage.set('CONEXION', this.CONEXION).then(() => {
                    })
                }
            })
        }
        this.set_company();
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    conectarApp(verificar) {
        this.cargar = true;
        this.set_company();
        if (verificar) {
            this.check_conexion(this.CONEXION)
        } else {
            this.storage.get('CONEXION').then((val) => {
                var con;
                if (val == null) {//no existe datos         
                    this.cargar = false;
                    con = this.CONEXION;
                    if (con.username.length < 3 || con.password.length < 3) {
                        if (verificar) {
                            this.presentAlert('¡Alerta!', 'Por favor ingrese usuario y contraseña');
                        }
                        return;
                    }
                } else {
                    //si los trae directamente ya fueron verificados
                    con = val;
                    if (con.username.length < 3 || con.password.length < 3) {
                        this.cargar = false;
                        return
                    }
                }
                if (con) {
                    this.storage.set('CONEXION', con).then(() => {
                        this.check_conexion(con)
                        this.cargar=false
                    })
                }
            })
        }
    }

    check_conexion(con) {	
        var model = 'res.users'
        var domain = [['login', '=', con.username]]
        var fields = ['id', 'login', 'image', 'name', 'company_id']
        var odoo = new OdooApi(con.url, con.db, con.uid, con.password);
        odoo.login(con.username, con.password).then((uid) => {
	    con.uid = uid
            this.storage.set('CONEXION', con).then(() => {
                this.navCtrl.setRoot(ListPage, {mode: con.mode});
            })
            odoo.search_read(model, domain, fields).then((value) => {
                if (value) {
                    if (!con.user || value[0].id != con.user['id'] || value[0].company_id[0] != con.user['company_id']) {
                        con.user = value[0];
			con.uid = value[0].id;
                    }
                    this.storage.set('CONEXION', con).then(() => {
                        this.navCtrl.setRoot(ListPage, {mode: con.mode});
                    })
                }
            })
            .catch(() => {
                this.cargar = false;
                this.presentAlert('¡Error!', 'No se pudo encontrar el usuario: ' + con.username);
            });
        })
        .catch (() => {
            this.presentAlert('¡Error!', 'No se pudo conectar a Odoo');
            this.cargar = false;
        })
    }
}
