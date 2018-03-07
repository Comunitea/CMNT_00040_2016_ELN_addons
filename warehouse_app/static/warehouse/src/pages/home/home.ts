import {NavController, NavParams, AlertController} from 'ionic-angular';
import {Component} from '@angular/core';
import {Network} from '@ionic-native/network';
import {Storage} from '@ionic/storage';

import {TreepickPage} from '../../pages/treepick/treepick'; 
/*import {PROXY} from '../../providers/constants/constants';*/
//import  * as odoo from '../../providers/odoo-connector/odoo.js';
import { AuxProvider } from '../../providers/aux/aux'
import { ShowinfoPage } from '../showinfo/showinfo';

declare var OdooApi: any;
@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

  loginData = {password: '', username: ''};
  CONEXION = {

      url: 'http://odoopistola.com',
      port: '80',
      db: 'pistola',
      username: 'admin',
      password: 'admin',

  };
  /*CONEXION = {
    url: 'http://elnapp.livingodoo.com',
    port: '80',
    db: 'elnapp',
    username: 'admin',
    password: 'admin',
};*/
  cargar = true;
  mensaje = '';


  constructor(public navCtrl: NavController, public navParams: NavParams, private storage: Storage, public alertCtrl: AlertController, private network: Network, public auxProvider: AuxProvider) {

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

                  self.navCtrl.setRoot(HomePage);
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
                      self.storage.set('CONEXION', con);
                      user.id = value[0].id;
                      user.name = value[0].name;
                      user.login = value[0].login;
                      self.auxProvider.filter_user='assigned'
                      self.navCtrl.setRoot(TreepickPage); //-> me voy para la home page
                      //self.navCtrl.setRoot(TreepickPage);
                      //self.navCtrl.setRoot(ShowinfoPage)

                  }
                  else {
                      self.cargar = false;
                      return self.presentAlert('Falla!', 'Usuario incorrecto');
                  }
                })
          })
    });
  }
  get_picking_types(){
    var self = this
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
          self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.search_read('stock.picking.type', [['show_in_pda', '=', true]], ['id', 'name', 'short_name'], 0, 0).then(
                function (value) {
                  
                  self.storage.set('stock.picking.type', value);
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
                  self.cargar = false;
              }
          });
      

  }  
  getObjectId(values){
    var self = this;
    var object_id = {}

    var model = 'warehouse.app'
    var method = 'get_object_id'

    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.call(model, method, values).then(
                function (value) {
                  object_id = value;
                  self.cargar = false;
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
                  self.cargar = false;


              }
              return object_id

          });


        }

}
