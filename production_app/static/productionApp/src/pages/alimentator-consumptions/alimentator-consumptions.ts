import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ModalController, AlertController } from 'ionic-angular';
import { ConsumeModalPage } from '../../pages/consume-modal/consume-modal';
import { ProductionProvider } from '../../providers/production/production';

/**
 * Generated class for the AlimentatorConsumptionsPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-alimentator-consumptions',
  templateUrl: 'alimentator-consumptions.html',
})
export class AlimentatorConsumptionsPage {

    consumptions_in: any[];
    consumptions_out: any[];
    title: String;

    constructor(public navCtrl: NavController, 
                public navParams: NavParams,
                public alertCtrl: AlertController,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider) {
        this.title = this.prodData.workline_name

    }

    ionViewDidLoad() {
        this.consumptions_in = this.prodData.consumptions_in;
        this.consumptions_out = this.prodData.consumptions_out;
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    updateLotValue(line_vals){
        if (!line_vals.lot_id)
            return
        if (line_vals.type == 'out'){
            for (let indx in this.consumptions_in) {
                if (this.consumptions_in[indx].product_id == line_vals.product_id) {
                    this.consumptions_in[indx].lot_id = line_vals.lot_id
                    this.consumptions_in[indx].lot_name = line_vals.lot_name
                    break;
                }
            }
        }
        else{
            for (let indx in this.consumptions_out) {
                if (this.consumptions_out[indx].product_id == line_vals.product_id) {
                    this.consumptions_out[indx].lot_id = line_vals.lot_id
                    this.consumptions_out[indx].lot_name = line_vals.lot_name
                    break;
                }
            }
        }
        return
    }


    consume_click(line){
        var mydata = {'line': line}
        let consumeModal = this.modalCtrl.create(ConsumeModalPage, mydata);
        consumeModal.present();


         // When modal closes
         consumeModal.onDidDismiss(line_vals => {
            this.prodData.saveConsumptionLine(line_vals).then((res) => {
                this.updateLotValue(line);
                console.log("Línea de operario escrita")
            })
            .catch( (err) => {
                this.presentAlert("Error", "Falló al escribir la línea de consumo");
            }); 
        });
    }

}
