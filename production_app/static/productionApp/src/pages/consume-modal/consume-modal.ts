import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, ModalController, AlertController} from 'ionic-angular';
import { ProductionProvider } from '../../providers/production/production';
import { OdooProvider } from '../../providers/odoo/odoo';
import { CalculatorModalPage } from '../../pages/calculator/calculator';

/**
 * Generated class for the ConsumeModalPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-consume-modal',
  templateUrl: 'consume-modal.html',
})
export class ConsumeModalPage {
    line;
    lots: Object[];
    items: Object[];

    mode: string = 'default';

    constructor(public navCtrl: NavController, public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider, private odooCon: OdooProvider) {
        this.line = this.navParams.get('line');
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ConsumeModalPage');
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    showLots(){
        this.mode = 'show'
        if (this.line.product_id in this.prodData.lotsByProduct){
            this.lots = this.prodData.lotsByProduct[this.line.product_id]
            this.items = this.prodData.lotsByProduct[this.line.product_id]
        }
    }
    lotSelected(lot_obj){
        this.mode = 'default';
        this.line.lot_name = lot_obj.name
        this.line.lot_id = lot_obj.id
    }

    getItems(ev: any) {
        // Reset items back to all of the items
        this.items = this.prodData.lotsByProduct[this.prodData.product_id]

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                return (item['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }

    confirmModal() {
        if (this.line.lot_required && !this.line.lot_id && (this.line.type == 'in' || this.line.type == 'out')) {
            this.presentAlert("Error", "Es obligatorio indicar el lote")
        } else {
            this.viewCtrl.dismiss(this.line);
        }
    }

    removeLine() {
        let confirm = this.alertCtrl.create({
          title: '¿Eliminar línea?',
          message: '¿Seguro que deseas eliminar la línea seleccionada?',
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
                  this.line.remove = true;
                  this.viewCtrl.dismiss(this.line);
              }
            }
          ]
        });
        confirm.present();
        // this.line.remove = true;
        // this.viewCtrl.dismiss(this.line);
    }

    closeModal() {
        this.viewCtrl.dismiss([]);
    }

    open_calculator() {
        let calulatorModal = this.modalCtrl.create(CalculatorModalPage);
        calulatorModal.present();
        // When modal closes
        calulatorModal.onDidDismiss(res => {
            if ('display_value' in res) {
                this.line.qty = res['display_value']
            }
        });
    }

    convert_bobbin(qty_to_convert: number) {
        var model = 'product.product'
        var domain = [['id', '=', this.line.product_id]]
        var fields = ['id', 'name', 'unit_gross_weight', 'unit_net_weight']
        this.odooCon.searchRead(model, domain, fields).then( (res) => {
            var bobbin_weight = res[0].unit_net_weight;
            var core_weight = res[0].unit_gross_weight - bobbin_weight;
            var net_qty_to_convert = 1000 * qty_to_convert - core_weight
            if (bobbin_weight != 0.0 && net_qty_to_convert > 0.0) {
                this.line.qty = Math.round(net_qty_to_convert / bobbin_weight)
            }
        })
        .catch( (err) => {
            this.presentAlert("Error", "Fallo en la conversión de kilogramos a metros");
        });
    }

}
