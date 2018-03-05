import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';

/**
 * Generated class for the ProductionPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

declare var OdooApi: any;

@IonicPage()
@Component({
  selector: 'page-production',
  templateUrl: 'production.html',
})
export class ProductionPage {
 
    constructor(public navCtrl: NavController, private storage: Storage, public navParams: NavParams, public alertCtrl: AlertController) {
        this.workcenter = false // avoid fail next line for not declared
        this.workcenter = this.navParams.get('workcenter_id')[1];
        this.registry_id = this.navParams.get('id');
        this.state = this.navParams.get('state');
        this.states = {
            'waiting': 'ESPERANDO PRODUCCIÖN',
            'confirmed': 'PRODUCCIÓN CONFIRMADA',
            'setup': 'PREPARACIÓN PRODUCCION',
            'started': 'PRODUCCIÓN INICIADA',
            'stoped': 'PRODUCCIÓN PARADA',
            'cleaning': 'PRODUCCIÓN EN LIMPIEZA',
            'finished': 'PRODUCCIÓN FINALIZADA'
        };
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

    beginLogistics() {
        this.presentAlert('Logistica', 'PENDIENTE DESAROLLO')
    }

    confirmProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('confirm_production', values).then( (res) => {
            console.log("PRODUCCIÓN CONFIRMADA:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
     }
    setupProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('setup_production', values).then( (res) => {
            console.log("PRODUCCIÓN EN PREPARACIÖN:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    startProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('start_production', values).then( (res) => {
            console.log("PRODUCCIÓN EMPEZADA:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    cleanProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('clean_production', values).then( (res) => {
            console.log("PRODUCCIÓN EN LIMPIEZA:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    finishProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('finish_production', values).then( (res) => {
            console.log("PRODUCCIÓN FINALIZADA:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    stopProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('stop_production', values).then( (res) => {
            console.log("PRODUCCIÓN PARADA:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    restartProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('restart_production', values).then( (res) => {
            console.log("PRODUCCIÓN REINICIADA:") 
            this.state = res.state;
        })
        .catch( (err) => {
            console.log(err) 
        });
    }


}
