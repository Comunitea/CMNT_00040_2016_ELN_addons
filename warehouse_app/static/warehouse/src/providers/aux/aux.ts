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
  constructor() {

    this.pick_states_visible = ['partially_available', 'assigned']
    console.log('Hello AuxProvider Provider');
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
