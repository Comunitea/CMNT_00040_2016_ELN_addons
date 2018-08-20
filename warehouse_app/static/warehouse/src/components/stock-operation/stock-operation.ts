
import { Component, ViewChild, Input, Output, EventEmitter } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
/*import { PROXY } from '../../providers/constants/constants';*/
import {FormBuilder, FormGroup } from '@angular/forms';

import { HostListener } from '@angular/core';
import { AuxProvider } from '../../providers/aux/aux'
import { SlideopPage} from '../../pages/slideop/slideop'

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

export interface PackOperation {
  id : number
  product_id: {};
  location_id: {};
  location_dest_id: {};
  pda_done : boolean;
  pda_checked: boolean;
  qty_done : number;
  product_qty: number;
  lot_id: {};
  package_id: {};
  result_package_id: {};
  index: number
}
export interface Pick {}


@Component({
  selector: 'stock-operation',
  templateUrl: 'stock-operation.html'
})
export class StockOperationComponent {

  @Input() stock_operation: PackOperation
  @Input() pick: Pick
  @Input() whatOps: String
  

  @Output() notify: EventEmitter <Boolean> = new EventEmitter<Boolean>();

  op_val: {'id': 0, 'do_op': false}
  pda_done: Boolean
  id: number
  product_id: {}
  process_from_tree: Boolean
  constructor (private navCtrl:NavController){

  }
  ngOnInit() {
    this.initOperation();
  }
  
  initOperation(){
    this.pda_done = this.stock_operation.pda_done
    this.id = this.stock_operation.id
    this.process_from_tree = this.pick['picking_type_id']['process_from_tree']
  }
   
  filter_picks(){
    let filter: boolean
    let filter_picks = []
    if (this.whatOps=='Todas') {
      filter_picks = this.pick['pack_operation_ids']
      return filter_picks
    }
    else if (this.whatOps=='Realizadas'){
      filter=true
    }
    else {
      filter=false
    }
    filter_picks = this.pick['pack_operation_ids'].filter(op => op.pda_done == filter)
    return filter_picks

  }

  doOp(do_id: Boolean){
    this.notify.emit(do_id)
  }
  openOp(op_id, op_id_index){
    let pick =  {'id': this.pick['id'], 'model': this.pick['model'], 'name': this.pick['name'], 'user_id': this.pick['user_id']}
    let val =  {op_id: this.id, index: this.stock_operation.index, ops: this.filter_picks(), pick: pick}
    this.navCtrl.setRoot(SlideopPage, val)
  }
}
