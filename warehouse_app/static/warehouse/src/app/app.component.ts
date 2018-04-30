import { Component, ViewChild } from '@angular/core';
import { Nav, Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

//Paginas

import { HomePage } from '../pages/home/home';
import { TreepickPage } from '../pages/treepick/treepick';
import { TreeopsPage } from '../pages/treeops/treeops';
import { SlideopPage } from '../pages/slideop/slideop';
import { ManualPage } from '../pages/manual/manual';
import { ShowinfoPage } from '../pages/showinfo/showinfo';

//Modal

import { SelectLotPage } from '../pages/select-lot/select-lot'

import { ProductPage} from '../pages/product/product'
import { LotPage} from '../pages/lot/lot'
import { PackagePage} from '../pages/package/package'
import { LocationPage} from '../pages/location/location'

import { OdooProvider } from  '../providers/odoo-connector/odoo-connector'
import { AuxProvider } from '../providers/aux/aux'
import { AppSoundProvider } from '../providers/app-sound/app-sound'





@Component({
  templateUrl: 'app.html'
})

export class MyApp {

  @ViewChild(Nav) nav: Nav;
  
  rootPage:any = HomePage;
  pages: Array<{title: string, component: any, param: string}>;

  ops_filter = "Todas"/*o pendientes*/ 

  constructor(public platform: Platform, public statusBar: StatusBar, public splashScreen: SplashScreen, public auxProvider: AuxProvider ) {
    
    this.initializeApp();
    this.pages = [
      { title: 'Mis trabajos', component: HomePage , param: 'assigned'},
      { title: 'Sin asignar', component: TreepickPage, param: 'no_assigned'},
      { title: 'Manual', component: ManualPage, param: 'new_move'},
      { title: 'Etiqueta', component: ShowinfoPage, param: 'info'},
      { title: 'Borrar Datos', component: HomePage, param: 'delete'},
      { title: 'Imprimir', component: HomePage, param: 'print_tag'},
    ]
    }

    initializeApp(){  
    this.platform.ready().then(() => {
      // Okay, so the platform is ready and our plugins are available.
      // Here you can do any higher level native things you might need.
      this.statusBar.styleDefault();
      this.splashScreen.hide();
    });
  }

  openPage(page) {
    // Reset the content nav to have just this page
    // we wouldn't want the back button to show in this scenario
    if (page.param=='assigned') {this.auxProvider.filter_user = 'assigned';}
    if (page.param=='no_assigned') {this.auxProvider.filter_user = 'no_assigned';}
    this.nav.setRoot(page.component, {filter_user: page.param}) ;
    
  }
  
}

