import { Injectable } from '@angular/core';
import { ToastController } from 'ionic-angular';

@Injectable()
export class BarcodeScanner {

    code = ""
    timeStamp  = 0
    timeout = null
    state = false
    constructor(private toastCtrl: ToastController) {
        this.reset_scan()
    }
    reset_scan(){
        this.code = ""
        this.timeStamp = 0
        this.timeout = null
    }
    on(){
        this.state=true
        this.reset_scan()
    }
    off(){
        this.state=false
        this.reset_scan()
    }

    key_press(event){
        let st = ("Me llega " + event.which + '[' + event.key + ' ]' + " y tengo " + this.code)

        this.presentToast(st)
        let e = event.key.substring(0,1)
        this.presentToast(e)
        if(!this.state){ //ignore returns

        }
        else{
            //este 250 es el tiempo en resetear sin pulsaciones
            if(this.timeStamp + 100 < new Date().getTime()){
                this.code = "";
            }
            this.timeStamp = new Date().getTime();
            clearTimeout(this.timeout);
            if (event.which >= 48) {
                e = event.which == 111 && "-" || e;
                this.code += e;
            }
            
            
            this.timeout = new Promise ((resolve) => {
                setTimeout(()=>{
                if(this.code && this.code.length >= 4){
                    console.log('Devuelvo ' + this.code)
                    let scan = this.code.replace('-','/')
                    this.code = ''
                    console.log (scan + " ----> " + this.code)
                    resolve(scan);
                };
                },100);
                // este 500 es el tiempo que suma pulsaciones
            })
        }
        return this && this.timeout
    }
    
presentToast(message, duration=30, position='top') {
    let toast = this.toastCtrl.create({
      message: message,
      duration: duration,
      position: position
    });
  
    toast.onDidDismiss(() => {
      console.log('Dismissed toast');
    });
  
    toast.present();
  }
}
