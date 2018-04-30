import { Component } from '@angular/core';

/**
 * Generated class for the StockPickingComponent component.
 *
 * See https://angular.io/api/core/Component for more info on Angular
 * Components.
 */
@Component({
  selector: 'stock-picking',
  templateUrl: 'stock-picking.html'
})
export class StockPickingComponent {

  text: string;

  constructor() {
    console.log('Hello StockPickingComponent Component');
    this.text = 'Hello World';
  }

}
