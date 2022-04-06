import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, ViewController, ModalController, AlertController } from 'ionic-angular';
import { Storage } from '@ionic/storage';
import { ProductionProvider } from '../../providers/production/production';
import { CalculatorModalPage } from '../../pages/calculator/calculator';


@IonicPage()
@Component({
  selector: 'page-finish-modal',
  templateUrl: 'finish-modal.html',
})
export class FinishModalPage {
    navbarColor: string = 'primary';
    qty = 0;
    uos_qty = 0;
    lot: string;
    date: string;
    max_date: string;
    lots: Object[];
    items: Object[];
    mode: string = 'default';
    mode_step: string = 'start';
    ctrl: string = 'do';
    allow_zero: boolean = false;

    constructor(public navCtrl: NavController, private storage: Storage,
                public navParams: NavParams,
                public viewCtrl: ViewController, public alertCtrl: AlertController,
                public modalCtrl: ModalController,
                private prodData: ProductionProvider) {
        this.storage.get('CONEXION').then((con_data) => {
            this.mode = con_data.mode;
            this.navbarColor = con_data.company == 'qv' ? 'qv' : 'vq';
        })
        this.lots = [];
        this.items = [];
        // Inicializamos los valores de lote y fecha del PT con lo que se ha cargado al inicializar el registro
        // por si cuando llamamos a getMaxUseDate() estamos offline (de esta forma tenemos unos valores 
        // que deberían ser válidos en el 99% de los casos)
        this.lot = this.prodData.product_lot_name;
        this.date = this.prodData.product_use_date;
        this.max_date = this.prodData.product_max_date;
        this.prodData.getMaxUseDate().then(() => {
            this.lot = this.prodData.product_lot_name;
            this.date = this.prodData.product_use_date;
            this.max_date = this.prodData.product_max_date;
        }).catch(() => {});
        this.ctrl = 'do'
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad FinishModalPage');
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

    confirm() {
        var res = {};
        if (this.mode_step === 'clean') {
            if (this.qty == 0 && !this.allow_zero) {
                this.presentAlert("Error", "Es obligatorio indicar una cantidad mayor que 0");
		return;
            };
            if (!isNaN(this.qty) && this.qty >= 0) {
                res['qty'] = +this.qty;
            } else {
                this.presentAlert("Error", "Es obligatorio indicar una cantidad");
                return;
            };
        } else {
            if (isNaN(Date.parse(this.date))) {
                this.presentAlert("Error", "La fecha indicada no es válida");
                return;
            };
            if (!(this.lot)) {
                this.presentAlert("Error", "Es obligatorio indicar un lote");
                return;
            };
            res['lot'] = this.lot
            res['date'] = this.date
        };
        // Si no tenemos max_date es porque el PT está marcado para no chequear o 
        // porque aun no añadimos componentes al registro de app
        if (this.date && this.max_date && this.date > this.max_date) {
            let titulo = "Advertencia";
            let texto = "La fecha de caducidad es:<br>" + 
                this.date.replace(/(\d{4})\-(\d{2})\-(\d{2}).*/, '$3-$2-$1') + 
                "<br>y no debería ser superior a:<br>" + 
                this.max_date.replace(/(\d{4})\-(\d{2})\-(\d{2}).*/, '$3-$2-$1') + 
                ".<br>¡Proceda a informar al responsable de producción de esta anomalía!" + 
                "<br>¿Continuar?" 
            this.confirmationAlert(titulo, texto).then(confirm => {
                if (confirm) {
                    this.prodData.registerMessage(
                        'Modo: Producción. FCP corta en uno de los componentes. Estado: ' + this.mode_step + '.');
                } else {
                    return
                }
            })
        };
        this.viewCtrl.dismiss(res);
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

    open_calculator() {
        let calulatorModal = this.modalCtrl.create(CalculatorModalPage);
        calulatorModal.present();
        // When modal closes
        calulatorModal.onDidDismiss(res => {
            if ('display_value' in res) {
                this.uos_qty = res['display_value']
            }
        });
    }

    showLots() {
        this.mode = 'show'
        if (this.prodData.product_id in this.prodData.lotsByProduct) {
            this.lots = this.prodData.lotsByProduct[this.prodData.product_id]
            this.items = this.prodData.lotsByProduct[this.prodData.product_id].filter(
                lot_id => lot_id.location_id === false);
        }
    }

    lotSelected(lot_obj) {
        this.mode = 'default';
        this.lot = lot_obj.name
        if (lot_obj.use_date) {
            this.date = lot_obj.use_date.split(" ")[0]
        }
    }

    getItems(ev: any) {
        // Reset items back to all of the items
        this.items = this.prodData.lotsByProduct[this.prodData.product_id].filter(
            lot_id => lot_id.location_id === false);

        // set val to the value of the searchbar
        let val = ev.target.value;

        // if the value is an empty string don't filter the items
        if (val && val.trim() != '') {
            this.items = this.items.filter((item) => {
                return (item['name'].toLowerCase().indexOf(val.toLowerCase()) > -1);
            })
        }
    }

    onchange_uom() {
        if (this.ctrl !== 'not do') {
            var uos_coeff = this.prodData.uos_coeff;
            this.uos_qty = parseFloat((this.qty * uos_coeff).toFixed(2));
            this.ctrl = 'not do';
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
            this.qty = parseFloat((this.uos_qty / uos_coeff).toFixed(2))
            this.ctrl = 'not do';
        } else {
            this.ctrl = 'do';
        }  
    }

    get_default_lot_name() {
        this.lot = this.prodData.get_default_lot_name()
        this.date = this.prodData.product_use_date;
    }

}
