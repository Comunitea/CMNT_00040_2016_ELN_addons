import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

/*
  Generated class for the AuxProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
@Injectable()
export class AuxProvider {


  pick_states_visible = []
  user = {}
  filter_user = 'assigned'
  picking_types = []
  location_badge
  op_validate_button
  auto: Boolean = true
  uom_id: Boolean = true
  constructor() {
    
    this.pick_states_visible = ['partially_available', 'assigned', 'in_progress']
    this.auto = true
    this.filter_user = 'assigned'
    this.picking_types = []
  }

}
/*
  set_user (user){
    this.user = user
  }
  get_user () {
    return this.user
  }

  set_auto (auto){
    this.auto = auto
  }
  get_auto () {
    return this.auto
  }
  set_picking_types(values){
    this.picking_types = values
  }
  get_picking_types(){
    return this.picking_types
  }
  set_filter_user(new_filter){
    this.filter_user = new_filter
  }
  get_filter_user(){
    return this.filter_user
  }
  
  set_op_validate_button(op_validate_button){
    this.op_validate_button = op_validate_button
    
  }
  get_op_validate_button(){
    return this.op_validate_button
  }
}*/
