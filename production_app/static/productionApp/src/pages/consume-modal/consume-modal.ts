import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, ModalController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
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
    navbarColor: string = 'primary';
    line;
    lots: Object[];
    items: Object[];
    uos_qty = 0;
    ctrl: string = 'do';

    mode: string = 'default';

    constructor(public navCtrl: NavController, private storage: Storage,
                public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider, private odooCon: OdooProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.mode = con_data.mode;
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        this.line = this.navParams.get('line');
        this.ctrl = 'do';
        if (this.line.type == 'finished') {
            // Ejecuto el onchange 2 veces al cargar.
            // El primero para calcular uos_qty al inicio
            // y el segundo para corregir un corportamiento anómalo que hace
            // que no se disparen correctamente hasta la segunda pulsación
            this.onchange_uom();
            this.onchange_uom();
        }
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ConsumeModalPage');
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

    confirmationAlert(titulo, texto): Promise<boolean> {
        let resolveFunction: (confirm: boolean) => void;
        let promise = new Promise<boolean>(resolve => {
            resolveFunction = resolve;
        });
        let alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            enableBackdropDismiss: false,
            buttons: [ {
                text: 'No',
                handler: () => resolveFunction(false)
            }, {
                text: 'Sí',
                handler: () => resolveFunction(true)
            } ]
        });
        alert.present();
        return promise;
    }

    showLots() {
        this.mode = 'show'
        if (this.line.product_id in this.prodData.lotsByProduct) {
            this.lots = this.prodData.lotsByProduct[this.line.product_id]
            this.items = this.prodData.lotsByProduct[this.line.product_id].filter(
                lot_id => lot_id.location_id === this.line.location_id);
        }
    }

    lotSelected(lot_obj) {
        this.mode = 'default';
        this.line.lot_name = lot_obj.name
        this.line.lot_id = lot_obj.id
    }

    getItems(ev: any) {
        // Reset items back to all of the items
        this.items = this.prodData.lotsByProduct[this.line.product_id].filter(
            lot_id => lot_id.location_id === this.line.location_id);

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
            return;
        };
        var use_date = this.prodData.product_use_date;
        var check_type = this.prodData.product_check_type;
        var comp_product= this.prodData.lotsByProduct[this.line.product_id] && 
            this.prodData.lotsByProduct[this.line.product_id].filter(
                lot_id => (lot_id && lot_id.id || false) === this.line.lot_id);
        var comp_date = (!(comp_product === undefined || comp_product.length == 0) &&
            comp_product[0]['use_date'] && comp_product[0]['use_date'].substring(0, 10) || '');
        // console.log("comp_product", comp_product, "comp_date", comp_date, "use_date", use_date, "check_type", check_type);
        if (this.line.type == 'in' && check_type != 'no_check') {
            var today = this.prodData.getUTCDateStr().substring(0, 10) 
            if (comp_date && today > comp_date) {
                let titulo = "Advertencia";
                let texto = "La fecha de caducidad de este componente ha expirado:<br>" + 
                    comp_date.replace(/(\d{4})\-(\d{2})\-(\d{2}).*/, '$3-$2-$1') + 
                    ".<br>¡Proceda a informar al responsable de producción de esta anomalía!" + 
                    "<br>¿Continuar?"
                this.confirmationAlert(titulo, texto).then(confirm => {
                    if (confirm) {
                        this.prodData.registerMessage(
                            'Modo: Alimentador. ' + 
                            'FCP expirada en el producto: ' + 
                            this.line.product_name + ', Lote: ' + this.line.lot_name + '.'
                        );
                        this.viewCtrl.dismiss(this.line);
                    } else {
                        return
                    }
                })
            } else if (check_type == 'short_dates' && use_date && comp_date && use_date > comp_date) {
                let titulo = "Advertencia";
                let texto = "La fecha de caducidad de este componente es:<br>" + 
                    comp_date.replace(/(\d{4})\-(\d{2})\-(\d{2}).*/, '$3-$2-$1') + 
                    "<br>y no debería ser inferior a:<br>" + 
                    use_date.replace(/(\d{4})\-(\d{2})\-(\d{2}).*/, '$3-$2-$1') + 
                    ".<br>¡Proceda a informar al responsable de producción de esta anomalía!" + 
                    "<br>¿Continuar?"
                this.confirmationAlert(titulo, texto).then(confirm => {
                    if (confirm) {
                        this.prodData.registerMessage(
                            'Modo: Alimentador. ' + 
                            'FCP corta en el producto: ' + 
                            this.line.product_name + ', Lote: ' + this.line.lot_name + '.'
                        );
                        this.viewCtrl.dismiss(this.line);
                    } else {
                        return
                    }
                })
            } else {
                this.viewCtrl.dismiss(this.line);
            };
        } else {
            this.viewCtrl.dismiss(this.line);
        };
    }

    removeLine() {
        let confirm = this.alertCtrl.create({
          title: '¿Eliminar línea?',
          message: '¿Seguro que deseas eliminar la línea seleccionada?',
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
                  this.line.remove = true;
                  this.viewCtrl.dismiss(this.line);
              }
            }
          ]
        });
        confirm.present();
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
        var model = 'product.logistic.sheet'
        var domain = [['product_id', '=', this.line.product_id]]
        var fields = ['id', 'name', 'unit_gross_weight', 'unit_net_weight']
        this.odooCon.searchRead(model, domain, fields, 0, 1, 'sequence').then((res) => {
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

    onchange_uom() {
        if (this.ctrl !== 'not do') {
            var uos_coeff = this.prodData.uos_coeff;
            var new_qty = parseFloat((this.line.qty * uos_coeff).toFixed(2));
            if (new_qty !== this.uos_qty) {
                this.uos_qty = new_qty;
                this.ctrl = 'not do';
            }
        } else {
            this.ctrl = 'do';
        }
    }

    onchange_uos() {
        if (this.ctrl !== 'not do') {
            var uos_coeff = this.prodData.uos_coeff;
            if (uos_coeff == 0) {
                uos_coeff = 1;
            }
            var new_qty = parseFloat((this.uos_qty / uos_coeff).toFixed(2));
            if (new_qty !== this.line.qty) {
                this.line.qty = new_qty;
                this.ctrl = 'not do';
            }
        } else {
            this.ctrl = 'do';
        }  
    }

}
