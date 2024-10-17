import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/

import { Storage } from '@ionic/storage';
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector'
//import { SHARED_FORM_DIRECTIVES } from '@angular/forms/src/directives';
//import { BarcodeScanner } from '../../providers/odoo-connector/barcode_scanner';
/**
 * Generated class for the ManualPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */


@IonicPage()
@Component({
    selector: 'page-manual',
    templateUrl: 'manual.html',
})

export class ManualPage {

    @ViewChild('scan') myScan;

    max_qty = 0.00
    model = 'stock.move'
    move = {}
    domain = []
    message = ''
    //state: number = 0; /* 0 origen 1 destino 2 validar */
    state: string
    scan_id: string = ''
    cargar
    models = []
    last_scan = ''
    input: number = 0;
    barcodeForm: FormGroup;
    tracking = 'none'
    debug = true

    constructor(public navCtrl: NavController, public toastCtrl: ToastController,
        public navParams: NavParams, private formBuilder: FormBuilder,
        public storage: Storage, private odoo: OdooProvider,
        public alertCtrl: AlertController) {
        this.debug = true
        this.input = 0;
        this.models = ['stock.production.lot', 'stock.location', 'product.product']
        this.cargar = false
        this.reset_form();
        this.tracking = 'lot';
    }

    get_filter() {
        let domain = []
        let lot_id = this.move['lot_id'] && this.move['lot_id']['id']
        let product_id = this.move['product_id'] && this.move['product_id']['id']
        let company_id = this.move['company_id'] && this.move['company_id']['id']
        let location_id = this.move['location_id'] && this.move['location_id']['id']
        if (company_id) {
            domain.push(['company_id', '=', company_id])
        }
        if (lot_id) {
            domain.push(['lot_id', '=', lot_id])
        }
        if (product_id) {
            domain.push(['product_id', '=', product_id])
        }
        if (location_id) {
            domain.push(['location_id', '=', location_id])
        }
        return domain
    }

    reset_form() {
        this.state = 'origin';
        this.scan_id = '';
        this.last_scan = ''
        this.barcodeForm = this.formBuilder.group({ scan: [''] });
        this.move = {};
        this['move']['productqty_qty'] = 0;
        console.log(this)
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad ManualPage');
    }

    get_id(val) {
        return (val && val[0]) || false

    }

    include(arr, obj) {
        return (arr.indexOf(obj) != -1);
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }

    get_lot_location_ids(id) {
        let model = 'stock.production.lot'
        let method = 'get_location_ids'
        let values = { 'id': id }

        this.odoo.execute(model, method, values).then((val) => {
            this.move['location_ids'] = val
        })
            .catch(() => {
                this.presentToast("Error al recuperar las ubicaciones del lote: " + this.move['lot_id'], false);
                return false;
            })
    }

    submit_dest_id(values, models = []) {
        if (!models) {
            models = this.models
        }
        var model = 'stock.move'
        var method = 'pda_get_destination_for_move'
        values['move'] = this.get_move_values(this.move)

        this.odoo.execute(model, method, values).then((val) => {
            this.check_dest_val(val)
        })
            .catch(() => {
                this.presentToast("Error al recuperar los ids", false);
                return false;
            })


    }

    submit(values, models = []) {

        //BUSCO LOS IDS Y EL MODELO
        if (!models) {
            models = this.models
        }
        var model = 'stock.move'
        var method = 'get_ids'
        values['move'] = this.get_move_values(this.move)
        values['move']['filter'] = this.get_move_filter(this.move)
        this.odoo.execute(model, method, values).then((val) => {
            this.check_val(val)
        })
            .catch(() => {
                this.presentToast("Error al recuperar los ids", false);
                return false;
            })
    }

    ret_m2o(val, field) {
        let m2o = { 'id': val[field][0], 'name': val[field][1] }
        return m2o
    }

    get_state() {
        let state = 'origin'
        let product = this.move['product_id']
        let lot = this.move['lot_id']
        let product_check = (product && product['id']) && ((product['track_all'] && lot && lot['id']) || (product && !product['track_all']))
        if (product_check && this.move['location_id']['id'] && this.move['company_id']) {
            state = 'qty'
        }
        if (state == 'qty' && this.move['location_dest_id'] && this.move['qty'] > 0.00) {
            state = 'dest'
        }
        return state
    }

    ids_to_id(val, field, field_ids) {
        if (val.length == 1) {
            this.move[field] = val[0]
            this.move[field_ids] = false
        }
        else {
            this.move[field] = false
            this.move[field_ids] = val
        }
    }

    check_dest_val(val) {
        if (this.state == 'qty') {
            if (val['location_dest_id']) {
                this.move['location_dest_id'] = val['location_dest_id']
            }
        }
        this.state = this.get_state()
        return true
    }

    check_val(val) {
        if (val['empty']) {
            this.presentToast(val['error'])
            return
        }
        //let product_id={}
        //let uom_id = {}
        //let location_id ={}
        //let lot_id = {}
        //let location_dest_id = {}
        //let qty = -1
        //let product_ids = val['product_ids']
        let field = ['lot_id', 'location_id', 'product_id', 'product_id', 'company_id']

        for (let f in field) {
            this.ids_to_id(val[field[f] + 's'], field[f], field[f] + 's')
        }
        this.move['lots'] = val['lots']
        this.move['qty'] = val['qty']
        this.move['product_uom'] = val['product_uom'] || val['lots'] && val['lots'][0]['uom_id']
        this.state = this.get_state()
        return true

        /*
        if (val['model']=='stock.location' && this.state=='qty'){
          this.move['location_dest_id'] = val['values'][0]
    
        }  
    
        if (this.state=='origin'){
          if (qty >=0) {this.move['qty']=qty}
          this.move['product_id'] = product_id
          this.move['location_id'] = location_id  
          this.move['uom_id'] = uom_id
        }
        this.state = this.get_state()
        */
    }

    select(company_id = false, lot_id = false, product_id = false, location_id = false, reservation_id = false) {
        this.cargar = true
        if (lot_id) {
            this.move['lot_id'] = { 'id': lot_id, 'name': 'nombre' }
        }
        if (company_id) {
            this.move['company_id'] = { 'id': company_id, 'name': 'nombre' }
        }
        if (product_id) {
            this.move['product_id'] = { 'id': product_id, 'name': 'nombre' }
        }
        if (location_id) {
            this.move['location_id'] = { 'id': location_id, 'name': 'nombre' }
        }
        if (reservation_id)
            this.move['reservation_id'] = reservation_id

        let values = { 'model': [], 'search_str': false, 'return_object': true };
        this.submit(values);
    }

    select_product(product_id, company_id = false, lot_id = false, location_id = false, reservation_id = false) {
        return this.select(company_id, lot_id, product_id, location_id, reservation_id)
    }

    select_lot(lot_id, company_id = false, product_id = false, location_id = false, reservation_id = false) {
        if (lot_id) {
            return this.select(company_id, lot_id, product_id, location_id, reservation_id)
        }
    }

    select_location(location_id, company_id = false, lot_id = false, product_id = false, reservation_id = false) {
        return this.select(company_id, lot_id, product_id, location_id, reservation_id)
    }

    inputQty() {
        let alert = this.alertCtrl.create({
            title: 'Qty',
            message: 'Cantidad a mover',
            inputs: [
                {
                    name: 'qty',
                    placeholder: this['move']['qty'].toString()
                },
            ],
            buttons: [
                {
                    text: 'Cancel',
                    handler: () => {
                        console.log('Cancel clicked');
                    }
                },
                {
                    text: 'Save',
                    handler: (data) => {
                        console.log('Saved clicked');
                        console.log(data.qty);
                        if (data.qty < 0) {
                            this.presentAlert('Error!', 'La cantidad debe ser mayor que 0');
                            return
                        }
                        else if (data.qty > this.move['qty']) {
                            this.presentAlert('Error!', 'La cantidad debe ser menor que la disponible');
                            return
                        }
                        this['move']['qty'] = data.qty
                        this.get_state();
                        this.input = 0;

                    }
                }
            ]
        });
        this.input = alert._state;
        alert.present();
    }

    presentToast(message, showClose = false) {
        var self = this;
        let duration = 3000;
        let toastClass = 'toastOk';
        //if (showClose){let toastClass = 'toastNo'};
        let toast = this.toastCtrl.create({
            message: message,
            duration: duration,
            position: 'top',
            showCloseButton: showClose,
            closeButtonText: 'Ok',
            cssClass: toastClass
        });
        toast.onDidDismiss(() => {
            self.myScan.setFocus();
        });
        toast.present();
    }

    get_move_values(move) {
        var values = {
            'product_id': move['product_id'] && move['product_id']['id'] || false,
            'product_qty': move['qty'] || 0,
            'restrict_lot_id': move['lot_id'] && move['lot_id']['id'] || false,
            'lot_id': move['lot_id'] && move['lot_id']['id'] || false,
            'location_id': move['location_id'] && move['location_id']['id'] || false,
            'location_dest_id': move['location_dest_id'] && move['location_dest_id']['id'] || false,
            'product_uom_qty': move['qty'] || 0,
            'company_id': move['company_id'] && move['company_id']['id'] || false,
            'reservation_id': move['reservation_id'] || false,
            'origin': 'PDA move'
        }
        return values
    }

    get_ids_list(val_ids) {
        let ids = []

        for (let x in val_ids) {
            ids.push(val_ids[x]['id'])
        }
        return ids
    }

    get_move_filter(move) {
        var filter = {
            'lot_ids': this.get_ids_list(move['lot_ids']),
            'product_ids': this.get_ids_list(move['product_ids']),
            'location_ids': this.get_ids_list(move['location_ids']),
            'company_ids': this.get_ids_list(move['company_ids']),
        }
        return filter
    }

    process_move() {
        /* CREAR Y PROCESAR UN MOVIMEINTO */
        var values = this.get_move_values(this['move'])
        var model = 'stock.move'
        var method = 'pda_move'
        this.odoo.execute(model, method, values).then((val) => {
            if (val['id'] != 0) {
                this.presentToast(val['message'], false);
                this.reset_form();
                return
            }
            else {
                this.presentToast(val['message'], true);
                return
            }
        })
            .catch(() => {
                this.presentToast("Error al recuperar los ids3", false);
                return false;
            })

    }

    get_ids_from_lots(new_lots) {

    }

    find(scan) {
        let index
        // SUPONGO PAQUETES UNICOS
        let lots = []
        for (index in this.move['lot_ids']) {
            if (this.move['lot_ids'][index]['name'] == scan) {
                lots.push(this.move['lot_ids'][index])
            }
        }
        if (lots) {
            this.move['lot_ids'] = lots
            return this.select_lot(false)
        }
        for (index in this.move['location_ids']) {
            let loc = this.move['location_ids'][index]
            if (loc['loc_barcode'] == scan) {
                return this.select_location(loc['id'])
            }
        }
        for (index in this.move['product_ids']) {
            let prod = this.move['product_ids'][index]
            if (prod['ean13'] == scan) {
                return this.select_product(prod['id'])
            }
        }
    }

    Scan(scan) {
        //let filter = 
        this.cargar = true
        let values
        if (this.state == 'dest' && this.last_scan == scan) {
            this.process_move();
        }
        else if (this.state == 'qty') {
            values = { 'model': ['stock.location'], 'search_str': scan, 'return_object': true };
            this.submit_dest_id(values);
        }
        else {
            values = { 'model': this.models, 'search_str': scan, 'return_object': true };
            if (this.move['product_ids'] || this.move['lot_ids'] || this.move['location_ids'] || this.move['product_ids']) {
                this.find(scan)
            }
            else {
                this.submit(values);
            }
        }
        this.last_scan = scan
    }

    submitScan() {
        this.Scan(this.barcodeForm.value['scan'])
        this.barcodeForm.reset();
    }
}
