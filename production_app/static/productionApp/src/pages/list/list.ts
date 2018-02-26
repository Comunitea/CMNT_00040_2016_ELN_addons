import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

@Component({
  selector: 'page-list',
  templateUrl: 'list.html'
})
export class ListPage {
    // selectedItem: any;
    // icons: string[];
    // items: Array<{title: string, note: string, icon: string}>;

    // constructor(public navCtrl: NavController, public navParams: NavParams) {
    //   // If we navigated to this page, we will have an item available as a nav param
    //   this.selectedItem = navParams.get('item');

    //   // Let's populate this page with some filler content for funzies
    //   this.icons = ['flask', 'wifi', 'beer', 'football', 'basketball', 'paper-plane',
    //   'american-football', 'boat', 'bluetooth', 'build'];

    //   this.items = [];
    //   for (let i = 1; i < 11; i++) {
    //     this.items.push({
    //       title: 'Item ' + i,
    //       note: 'This is item #' + i,
    //       icon: this.icons[Math.floor(Math.random() * this.icons.length)]
    //     });
    //   }
    // }

    // itemTapped(event, item) {
    //   // That's right, we're pushing to ourselves!
    //   this.navCtrl.push(ListPage, {
    //     item: item
    //   });
    // }

    num:number;
    mayorMenor: string = '...';
    numSecret: number = this.numAleatorio(0,100);

    constructor(public navCtrl: NavController){

    }

    numAleatorio(a,b){
        return Math.round(Math.random()*(b-a)+parseInt(a));
    }

    compruebaNumero(){
        if(this.num){
            if(this.numSecret < this.num){
                this.mayorMenor = 'menor';
            }
             else if(this.numSecret > this.num){
            this.mayorMenor = 'mayor';
            }
        else{
            this.mayorMenor = 'igual';
        }
        }
       
    }

    reinicia(){
        // reiniciamos las variables
        this.num = null;
        this.mayorMenor = '...';
        this.numSecret = this.numAleatorio(0,100);
    }

}
