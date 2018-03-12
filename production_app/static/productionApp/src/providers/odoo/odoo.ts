import { Injectable } from '@angular/core';
import { AlertController} from 'ionic-angular';
import { Storage } from '@ionic/storage';

/*
  Generated class for the OdooProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
declare var OdooApi: any;

@Injectable()
export class OdooProvider {

    constructor(private storage: Storage,  public alertCtrl: AlertController) {
        console.log('Hello OdooProvider Provider');
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    callRegistry(method, values) {
        var method = method
        var values = values
        var promise = new Promise( (resolve, reject) => {
            this.storage.get('CONEXION').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db);
                if (con_data == null) {
                    console.log('No hay conexión');
                    // this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
                } else {
                    odoo.login(con_data.username, con_data.password).then( (uid) => {
                        var model = 'app.registry'
                        // var method = method
                        // var values = values
                        odoo.call(model, method, values).then(
                            (res) => {
                            console.log(res)
                            resolve(res);
                        })
                        .catch( () => {
                            console.log('ERROR en el método ' + method + 'del modelo app.regustry')
                            this.presentAlert('Falla!', 'Ocurrio un error al obtener el registro de la aplicación');
                            reject();
                        });
                    });
                }
            });
        });
        return promise
    }

}
