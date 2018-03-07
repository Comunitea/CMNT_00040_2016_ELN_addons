import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController} from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
import { HostListener } from '@angular/core';
import { Storage } from '@ionic/storage';

//*Pagians
import { HomePage } from '../home/home';
import { LotPage } from '../lot/lot';
import { LocationPage } from '../location/location';
import { PackagePage } from '../package/package';
import { ProductPage } from '../product/product';


declare var OdooApi: any


@IonicPage()
@Component({
  selector: 'page-showinfo',
  templateUrl: 'showinfo.html',
})
export class ShowinfoPage {

  @ViewChild('scan') myScan ;

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) {
    if (!this.myScan._isFocus){this.myScan.setFocus()};
    }


  barcodeForm: FormGroup;

  constructor(public navCtrl: NavController, public toastCtrl: ToastController, public storage: Storage, public navParams: NavParams, private formBuilder: FormBuilder, public alertCtrl: AlertController) {

  this.barcodeForm = this.formBuilder.group({scan: ['']});
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad ShowinfoPage');
  }


submitScan(){

  var values = {'model':  ['stock.quant.package', 'stock.production.lot', 'stock.location', 'product.product'], 'search_str' : this.barcodeForm.value['scan']};
  this.barcodeForm.reset();
  this.submit(values);
  }



  submit (values){

    var self = this
    var model = 'warehouse.app'
    var method = 'get_object_id'
    var confirm = false
    self.storage.get('CONEXION').then((val) => {
      if (val == null) {
        console.log('No hay conexión');
        self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          console.log('Hay conexión');
          var con = val;
          var odoo = new OdooApi(con.url, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.call(model, method, values).then(
                function (value) {
                  //AQUI DECIDO QUE HACER EN FUNCION DE LO QUE RECIBO
                 self.openinfo(value)
                 },
                function () {

                  self.presentAlert('Falla!', 'Imposible conectarse');
                  }
                );
              },
            function () {

              self.presentAlert('Falla!', 'Imposible conectarse');
              }
            );


        }

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


  openinfo(value){
    var model = value['model']
    var id = value['id']
    var page
    switch (model) {
      case 'stock.production.lot':
        page = LotPage;
        break
      case 'stock.location':
        page = LocationPage;
        break
      case 'stock.quant.package':
        page = PackagePage;
        break
      case 'product.product':
        page = ProductPage;
        break      
    }
    if (page && id){
      this.navCtrl.push(page, {model: model, id: id});
    }
  }
}
