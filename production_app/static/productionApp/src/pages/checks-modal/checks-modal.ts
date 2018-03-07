import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, AlertController } from 'ionic-angular';
import { HomePage } from '../../pages/home/home';
import { Storage } from '@ionic/storage';

/**
 * Generated class for the ChecksModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

declare var OdooApi: any;

@IonicPage()
@Component({
  selector: 'page-checks-modal',
  templateUrl: 'checks-modal.html',
})
export class ChecksModalPage {
    product_id;
    quality_type;
    quality_checks;

    constructor(public navCtrl: NavController, public navParams: NavParams, public viewCtrl: ViewController, private storage: Storage, public alertCtrl: AlertController) {
        this.product_id = this.navParams.get('product_id');
        this.quality_type = this.navParams.get('quality_type');
        this.getQualityChecks()
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
                    this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
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

    getQualityChecks() {
        var values =  {
            'product_id': this.product_id,
            'quality_type': this.quality_type,
        };
        this.callRegistry('get_quality_checks', values).then( (res) => {
            console.log("LLamados los quality_checks")
            console.log(res)
            if (res) {
                this.quality_checks = res;
            }
        })
        .catch( (err) => {
            console.log(err) 
        });
     }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ChecksModalPage');
    }
    closeModal() {
        this.viewCtrl.dismiss(this.quality_checks);
    }

}
