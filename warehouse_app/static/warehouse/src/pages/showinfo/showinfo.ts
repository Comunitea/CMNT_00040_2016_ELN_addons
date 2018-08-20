import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController} from 'ionic-angular';
import { ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ToastController } from 'ionic-angular';
import { HostListener } from '@angular/core';

//*Pagians
import { HomePage } from '../home/home';
import { LotPage } from '../lot/lot';
import { LocationPage } from '../location/location';
import { PackagePage } from '../package/package';
import { ProductPage } from '../product/product';
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';


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

  constructor(public navCtrl: NavController, private odoo: OdooProvider, private formBuilder: FormBuilder, public alertCtrl: AlertController) {

  this.barcodeForm = this.formBuilder.group({scan: ['']});
  }


  submitScan(){

    var values = {'model':  ['stock.quant.package', 'stock.production.lot', 'stock.location', 'product.product'], 'search_str' : this.barcodeForm.value['scan']};
    this.barcodeForm.reset();
    this.submit(values);
    }

  submit(values){
      var object_id = {}
      var model = 'warehouse.app'
      var method = 'get_scanned_object_id'
      this.odoo.execute(model, method, values).then((value)=>{
        this.openinfo(value)
      })
      .catch(() => {
        this.presentAlert('Error!', 'No se pudo conectar a odoo para recuperar el escaneo');
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
      this.navCtrl.push(page, {model: model, location_id: id,  id: id});
    }
  }
}
