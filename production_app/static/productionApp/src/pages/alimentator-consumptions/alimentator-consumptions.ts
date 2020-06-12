import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ModalController, AlertController } from 'ionic-angular';
import { ConsumeModalPage } from '../../pages/consume-modal/consume-modal';
import { ConsumptionListModalPage } from '../../pages/consumption-list-modal/consumption-list-modal';
import { ConsumptionsPage } from '../../pages/consumptions/consumptions';
import { CalculatorModalPage } from '../../pages/calculator/calculator';
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
    consumptions_scrapped: any[];
    finished_products: any[];
    sum_finished_products;
    title: string;
    consumptions_note: string;

    constructor(public navCtrl: NavController, 
                public navParams: NavParams,
                public alertCtrl: AlertController,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider) {
        this.title = this.prodData.workline_name
	this.consumptions_note = this.prodData.consumptions_note;
    }

    ionViewDidLoad() {
        this.consumptions_in = this.prodData.consumptions_in;
        this.consumptions_out = this.prodData.consumptions_out;
        this.consumptions_scrapped = this.prodData.consumptions_scrapped;
        this.finished_products = this.prodData.finished_products;
        this.sum_finished_products = this.finished_products.reduce((sum, product) => sum + product.qty, 0);
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    open_list_consumes_in() {
        var mydata = {
            'type': 'in',
            'allowed_lines': this.prodData.consumptions
        }
        this.open_list_consumes(mydata)
    }

    open_list_consumes_out() {
        var mydata = {
            'type': 'out',
            'allowed_lines': this.consumptions_in
        }
        this.open_list_consumes(mydata)
    }

    open_list_consumes_scrapped() {
        var mydata = {
            'type': 'scrapped',
            'allowed_lines': this.consumptions_in
        }
        this.open_list_consumes(mydata)
    }

    add_finished_products() {
        if (this.block_by_state() || this.block_by_consumptions_done()) {
            return;
        }
        var mydata = {
            'id': false,
            'product_id': this.prodData.product_id,
            'qty': 0,
            'uom_id': this.prodData.uom_id,
            'location_id': this.prodData.location_dest_id,
            'lot_id': false,
            'type': 'finished'
        }
        // Create new finish product line
        this.prodData.saveConsumptionLine(mydata).then((res) => {
            // Read again lines
            this.prodData.getConsumeInOut().then((res) => {
                this.finished_products = this.prodData.finished_products;
                this.sum_finished_products = this.finished_products.reduce((sum, product) => sum + product.qty, 0);
            })
        })
        .catch( (err) => {
            this.presentAlert("Error", "Fallo al escribir la línea de producto terminado");
        });
    }

    block_by_state() {
        if (this.prodData.state == 'validated') {
            this.presentAlert("Error", "No se pueden modificar consumos en estado validado");
            return true;
        }
        return false
    }

    block_by_consumptions_done() {
        if (this.prodData.consumptions_done == true ) {
            this.presentAlert("Error", "No se pueden modificar consumos confirmados");
            return true;
        }
        return false
    }

    open_list_consumes(data) {
        if (this.block_by_state() || this.block_by_consumptions_done()) {
            return;
        }
        let consumeListModal = this.modalCtrl.create(ConsumptionListModalPage, data);
        consumeListModal.present();

        // When modal closes
        consumeListModal.onDidDismiss(new_line_vals => {
            // Create new consumption line
            this.prodData.saveConsumptionLine(new_line_vals).then((res) => {
                // Read again lines
                this.prodData.getConsumeInOut().then((res) => {
                    this.consumptions_in = this.prodData.consumptions_in;
                    this.consumptions_out = this.prodData.consumptions_out;
                    this.consumptions_scrapped = this.prodData.consumptions_scrapped;
                })
            })
            .catch( (err) => {
                this.presentAlert("Error", "Fallo al escribir la línea de consumo");
            }); 
        });
    }

    consume_click(line) {
        if (this.block_by_state() || this.block_by_consumptions_done()) {
            return;
        }
        var mydata = {'line': line}
        let consumeModal = this.modalCtrl.create(ConsumeModalPage, mydata);
        consumeModal.present();

         // When modal closes
         consumeModal.onDidDismiss(line_vals => {
            this.prodData.saveConsumptionLine(line_vals).then((res) => {
                this.prodData.getConsumeInOut().then((res) => {
                    this.consumptions_in = this.prodData.consumptions_in;
                    this.consumptions_out = this.prodData.consumptions_out;
                    this.consumptions_scrapped = this.prodData.consumptions_scrapped;
                    this.finished_products = this.prodData.finished_products;
                    this.sum_finished_products = this.finished_products.reduce((sum, product) => sum + product.qty, 0);
                })
            })
            .catch( (err) => {
                this.presentAlert("Error", "Fallo al escribir la línea de consumo");
            }); 
        });
    }

    confirm_consumptions() {
        if (this.block_by_state()) {
            return;
        }
        let total_finished_products = 0
        for (let indx in this.finished_products) {
            total_finished_products += this.finished_products[indx].qty
        }
        if (total_finished_products == 0) {
            this.presentAlert("Error", "La cantidad total de producto terminado no puede ser 0");
	    return;
        }
        this.prodData.getMergedConsumptions().then((res) => {
            this.prodData.consumptions_done = true;
            this.prodData.setConsumptionsDone();
        })
        .catch( (err) => {
            this.presentAlert("Error", "Errores detectados en las lineas de consumos");
        });
    }

    remove_confirm_consumptions() {
        if (this.block_by_state()) {
            return;
        }
        this.prodData.consumptions_done = false;
        this.prodData.unsetConsumptionsDone();
    }

    noteChange() {
	this.prodData.consumptions_note = this.consumptions_note;
        this.prodData.editConsumptionsNote();
        // console.log("onchange");
    }

    showConsumptions(workcenter) {
        this.navCtrl.push(ConsumptionsPage)
    }

    openCalculatorModal() {
        var mydata = {}
        let calculatorModal = this.modalCtrl.create(CalculatorModalPage, mydata);
        calculatorModal.present();
    }


}
