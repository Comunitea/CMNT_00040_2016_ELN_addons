import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ChecksModalPage } from '../../pages/checks-modal/checks-modal';
import { OdooProvider } from '../../providers/odoo/odoo';


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
    cdb;
    weight;
    constructor(public navCtrl: NavController, private storage: Storage, 
                public navParams: NavParams, public alertCtrl: AlertController, 
                public modalCtrl: ModalController,
                private odooCon: OdooProvider) {
        this.workcenter = this.navParams.get('workcenter_id')[1];
        this.registry_id = this.navParams.get('id');
        this.production = this.navParams.get('production_id')[1];
        this.product_id = this.navParams.get('product_id')[0];
        this.product = this.navParams.get('product_id')[1];
        this.state = this.navParams.get('state');
        this.last_stop_id = false;
        this.states = {
            'waiting': 'ESPERANDO PRODUCCIÓN',
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
    

    beginLogistics() {
        this.presentAlert('Logistica', 'PENDIENTE DESAROLLO')
    }

    confirmProduction() {
        var values =  {'registry_id': this.registry_id};
        this.odooCon.callRegistry('confirm_production', values).then( (res) => {
            console.log("PRODUCCIÓN CONFIRMADA:")
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
     }
    setupProduction() {
        var values =  {'registry_id': this.registry_id};
        this.odooCon.callRegistry('setup_production', values).then( (res) => {
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
        this.odooCon.callRegistry('start_production', values).then( (res) => {
            console.log("PRODUCCIÓN EMPEZADA:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    cleanProduction() {
        var values =  {'registry_id': this.registry_id};
        this.odooCon.callRegistry('clean_production', values).then( (res) => {
            console.log("PRODUCCIÓN EN LIMPIEZA:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    promptFinishData() {
        let alert = this.alertCtrl.create({
            title: 'Finalizar Producción',
            inputs: [
              {
                name: 'cdb',
                placeholder: 'CdB'
              },
              {
                name: 'weight',
                placeholder: 'Weight',
                type: 'numeric'
              }
            ],
            buttons: [
              {
                text: 'Cancel',
                role: 'cancel',
                handler: data => {
                  console.log('Cancel clicked');
                }
              },
              {
                text: 'OK',
                handler: data => {
                  this.cdb = data.cdb;
                  this.weight = data.weight;
                  this.writeFinishProductionData();
                }
              }
            ]
        });
        alert.present();
    }
    finishProduction() {
        this.promptFinishData();
    }
    writeFinishProductionData() {
        var values =  {'registry_id': this.registry_id, 
                       'cdb': this.cdb, 
                       'weight': this.weight};
        this.odooCon.callRegistry('finish_production', values).then( (res) => {
            console.log("PRODUCCIÓN FINALIZADA:") 
            this.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });
    }
    stopProduction() {
        var values =  {'registry_id': this.registry_id};
        this.odooCon.callRegistry('stop_production', values).then( (res) => {
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
        this.odooCon.callRegistry('restart_production', values).then( (res) => {
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
        this.odooCon.callRegistry('app_save_quality_checks', values).then( (res) => {
            console.log("RESULTADO GUARDADO") 
        })
        .catch( (err) => {
            console.log("Error al guardar Quality Checks") 
        });
    }


}
