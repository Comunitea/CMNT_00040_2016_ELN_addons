import { Component } from '@angular/core';

/**
 * Generated class for the ProductionLotComponent component.
 *
 * See https://angular.io/api/core/Component for more info on Angular
 * Components.
 */
@Component({
  selector: 'production-lot',
  templateUrl: 'production-lot.html'
})
export class ProductionLotComponent {

  text: string;

  constructor() {
    console.log('Hello ProductionLotComponent Component');
    this.text = 'Hello World';
  }

}
