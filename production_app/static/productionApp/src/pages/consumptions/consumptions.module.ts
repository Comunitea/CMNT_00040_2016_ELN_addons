import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ConsumptionsPage } from './consumptions';

@NgModule({
  declarations: [
    ConsumptionsPage,
  ],
  imports: [
    IonicPageModule.forChild(ConsumptionsPage),
  ],
})
export class ConsumptionsPageModule {}
