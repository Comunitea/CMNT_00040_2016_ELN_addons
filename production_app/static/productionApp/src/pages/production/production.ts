import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ChecksModalPage } from '../../pages/checks-modal/checks-modal';

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
    workcenter;
    registry_id;
    production;
    product;
    product_id;
    state;
    states;
    last_stop_id;
    constructor(public navCtrl: NavController, private storage: Storage, 
                public navParams: NavParams, public alertCtrl: AlertController, 
                public modalCtrl: ModalController) {
        this.workcenter = this.navParams.get('workcenter_id')[1];
        this.registry_id = this.navParams.get('id');
        this.production = this.navParams.get('production_id')[1];
        this.product_id = this.navParams.get('product_id')[0];
        this.product = this.navParams.get('product_id')[1];
        this.state = this.navParams.get('state');
        this.last_stop_id = false;
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
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
     }
    setupProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('setup_production', values).then( (res) => {
            console.log("PRODUCCIÓN EN PREPARACIÖN:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    startProduction() {
        this.openModal();
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('start_production', values).then( (res) => {
            console.log("PRODUCCIÓN EMPEZADA:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    cleanProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('clean_production', values).then( (res) => {
            console.log("PRODUCCIÓN EN LIMPIEZA:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    finishProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('finish_production', values).then( (res) => {
            console.log("PRODUCCIÓN FINALIZADA:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    stopProduction() {
        var values =  {'registry_id': this.registry_id};
        this.callRegistry('stop_production', values).then( (res) => {
            console.log("PRODUCCIÓN PARADA:") 
            if (res) {
                this.state = res['state'];
                this.last_stop_id = res['stop_id']
            }
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    restartProduction() {
        var values =  {
            'registry_id': this.registry_id,
            'stop_id': this.last_stop_id
        }
        this.callRegistry('restart_production', values).then( (res) => {
            console.log("PRODUCCIÓN REINICIADA:") 
            if (res) {
                this.state = res['state'];
                this.last_stop_id = false
            }
        })
        .catch( (err) => {
            console.log(err) 
        });
    }

    openModal() {
        var mydata = {
            'product_id': this.product_id,
            'quality_type': 'start'
        }
        let myModal = this.modalCtrl.create(ChecksModalPage, mydata);
        myModal.onDidDismiss(data => {
            this.saveQualityChecks(data);
        });

        myModal.present();
    }

    saveQualityChecks(data){
        console.log("RESULTADO A GUARDAR")
        console.log(data)
        var values = {
            'registry_id': this.registry_id,
            'lines': data
        }
        this.callRegistry('app_save_quality_checks', values).then( (res) => {
            console.log("RESULTADO GUARDADO") 
        })
        .catch( (err) => {
            console.log("Error al guardar Quality Checks") 
        });
    }


}
