
import { Component, ViewChild, Input} from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/
import {FormBuilder, FormGroup } from '@angular/forms';

import { HostListener } from '@angular/core';
import { AuxProvider } from '../../providers/aux/aux'


/**
 * Generated class for the TreepickPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
/*
  import { HomePage } from '../home/home';
  import { SlideopPage } from '../slideop/slideop';
  import { Storage } from '@ionic/storage';
  import { TreepickPage } from '../treepick/treepick'
*/

/**
 * Generated class for the StockOperationComponent component.
 *
 * See https://angular.io/api/core/Component for more info on Angular
 * Components.
 */

export interface Product {
  
}


@Component({
  selector: 'product-product',
  templateUrl: 'product-product.html'
})
export class ProductProductComponent {

  @Input() product: Product

  
  id: number
  product_id: {}
  ngOnInit() {
    this.initOperation();
  }
  
  initOperation(){
    this.id = this.product['id']
  }
  

}
