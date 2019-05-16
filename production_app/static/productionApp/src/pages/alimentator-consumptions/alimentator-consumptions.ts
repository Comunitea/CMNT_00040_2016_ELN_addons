import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ModalController, AlertController } from 'ionic-angular';
import { ConsumeModalPage } from '../../pages/consume-modal/consume-modal';
import { ConsumptionListModalPage } from '../../pages/consumption-list-modal/consumption-list-modal';
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

    // Necesitaría enlazar la entrada con la salida para hacer esto bien
    // updateLotValue(line_vals){
    //     if (!line_vals.lot_id)
    //         return
    //     if (line_vals.type == 'out'){
    //         for (let indx in this.consumptions_in) {
    //             if (this.consumptions_in[indx].product_id == line_vals.product_id) {
    //                 this.consumptions_in[indx].lot_id = line_vals.lot_id
    //                 this.consumptions_in[indx].lot_name = line_vals.lot_name
    //                 break;
    //             }
    //         }
    //     }
    //     else{
    //         for (let indx in this.consumptions_out) {
    //             if (this.consumptions_out[indx].product_id == line_vals.product_id) {
    //                 this.consumptions_out[indx].lot_id = line_vals.lot_id
    //                 this.consumptions_out[indx].lot_name = line_vals.lot_name
    //                 break;
    //             }
    //         }
    //     }
    //     return
    // }
    open_list_consumes_in(){
        var mydata = {
            'type': 'in',
            'allowed_lines': this.prodData.allowed_consumptions
        }
        this.open_list_consumes(mydata)
    }
    open_list_consumes_out(){
        var mydata = {
            'type': 'out',
            'allowed_lines': this.consumptions_in
        }
        this.open_list_consumes(mydata)
    }
    block_by_state(){
        if (this.prodData.state == 'validated'){
            this.presentAlert("Error", "No se pueden modificar consumos en estado validado");
            return true;
        }
        return false
    }
    open_list_consumes(data){
        if (this.block_by_state()){
            return;
        }
        let consumeListModal = this.modalCtrl.create(ConsumptionListModalPage, data);
        consumeListModal.present();

        // When modal closes
        consumeListModal.onDidDismiss(new_line_vals => {
            console.log(new_line_vals);
            // Create new consuption line
            this.prodData.saveConsumptionLine(new_line_vals).then((res) => {
                // Read again lines
                this.prodData.getConsumeInOut().then((res) => {
                    this.consumptions_in = this.prodData.consumptions_in;
                    this.consumptions_out = this.prodData.consumptions_out;
                })
            })
            .catch( (err) => {
                this.presentAlert("Error", "Falló al escribir la línea de consumo");
            }); 
        });
    }

    consume_click(line){
        if (this.block_by_state()){
            return;
        }


        var mydata = {'line': line}
        let consumeModal = this.modalCtrl.create(ConsumeModalPage, mydata);
        consumeModal.present();


         // When modal closes
         consumeModal.onDidDismiss(line_vals => {
            // if (line_vals.remove_id) {
            //     alert('Borrar')
            //     return
            // }
            this.prodData.saveConsumptionLine(line_vals).then((res) => {
                console.log("Línea de operario escrita")
                // this.updateLotValue(line);
                this.prodData.getConsumeInOut().then((res) => {
                    this.consumptions_in = this.prodData.consumptions_in;
                    this.consumptions_out = this.prodData.consumptions_out;
                })
            })
            .catch( (err) => {
                this.presentAlert("Error", "Falló al escribir la línea de consumo");
            }); 
        });
    }

    confirm_consumptions(){
        if (this.block_by_state()){
            return;
        }
        this.prodData.consumptions_done = true;
        this.prodData.setConsumptionsDone();
    }
    remove_confirm_consumptions(){
        if (this.block_by_state()){
            return;
        }
        this.prodData.consumptions_done = false;
        this.prodData.unsetConsumptionsDone();
    }

}
