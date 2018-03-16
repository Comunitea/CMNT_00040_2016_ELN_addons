import { Component, ViewChild } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ModalController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { HomePage } from '../../pages/home/home';
import { ChecksModalPage } from '../../pages/checks-modal/checks-modal';
import { UsersModalPage } from '../../pages/users-modal/users-modal';
import { OdooProvider } from '../../providers/odoo/odoo';
import { ProductionProvider } from '../../providers/production/production';
import { TimerComponent } from '../../components/timer/timer';


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
    
    cdb;
    weight;
    interval_list: any[] = [];

    @ViewChild(TimerComponent) timer: TimerComponent;

    constructor(public navCtrl: NavController, private storage: Storage, 
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
    
    writeFinishProductionData() {
        var values =  {'registry_id': this.prodData.registry_id, 
                       'cdb': this.cdb, 
                       'weight': this.weight};
        this.odooCon.callRegistry('finish_production', values).then( (res) => {
            console.log("PRODUCCIÓN FINALIZADA:") 
            this.prodData.state = res['state'];
        })
        .catch( (err) => {
            console.log(err) 
        });

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
        var mydata = {
        }
        let usersModal = this.modalCtrl.create(UsersModalPage, mydata);
        usersModal.present();
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
            if (!(qc.repeat in checks_by_delay)){
                checks_by_delay[qc.repeat] = [];
            }
            checks_by_delay[qc.repeat].push(qc) 
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
        this.prodData.confirmProduction();
    }

    setupProduction() {
        this.prodData.setupProduction();
        this.timer.startTimer()  // Set-Up timer on
        
    }

    startProduction() {
        this.prodData.startProduction();

        this.openModal('start', this.prodData.start_checks);  // Production timer setted when modal is clos   
        this.scheduleChecks();
    }

    stopProduction() {
        this.timer.pauseTimer();
        this.prodData.stopProduction();
    }

    restartProduction() {
        this.timer.resumeTimer();
        this.prodData.restartProduction();
    }

    cleanProduction() {
        this.clearIntervales();
        this.timer.restartTimer();
        this.prodData.cleanProduction();
    }

    finishProduction() {
        this.timer.pauseTimer()
        this.prodData.finishProduction();
        this.promptFinishData();
    }

}
