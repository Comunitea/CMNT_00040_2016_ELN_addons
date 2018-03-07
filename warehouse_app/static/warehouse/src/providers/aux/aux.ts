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
  filter_user = 'assigned'
  constructor() {

    this.pick_states_visible = ['partially_available', 'assigned']
    console.log('Hello AuxProvider Provider');
  }

  set_filter_user(new_filter){
    this.filter_user = new_filter
  }
  get_filter_user(){
    return this.filter_user
  }
  set_pick_states_visible (new_states){
    var self = this
    self.pick_states_visible = new_states
  }
  get_pick_states_visible (){
    var self = this;
    return self.pick_states_visible
  }
  
  
}
