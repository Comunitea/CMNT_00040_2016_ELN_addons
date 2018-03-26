import { Component, ViewChild } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController } from 'ionic-angular';
import { HomePage } from '../../pages/home/home';
import { ChecksModalPage } from '../../pages/checks-modal/checks-modal';
import { UsersModalPage } from '../../pages/users-modal/users-modal';
import { ReasonsModalPage } from '../../pages/reasons-modal/reasons-modal';
import { OdooProvider } from '../../providers/odoo/odoo';
import { ProductionProvider } from '../../providers/production/production';
import { TimerComponent } from '../../components/timer/timer';


@IonicPage()
@Component({
  selector: 'page-production',
  templateUrl: 'production.html',
})
export class ProductionPage {
    
    cdb;
    weight;
    interval_list: any[] = [];

    @ViewChild(TimerComponent) timer: TimerComponent;

    constructor(public navCtrl: NavController,
                public navParams: NavParams, public alertCtrl: AlertController, 
                public modalCtrl: ModalController,
                private odooCon: OdooProvider, private prodData: ProductionProvider) {
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

    promptNextStep(msg){
        var promise = new Promise( (resolve, reject) => {
            let confirm = this.alertCtrl.create({
              title: 'Confirmar',
              message: msg,
              buttons: [
                {
                  text: 'No',
                  handler: () => {
                    reject();
                  }
                },
                {
                  text: 'Si',
                  handler: () => {
                    resolve();
                  }
                }
              ]
            });
            confirm.present();
        });
        return promise
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    promptFinishData() {
        let alert = this.alertCtrl.create({
            title: 'Finalizar Producción',
            inputs: [
              {
                name: 'qty',
                placeholder: 'Cantidad',
                label: 'Cantidad',
                type: 'number'
              },
              {
                name: 'lot',
                placeholder: 'Lote',
                id: 'Lote',
                type: 'text'
              },
              {
                name: 'date',
                placeholder: 'Fecha caducidad',
                type: 'date'
              },
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
                  this.prodData.qty = data.qty;
                  this.prodData.lot_name = data.lot;
                  this.prodData.lot_date = data.date;
                  this.prodData.finishProduction();
                }
              }
            ]
        });
        alert.present();
    }

    openModal(qtype, qchecks) {
        var mydata = {
            'product_id': this.prodData.product_id,
            'quality_type': qtype,
            'quality_checks': qchecks
        }
        let myModal = this.modalCtrl.create(ChecksModalPage, mydata);

        // When modal closes
        myModal.onDidDismiss(data => {
            this.prodData.saveQualityChecks(data);  // TODO CONVERT IN PROMISE
            if (qtype == 'start'){
                this.timer.restartTimer();  // Production timer on
            } 
        });

        myModal.present();
    }

    openUsersModal(){
        var mydata = {}
        let usersModal = this.modalCtrl.create(UsersModalPage, mydata);
        usersModal.present();
    }

    openReasonsModal(){
        var promise = new Promise( (resolve, reject) => {
            var mydata = {}
            let reasonsModal = this.modalCtrl.create(ReasonsModalPage, mydata);
            reasonsModal.present();

            // When modal closes
            reasonsModal.onDidDismiss(reason_id => {
                if (reason_id == 0){
                    reject(reason_id)
                }
                else{
                    resolve(reason_id);
                }
            });
        });
        return promise;
    }

    clearIntervales(){
        for (let indx in this.interval_list){
            let int = this.interval_list[indx];
            clearInterval(int);
        }
    }

    scheduleIntervals(delay, qchecks){
        let timerId = setInterval(() => 
        {
            this.openModal('freq', qchecks)
        }, delay*60*1000);
        this.interval_list.push(timerId);
    }

    scheduleChecks(){
        var checks_by_delay = {};
        for (let i in this.prodData.freq_checks){
            let qc = this.prodData.freq_checks[i];
            if (!(qc['repeat'] in checks_by_delay)){
                checks_by_delay[qc['repeat']] = [];
            }
            checks_by_delay[qc['repeat']].push(qc) 
        }
        for (let key in checks_by_delay){
            this.scheduleIntervals(key, checks_by_delay[key]);
        }
    }


    
    // ************************************************************************
    // ************************* BUTONS FUNCTIONS *****************************
    // ************************************************************************
    beginLogistics() {
        this.presentAlert('Logistica', 'PENDIENTE DESAROLLO, LLAMAR APP ALMACÉN')
    }

    confirmProduction() {
        this.promptNextStep('Confirmar producción?').then( () => {
            this.prodData.confirmProduction();
        })
        .catch( () => {});
    }

    setupProduction() {
        this.promptNextStep('Empezar preparación?').then( () => {
            this.prodData.setupProduction();
            this.timer.startTimer()  // Set-Up timer on
        })
        .catch( () => {});
    }

    startProduction() {
        this.promptNextStep('Terminar preparación y empezar producción').then( () => {
            this.prodData.startProduction();
            this.openModal('start', this.prodData.start_checks);  // Production timer setted when modal is clos   
            this.scheduleChecks();
        })
        .catch( () => {});
    }

    stopProduction() {
        this.promptNextStep('Registrar una parada?').then( () => {
            this.openReasonsModal().then( (reason_id) => {
                this.clearIntervales();
                console.log("STOP MODAL RES");
                console.log(reason_id);
                this.timer.pauseTimer();
                this.prodData.stopProduction(reason_id);
            })
            .catch( () => {
                console.log("Pues no hago nada")
            })
        })
        .catch( () => {});
    }

    restartAndCleanProduction(){
        this.promptNextStep('Reanudar producción y pasar a limpieza').then( () => {
            this.scheduleChecks();
            this.timer.resumeTimer();
            this.prodData.restartAndCleanProduction();
            this.openModal('start', this.prodData.start_checks);
        })
        .catch( () => {});
    }

    restartProduction() {
        this.promptNextStep('Reanudar producción').then( () => {
            this.scheduleChecks();
            this.timer.resumeTimer();
            this.prodData.restartProduction();
            this.openModal('start', this.prodData.start_checks);
        })
        .catch( () => {});
    }

    cleanProduction() {
        this.promptNextStep('Empezar limpieza?').then( () => {
            this.clearIntervales();
            this.timer.restartTimer();
            this.prodData.cleanProduction();
        })
        .catch( () => {});
    }

    finishProduction() {
        this.promptNextStep('Finalizar producción').then( () => {
            this.timer.pauseTimer()
            this.promptFinishData();
        })
        .catch( () => {});
    }
    loadNextProduction(){
        this.prodData.loadProduction(this.prodData.workcenter).then( (res) => {
        })
        .catch( (err) => {
            this.presentAlert(err.title, err.msg);
        }); 
    }

}
