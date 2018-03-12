import { BrowserModule } from '@angular/platform-browser';
import { enableProdMode, ErrorHandler, NgModule } from '@angular/core';
import { IonicApp, IonicErrorHandler, IonicModule } from 'ionic-angular';


import { SplashScreen } from '@ionic-native/splash-screen';
import { StatusBar } from '@ionic-native/status-bar';


import { HttpModule } from '@angular/http';
import { IonicStorageModule } from '@ionic/storage';
import { Network } from '@ionic-native/network';
import { File } from '@ionic-native/file';

//Paginas
import { MyApp } from './app.component';
import { HomePage } from '../pages/home/home';
import { ProductionPage } from '../pages/production/production';
import { ListPage } from '../pages/list/list';
import { ChecksModalPage } from '../pages/checks-modal/checks-modal';
import { OdooProvider } from '../providers/odoo/odoo';




@NgModule({
  declarations: [
    MyApp,
    HomePage,
    ProductionPage,
    ListPage,
    ChecksModalPage,
  ],
  imports: [
    BrowserModule,
    HttpModule,
    IonicModule.forRoot(MyApp),
    IonicStorageModule.forRoot()    
  ],
  bootstrap: [IonicApp],

  entryComponents: [
    MyApp,
    HomePage,
    ProductionPage,
    ListPage,
    ChecksModalPage,
  ],
  providers: [
    StatusBar,
    SplashScreen,
    {provide: ErrorHandler, useClass: IonicErrorHandler},
    File,
    Network,
    OdooProvider,
  ]
})
export class AppModule {}
