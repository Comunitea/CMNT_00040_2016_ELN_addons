import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { FinishModalPage } from './finish-modal';

@NgModule({
  declarations: [
    FinishModalPage,
  ],
  imports: [
    IonicPageModule.forChild(FinishModalPage),
  ],
})
export class FinishModalPageModule {}
