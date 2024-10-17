import { Component } from '@angular/core';
import { NavParams, AlertController } from 'ionic-angular';
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';
/**
 * Generated class for the StockLocationComponent component.
 *
 * See https://angular.io/api/core/Component for more info on Angular
 * Components.
 */
@Component({
    selector: 'stock-location',
    templateUrl: 'stock-location.html'
})
export class StockLocationComponent {

    id: Number
    constructor(private odoo: OdooProvider, public alertCtrl: AlertController, public navParams: NavParams,) {
        this.id = this.navParams.data.location_id;
        console.log('Hello StockLocationComponent Component');
    }

    load_stock(id, stock = 'stock') {
        let values = { 'id': id, 'type': stock }
        //var self = this;
        //var object_id = {}
        var model = 'stock.location'
        var method = 'get_pda_info'
        this.odoo.execute(model, method, values).then((value) => {
            if (value) {
                this.presentAlert('Error!', values);
            }
        })
            .catch(() => {
                this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
            });
    }

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }
}
