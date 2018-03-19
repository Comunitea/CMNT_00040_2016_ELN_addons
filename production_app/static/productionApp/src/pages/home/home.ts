import {NavController, NavParams, AlertController} from 'ionic-angular';
import {Component} from '@angular/core';    

import {Storage} from '@ionic/storage';
import {ListPage} from '../../pages/list/list';
import { ProductionProvider } from '../../providers/production/production';



declare var OdooApi: any;
@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})

export class HomePage {

    loginData = {password: '', username: ''};
    CONEXION = {
        url: 'http://nogalproduction.com',
        port: '9069',
        db: 'nogal_dev',
        username: 'admin',
        password: 'admin',
    };
    cargar = true;
    mensaje = '';
  
    constructor(public navCtrl: NavController, public navParams: NavParams, 
                private storage: Storage, public alertCtrl: AlertController,
                private prodData: ProductionProvider) {
    
        var borrar = this.navParams.get('borrar');
        this.CONEXION.username = (this.navParams.get('login') == undefined)? '' : this.navParams.get('login');
            if (borrar == true) {
                this.cargar = false;
                this.storage.remove('CONEXION');
            } else {
                this.conectarApp(false);
            }
    } 
        
    loginSinDatos() {
        var self = this;
        this.storage.get('res.users').then((val) => {
            if (val == null) {//no existe datos
                self.presentAlert('Falla!', 'Imposible conectarse');
            } else {
                self.navCtrl.setRoot(ListPage);
            }
            self.cargar = false;
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
  
    conectarApp(verificar) {
        var self = this;


        var con;
        con = self.CONEXION;
        this.storage.get('CONEXION').then((val) => {
        var con;
        if (val == null) {//no existe datos         
            self.cargar = false;
            con = self.CONEXION;
            if (con.username.length < 3 || con.password.length < 3) {
                if (verificar) {
                    self.presentAlert('Alerta!', 'Por favor ingrese usuario y contraseña');
                }
            return;
        }

        } else {
        //si los trae directamente ya fueron verificados
        con = val;
        if (con.username.length < 3 || con.password.length < 3) {
            return self.cargar = false;
        }
    }

    self.cargar = true;
    //var odoo = new Odoo(con);
    var odoo = new OdooApi(con.url, con.db);
    odoo.login(con.username, con.password).then(
        function (uid) {
            odoo.search('res.users', [['login', '=', con.username]], ['id', 'login', 'image', 'name']).then(
                function (value) {
            
                    var user = {id: null, name: null, image: null, login: null, cliente_id: null};
                    //self.mensaje += JSON.stringify(value);
                    if (value.length > 0) {
                        self.storage.set('CONEXION', con).then(() => {
                            user.id = value[0].id;
                            user.name = value[0].name;
                            user.login = value[0].login;
                            self.prodData.getUsers(user);
                            self.prodData.getStopReasons();
                            //todo debería ser una promesa?
                            // me voy para página de producción
                            self.navCtrl.setRoot(ListPage); 
                        })
                        

                    } 
                    else {
                        self.cargar = false;
                        return self.presentAlert('Falla!', 'Usuario incorrecto');
                    } 
                })
          })
            .catch( () => {
                this.presentAlert('Error!', 'No se pudo conectar contra odoo');
                // TODO DESARROLLAR UN RETRY
            });
    });
  }

}
