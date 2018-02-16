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
import { AuxProvider } from '../providers/aux/aux'
@Component({
  templateUrl: 'app.html'
})

export class MyApp {

  @ViewChild(Nav) nav: Nav;
  
  rootPage:any = HomePage;
  pages: Array<{title: string, component: any, param: string}>;

  constructor(public platform: Platform, public statusBar: StatusBar, public splashScreen: SplashScreen, public Configs: AuxProvider ) {
    
    this.initializeApp();
    this.Configs = new AuxProvider()
    this.pages = [
      { title: 'Mis albaranes', component: HomePage , param: 'assigned'},
      { title: 'Sin asignar', component: TreepickPage, param: 'no_assigned' },
      { title: 'Mov. Manual', component: ManualPage, param: 'new_move'},
      { title: 'Info Etiqueta', component: HomePage, param: 'info'},
      { title: 'Borrar Datos', component: HomePage, param: 'delete'},
      { title: 'Imprimir etiqueta', component: HomePage, param: 'print_tag'},

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
    this.nav.setRoot(page.component, {user: page.param}) ;
    
  }
  
}

