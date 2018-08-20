import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';

import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';

/**
 * Generated class for the LocationPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-location',
  templateUrl: 'location.html',
})
export class LocationPage {
  
  cargar: Boolean
  id: Number
  location = {}
  stock = []
  offset=0
  limit=25
  type: String
  cabecera: Boolean
  constructor(public navCtrl: NavController, private odoo: OdooProvider, public alertCtrl: AlertController,  public navParams: NavParams,) {
    this.id = this.navParams.data.location_id || this.navParams.data.id;
    this.cargar=true
    this.offset=0
    this.limit=5
    this.type ='stock'
    this.cabecera = true
    this.load_stock(this.id, this.type, 0,0,false)
  }

  load_stock(id, stock, offset=0, inc_offset=0, last=false){
    this.type = stock
    this.offset = inc_offset + offset
    if (this.offset<0){
      this.offset=0
    }
    let values = {'id': id, 'type': this.type, 'offset': this.offset, 'limit': this.limit, 'last': last}
    var object_id = {}
    var model = 'stock.location'
    var method = 'get_pda_info'

    this.odoo.execute(model, method, values).then((value)=>{
     console.log("OK")
     if (value['stock'].length == 0 && this.offset != 0){
      this.load_stock(id, this.type, this.offset, -this.limit)
     }
     else {
      this.location = value['location']
      this.stock = value['stock']
      this.offset = value['location']['offset'] 
      this.cargar = false
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

  inputlineas() {
    var self = this;
    
    let alert = this.alertCtrl.create({
      title: 'Líneas',
      message: 'nº de líneas',
      inputs: [
        {
          name: 'nlineas',
          placeholder: self.limit.toString()
        },
       
      
      ],
      buttons: [
        {
          text: 'Cancelar',
          handler: () => {
            console.log('Cancel clicked');
          }
        },
        {
          text:'Ok',
          handler:(data)=>{
            this.limit = data.nlineas*1
          }
        },
      
      
      ]
    });
    alert.present();
  }
}
