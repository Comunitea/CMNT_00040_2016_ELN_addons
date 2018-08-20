import { Component } from '@angular/core';

/**
 * Generated class for the StockPackageComponent component.
 *
 * See https://angular.io/api/core/Component for more info on Angular
 * Components.
 */
@Component({
  selector: 'stock-package',
  templateUrl: 'stock-package.html'
})
export class StockPackageComponent {

  text: string;

  constructor() {
    console.log('Hello StockPackageComponent Component');
    this.text = 'Hello World';
  }

}
