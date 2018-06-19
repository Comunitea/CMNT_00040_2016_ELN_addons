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
        console.log("Me llega " + event.which + '[' + event.key + ' ]')
        let e = event.key
        if(!this.state){ //ignore returns

        }
        else{
            if(this.timeStamp + 1000 < new Date().getTime()){
                this.code = "";
            }
            this.timeStamp = new Date().getTime();
            clearTimeout(this.timeout);
            if (event.which >= 32) {
                this.code += e;
            }
            
            this.timeout = new Promise ((resolve) => {
                setTimeout(()=>{
                if(this.code && this.code.length >= 4){
                    console.log('Devuelvo ' + this.code)
                    let scan = this.code
                    this.code = ''
                    console.log (scan + " ----> " + this.code)
                    resolve(scan);
                };
                },2000);

            })
        }
        return this.timeout
    }
    
}
