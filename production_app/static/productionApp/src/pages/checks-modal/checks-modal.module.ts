import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { ChecksModalPage } from './checks-modal';

@NgModule({
  declarations: [
    ChecksModalPage,
  ],
  imports: [
    IonicPageModule.forChild(ChecksModalPage),
  ],
})
export class ChecksModalPageModule {}
