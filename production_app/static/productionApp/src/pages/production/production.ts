import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';

/**
 * Generated class for the ProductionPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-production',
  templateUrl: 'production.html',
})
export class ProductionPage {

    constructor(public navCtrl: NavController, public navParams: NavParams, public alertCtrl: AlertController) {
        this.workcenter = this.navParams.get('workcenter_id')[1];
        this.state = 'waiting';
        this.states = {
            'waiting': 'ESPERANDO PRODUCCIÖN',
            'confirmed': 'PRODUCCIÓN CONFIRMADA',
            'setup': 'PREPARACIÓN PRODUCCION',
            'started': 'PRODUCCIÓN INICIADA',
            'stoped': 'PRODUCCIÓN PARADA',
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
    beginLogistics() {
        this.presentAlert('Logistica', 'PENDIENTE DESAROLLO')
    }

    confirmProduction() {
        this.state = 'confirmed'
    }
    setupProduction() {
        this.state = 'setup'
    }
    startProduction() {
        this.state = 'started'
    }
    finishProduction() {
        this.state = 'finished'
        this.state = 'waiting'
    }
    stopProduction() {
        this.state = 'stoped'
    }
    restartProduction() {
        this.state = 'started'
    }


}
