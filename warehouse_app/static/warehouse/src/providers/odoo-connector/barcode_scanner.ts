import { Injectable } from '@angular/core';


@Injectable()
export class BarcodeScanner {

    code = ""
    timeStamp  = 0
    timeout = null
    state = false
    constructor() {
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
        console.log("Me llega " + event.which + '[' + event.key + ' ]' + " y tengo " + this.code)
        let e = event.key.substring(0,1)
        if(!this.state){ //ignore returns

        }
        else{
            //este 250 es el tiempo en resetear sin pulsaciones
            if(this.timeStamp + 500 < new Date().getTime()){
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
                if(this.code && this.code.length >= 5){
                    console.log('Devuelvo ' + this.code)
                    let scan = this.code.replace('-','/')
                    this.code = ''
                    console.log (scan + " ----> " + this.code)
                    resolve(scan);
                };
                },500);
                // este 500 es el tiempo que suma pulsaciones
            })
        }
        return this.timeout
    }
    
}
