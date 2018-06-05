import { BrowserModule } from '@angular/platform-browser';
import { ErrorHandler, NgModule } from '@angular/core';
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
import { UsersModalPage } from '../pages/users-modal/users-modal';
import { ReasonsModalPage } from '../pages/reasons-modal/reasons-modal';
import { FinishModalPage } from '../pages/finish-modal/finish-modal';
import { ConsumptionsPage } from '../pages/consumptions/consumptions';

//Providers
import { OdooProvider } from '../providers/odoo/odoo';
import { ProductionProvider } from '../providers/production/production';

//Componentes
import { TimerComponent } from '../components/timer/timer';



@NgModule({
  declarations: [
    MyApp,
    HomePage,
    ProductionPage,
    ListPage,
    ChecksModalPage,
    UsersModalPage,
    ReasonsModalPage,
    FinishModalPage,
    ConsumptionsPage,
    TimerComponent
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
    UsersModalPage,
    ReasonsModalPage,
    ConsumptionsPage,
    FinishModalPage,
  ],
  providers: [
    StatusBar,
    SplashScreen,
    {provide: ErrorHandler, useClass: IonicErrorHandler},
    File,
    Network,
    OdooProvider,
    ProductionProvider,
  ]
})
export class AppModule {}
