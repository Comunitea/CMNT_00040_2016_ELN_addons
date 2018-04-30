import { Component } from '@angular/core';

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

  text: string;

  constructor() {
    console.log('Hello StockLocationComponent Component');
    this.text = 'Hello World';
  }

}
