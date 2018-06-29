import { Component, ViewChild } from '@angular/core';
import { Nav, Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';

//Paginas

import { HomePage } from '../pages/home/home';
import { TreepickPage } from '../pages/treepick/treepick';
import { ManualPage } from '../pages/manual/manual';
import { ShowinfoPage } from '../pages/showinfo/showinfo';
import {Storage} from '@ionic/storage';
//Modal
import { AuxProvider } from '../providers/aux/aux'

import { HostListener } from '@angular/core';
import { BarcodeScanner } from '../providers/odoo-connector/barcode_scanner';



@Component({
  templateUrl: 'app.html'
})

export class MyApp {

  @ViewChild(Nav) nav: Nav;


  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) { 
    console.log("Desde treepick" + event.key)
    //if (!this.Scanner.key_press(event)) {return}
    try{  
      this.Scanner.key_press(event).then((scan)=>{
        if (scan){
          console.log('from app')
          console.log(this.nav)
          console.log(this.nav.getActive())
          console.log(this.nav.getActive().instance)
          if (this.nav && this.nav.getActive().instance['Scanner']){
            console.log("Envio " + scan + " a " + this.nav.getActive().instance)
            this.nav.getActive().instance.Scan(scan)
          }
        }
      })
    }
    catch(err){
      console.log("Desde treepick" + event.key);
      alert(err.message)
    }
  }

  rootPage:any = HomePage;
  pages: Array<{title: string, component: any, param: string}>;

  ops_filter = "Todas"/*o pendientes*/
  user={}
  constructor(public Scanner: BarcodeScanner, public platform: Platform, public statusBar: StatusBar, public splashScreen: SplashScreen, public auxProvider: AuxProvider, public storage: Storage ) {

    this.initializeApp();
    this.Scanner.on()
    this.storage.get('CONEXION').then((val) => {
			
			if (val != null && val.user){
        this.user = val.user
      }
    })
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

