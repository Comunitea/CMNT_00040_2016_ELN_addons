import { Component, ViewChildren, QueryList } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ChecksModalPage } from '../../pages/checks-modal/checks-modal';
import { CalculatorModalPage } from '../../pages/calculator/calculator';
import { UsersModalPage } from '../../pages/users-modal/users-modal';
import { ReasonsModalPage } from '../../pages/reasons-modal/reasons-modal';
import { FinishModalPage } from '../../pages/finish-modal/finish-modal';
import { ScrapModalPage } from '../../pages/scrap-modal/scrap-modal';
import { NoteModalPage } from '../../pages/note-modal/note-modal';
import { ListProductionsModalPage } from '../../pages/list-productions-modal/list-productions-modal';
import { ProductionProvider } from '../../providers/production/production';
import { TimerComponent } from '../../components/timer/timer';
import { ConsumptionsPage } from '../../pages/consumptions/consumptions';


@IonicPage()
@Component({
  selector: 'page-production',
  templateUrl: 'production.html',
})
export class ProductionPage {
    show_create_mo: boolean = true;
    hidden_class: string = 'my-hide';
    navbarColor: string = 'primary';

    @ViewChildren(TimerComponent) timer: QueryList<TimerComponent>;

    constructor(public navCtrl: NavController, private storage: Storage,
                public navParams: NavParams, public alertCtrl: AlertController,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
    }

    ionViewDidLoad() {
        this.initProduction();
    }

    initProduction() {
        this.clearIntervales();
        this.timer.toArray()[0].initTimer();
        this.timer.toArray()[1].initTimer();
        var timer_1_states = ['setup', 'started', 'cleaning']
        if (timer_1_states.indexOf(this.prodData.state) >= 0) {
            if (this.prodData.state == 'started') {
                this.scheduleChecks();
            }
            this.timer.toArray()[0].restartTimer();
        }
        if (this.prodData.state == 'stopped') {
            if (this.prodData.setup_end == true) {
                this.scheduleChecks();
            }
            this.hidden_class = 'none'
            this.timer.toArray()[0].restartTimer();
            this.timer.toArray()[1].restartTimer();
        } else {
            this.hidden_class = 'my-hide'
        }
    }

    logOut() {
        let confirm = this.alertCtrl.create({
          title: '¿Salir de la aplicación?',
          message: '¿Seguro que deseas salir de la aplicación?',
          enableBackdropDismiss: false,
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
                this.clearIntervales();
                this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
              }
            }
          ]
        });
        confirm.present();
    }

    promptNextStep(msg) {
        var promise = new Promise( (resolve, reject) => {
            let confirm = this.alertCtrl.create({
              title: 'Confirmar',
              message: msg,
              enableBackdropDismiss: false,
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
                    if (this.prodData.active_operator_id === 0) {
                        this.presentAlert("¡Error!", "No puede continuar sin un operario activo");
                        reject();
                    }
                    resolve();
                  }
                }
              ]
            });
            confirm.present();
        });
        return promise
    }

    reloadProduction() {
        this.promptNextStep('¿Recargar producción?').then(() => {
            var vals = {'workcenter_id': this.prodData.workcenter['id'],
                        'workline_id': this.prodData.workline[0]}
            this.clearIntervales();
            this.prodData.loadProduction(vals).then((res) => {
                this.initProduction();
            })
            .catch( () => {});
            })
        .catch( () => {});
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

    openChecksModal(qtype, qchecks, restart_timer) {
        var promise = new Promise( (resolve, reject) => {
            var mydata = {
                'product_id': this.prodData.product_id,
                'quality_type': qtype,
                'quality_checks': qchecks
            }
            let myModal = this.modalCtrl.create(ChecksModalPage, mydata);

            // When modal closes
            myModal.onDidDismiss(data => {
                if (data !== null && Object.keys(data).length !== 0) {
                    this.prodData.saveQualityChecks(data);
                    if (qtype == 'start' && restart_timer) {
                        this.timer.toArray()[0].restartTimer();  // Production timer on
                    } 
                    resolve();
                } else {
                    if (qchecks.length === 0) {
                        resolve();
                    } else {
                        reject();
                    };
                }
            });
            myModal.present();
        });
        return promise
    }

    openCalculatorModal() {
        var mydata = {}
        let calculatorModal = this.modalCtrl.create(CalculatorModalPage, mydata);
        calculatorModal.present();
    }

    openUsersModal() {
        var mydata = {}
        let usersModal = this.modalCtrl.create(UsersModalPage, mydata);
        usersModal.present();
    }

    openReasonsModal(type) {
        var promise = new Promise( (resolve, reject) => {
            var mydata = {'type': type}
            let reasonsModal = this.modalCtrl.create(ReasonsModalPage, mydata);
            reasonsModal.present();

            // When modal closes
            reasonsModal.onDidDismiss((res) => {
                if (res === null || res['reason_id'] == 0){
                    reject(res);
                } else {
                    resolve(res);
                }
            });
        });
        return promise;
    }

    openFinishModal(mode_step) {
        var promise = new Promise( (resolve, reject) => {
            var mydata = {'mode_step': mode_step}
            let finishModal = this.modalCtrl.create(FinishModalPage, mydata);
            finishModal.present();

            // When modal closes
            finishModal.onDidDismiss((res) => {
                if (res === null || Object.keys(res).length === 0) {
                    reject();
                } else {
                    if (res.hasOwnProperty('qty')) {
                        this.prodData.qty = res.qty;
                    };
                    if (res.hasOwnProperty('lot')) {
                        this.prodData.product_lot_name = res.lot;
                    };
                    if (res.hasOwnProperty('date')) {
                        this.prodData.product_use_date = res.date;
                    };
                    resolve();
                }
            });
        });
        return promise;
    }

    openScrapModal() {
        var promise = new Promise( (resolve, reject) => {
            let scrapModal = this.modalCtrl.create(ScrapModalPage, {});
            scrapModal.present();

            // When modal closes
            scrapModal.onDidDismiss((res) => {
                if (res === null || Object.keys(res).length === 0) {
                    reject();
                } else {
                    this.prodData.scrap_qty = res.qty;
                    this.prodData.scrap_reason_id = res.reason_id;
                    resolve();
                }
            });
        });
        return promise;
    }

    openListProductionsModal() {
        this.prodData.getWorkcenterLines().then(() => {
            var promise = new Promise( (resolve, reject) => {
                var mydata = {}
                let listProductionsModal = this.modalCtrl.create(ListProductionsModalPage, mydata);
                listProductionsModal.present();

                // When modal closes
                listProductionsModal.onDidDismiss((res) => {
                    if (res !== null && res !== 0) {
                        var vals = {'workcenter_id': res.workcenter_id[0],
                                    'workline_id': res.id}
                        this.clearIntervales();
                        this.prodData.loadProduction(vals).then((reg) => {
                            this.initProduction();
                        })
                        .catch( () => {
                            this.presentAlert("Error", "Error cargando wc_line seleccionado");
                        });
                        resolve();
                    }
                });
            });
            return promise;
        })
        .catch( () => {
            this.presentAlert("Error", "Error cargando wc_lines");
        });
    }

    openNoteModal() {
        var promise = new Promise( (resolve, reject) => {
            var mydata = {}
            let noteModal = this.modalCtrl.create(NoteModalPage, mydata);
            noteModal.present();

            // When modal closes
            noteModal.onDidDismiss((res) => {
                if (res !== null && res !== 0) {
                    if (this.prodData.note !== res.note) {
                        // Solo si ha cambiado el texto lo grabo, para evitar escrituras innecesarias
                        this.prodData.note = res.note
                        resolve();
                    } else {
                        reject();
                    }
                } else {
                    reject();
                }
            });
        });
        return promise;
    }

    clearIntervales() {
        for (let indx in this.prodData.interval_list) {
            let int = this.prodData.interval_list[indx];
            clearInterval(int);
        }
        this.prodData.interval_list = [];
    }

    scheduleIntervals(delay, qchecks) {
        let timerId = setInterval(() => 
        {
            this.openChecksModal('freq', qchecks, false).then(() => {}).catch(() => {});
        }, delay*60*1000);
        this.prodData.interval_list.push(timerId);
    }

    scheduleChecks() {
        var checks_by_delay = {};
        for (let i in this.prodData.freq_checks) {
            let qc = this.prodData.freq_checks[i];
            if (!(qc['repeat'] in checks_by_delay)) {
                checks_by_delay[qc['repeat']] = [];
            }
            checks_by_delay[qc['repeat']].push(qc) 
        }
        for (let key in checks_by_delay) {
            this.scheduleIntervals(key, checks_by_delay[key]);
        }
    }


    
    // ************************************************************************
    // ************************* BUTONS FUNCTIONS *****************************
    // ************************************************************************
    beginLogistics() {
        this.presentAlert('Logística', 'PENDIENTE DESAROLLO, LLAMAR APP ALMACÉN')
    }

    showConsumptions(workcenter) {
        this.navCtrl.push(ConsumptionsPage)
    }

    confirmProduction() {
        this.promptNextStep('¿Confirmar producción?').then(() => {
            this.prodData.confirmProduction();
        })
        .catch( () => {});
    }

    setupProduction() {
        this.promptNextStep('¿Empezar preparación?').then(() => {
            this.prodData.setupProduction();
            this.timer.toArray()[0].restartTimer()  // Set-Up timer on
        })
        .catch( () => {});
    }

    startProduction() {
        this.promptNextStep('¿Terminar preparación y empezar producción?').then(() => {
            this.openFinishModal("start").then(() => {
                this.openChecksModal('start', this.prodData.start_checks, true).then(() => {
                    this.prodData.startProduction();
                    this.scheduleChecks();
                }).catch(() => {});
            }).catch(() => {});
        })
        .catch( () => {});
    }

    stopProduction() {
        this.promptNextStep('¿Registrar una parada?').then(() => {
            this.hidden_class = 'my-hide'
            var stop_start = this.prodData.getUTCDateStr()
            this.timer.toArray()[1].restartTimer();
            this.openReasonsModal('all').then((res) => {
                if (res !== 0) {
                    var reason_id = res['reason_id']
                    this.hidden_class = 'none'
		    // No reseteamos los checks frecuenciales durante la parada
                    // this.clearIntervales();
                    this.show_create_mo = true;
                    this.prodData.stopProduction(reason_id, stop_start);
                }
            })
            .catch( () => {
                console.log("Pues no hago nada")
            })
        })
        .catch( () => {});
    }

    restartAndCleanProduction() {
        this.promptNextStep('¿Reanudar producción y pasar a limpieza?').then(() => {
            var cleaning_start = this.prodData.getUTCDateStr()
            this.openFinishModal("clean").then(() => {
                this.openChecksModal('end', this.prodData.freq_checks, false).then(() => {
                    this.clearIntervales();
                    this.hidden_class = 'my-hide'
                    this.timer.toArray()[0].restartTimer();
                    this.timer.toArray()[1].pauseTimer();
                    this.prodData.restartAndCleanProduction(cleaning_start);
                }).catch(() => {});
            }).catch(() => {});
        })
        .catch( () => {});
    }

    restartProduction() {
        this.promptNextStep('¿Reanudar producción?').then(() => {
            this.hidden_class = 'my-hide'
            this.timer.toArray()[1].pauseTimer();
            this.prodData.restartProduction();
            if (this.prodData.state !== 'cleaning') {
               // Como no reseteamos los checks frecuenciales durante la parada, tampoco los iniciamos al volver, sino acumulamos
               // this.scheduleChecks();
            }
            // Si la parada dura menos de 20 minutos no pedimos checks de inicio
            if (this.timer.toArray()[1].timer.secondsCounter > 1200) {
                this.openChecksModal('start', this.prodData.start_checks, false).then(() => {}).catch(() => {});
            }
        })
        .catch( () => {});
    }

    cleanProduction() {
        this.promptNextStep('¿Empezar limpieza?').then(() => {
            var cleaning_start = this.prodData.getUTCDateStr()
            this.openFinishModal("clean").then(() => {
                this.openChecksModal('end', this.prodData.freq_checks, false).then(() => {
                    this.clearIntervales();
                    this.timer.toArray()[0].restartTimer();
                    this.prodData.cleanProduction(cleaning_start);
                }).catch(() => {});
            }).catch(() => {});
        })
        .catch( () => {});
    }

    finishProduction() {
        this.promptNextStep('¿Finalizar producción').then(() => {
            this.timer.toArray()[0].restartTimer()
            this.timer.toArray()[0].pauseTimer()
            this.prodData.finishProduction();
        })
        .catch( () => {});
    }

    loadNextProduction() {
        this.prodData.loadProduction({'workcenter_id': this.prodData.workcenter['id']}).then((res) => {
            // this.prodData.active_operator_id = 0;
        })
        .catch( (err) => {
            this.presentAlert("Error", "Fallo al cargar la siguiente producción.");
        }); 
    }

    scrapProduction() {
        this.openScrapModal().then(() => {
            this.prodData.scrapProduction();
        })
        .catch( () => {});
    }

    createMaintenanceOrder() {
        this.openReasonsModal('technical').then((res) => {
            if (res !== 0) {
                this.promptNextStep('¿Crear orden de mantenimiento?').then(() => {
                    var reason_id = res['reason_id']
                    this.show_create_mo = false;
                    this.prodData.createMaintenanceOrder(reason_id);
                })
                .catch( () => {});
            }
        })
        .catch( () => {
            console.log("Pues no hago nada")
        })
    }

    editNote() {
        this.openNoteModal().then(() => {
            this.prodData.editNote();
        })
        .catch( () => {});
    }

}
