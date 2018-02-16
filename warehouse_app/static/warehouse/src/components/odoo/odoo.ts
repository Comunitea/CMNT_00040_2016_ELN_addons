import { Component } from '@angular/core';

/**
 * Generated class for the OdooComponent component.
 *
 * See https://angular.io/api/core/Component for more info on Angular
 * Components.
 */
@Component({
  selector: 'odoo',
  templateUrl: 'odoo.html'
})
export class OdooComponent {

  text: string;

  constructor() {
    console.log('Hello OdooComponent Component');
    this.text = 'Hello World';
  }

}
