import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ConsumptionListModalPage } from './consumption-list-modal';

@NgModule({
  declarations: [
    ConsumptionListModalPage,
  ],
  imports: [
    IonicPageModule.forChild(ConsumptionListModalPage),
  ],
})
export class ConsumptionListModalPageModule {}
