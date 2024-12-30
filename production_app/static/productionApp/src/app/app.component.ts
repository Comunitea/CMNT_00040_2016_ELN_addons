import { Component, ViewChild } from '@angular/core';
import { Nav, Platform } from 'ionic-angular';
import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
//import { Insomnia } from '@ionic-native/insomnia';

import { HomePage } from '../pages/home/home';
import { ListPage } from '../pages/list/list';

@Component({
    templateUrl: 'app.html'
})
export class MyApp {
    @ViewChild(Nav) nav: Nav;

    rootPage: any = HomePage;

    pages: Array<{ title: string, component: any }>;

    constructor(public platform: Platform,
        //private insomnia: Insomnia,
        public statusBar: StatusBar,
        public splashScreen: SplashScreen) {
        this.initializeApp();

        this.pages = [
            { title: 'Lista de líneas', component: ListPage },
        ];

    }

    initializeApp() {
        this.platform.ready().then(() => {
            // Okay, so the platform is ready and our plugins are available.
            // Here you can do any higher level native things you might need.

            // Mantener el dispositivo despierto globalmente
            //this.insomnia.keepAwake().then(
            //    () => console.log('keepAwake success'),
            //    () => console.log('keepAwake error')
            //);

            // Configuración inicial de la aplicación
            this.statusBar.styleDefault();
            this.splashScreen.hide();
        });
    }

    openPage(page) {
        // Reset the content nav to have just this page
        // we wouldn't want the back button to show in this scenario
        this.nav.setRoot(page.component);
    }
    // Permitimos el modo suspensión cuando la aplicación se cierra
    //ngOnDestroy() {
    //    this.insomnia.allowSleepAgain().then(
    //        () => console.log('allowSleep success'),
    //        () => console.log('allowSleep error')
    //    );
    //}
}
