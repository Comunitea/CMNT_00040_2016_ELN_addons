import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { SelectPackagePage } from './select-package';

@NgModule({
  declarations: [
    SelectPackagePage,
  ],
  imports: [
    IonicPageModule.forChild(SelectPackagePage),
  ],
})
export class SelectPackagePageModule {}
