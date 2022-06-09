import { Component } from '@angular/core';
import { NavController, ViewController } from 'ionic-angular';

@Component({
    selector: 'page-calculator',
    templateUrl: 'calculator.html'
})
export class CalculatorModalPage {
    display = 0;
    memory = 0;
    state = 'number';
    operator = '+';
    decimal = false;
    decimals = 0;

    clickNumber(n: number) {
        switch (this.state) {
            case 'number':
                if (this.decimal) {
                    this.decimals++;
                    this.display = this.display + n * Math.pow(10, -this.decimals);
                } else {
                    this.display = this.display * 10 + n;
                }
                break;
            case 'operator':
                this.display = n;
                this.state = 'number';
                break;
            case 'result':
                this.memory = 0;
                this.display = n;
                this.state = 'number';
        }
    }

    clickOperator(o: string) {
        if (this.state != 'operator') {
            this.calculate();
        }
        this.operator = o;
        this.memory = this.display;
        this.state = 'operator';
    }

    calculate() {
        this.display = eval('' + this.memory + this.operator + '(' + this.display + ')');
        this.memory = 0;
        this.state = 'result';
        this.operator = '+';
        this.decimal = false;
        this.decimals = 0;
    }

    resetLastNumber() {
        this.display = 0;
        this.state = 'number';
        this.decimal = false;
        this.decimals = 0;
    }

    reset() {
        this.display = 0;
        this.memory = 0;
        this.state = 'number';
        this.operator = '+';
        this.decimal = false;
        this.decimals = 0;
    }

    clickBackspace() {
        if (this.decimal) {
            this.decimals--;
            if (this.decimals == 0) {
                this.decimal = false;
            }
            this.display = Math.floor(this.display * Math.pow(10, this.decimals)) / Math.pow(10, this.decimals);
        } else {
            this.display = this.display / 10 ^ 0;
        }
        this.state = 'number';
        //this.operator = '+';
    }

    changeSign() {
        this.display = this.display * -1;
    }

    setDecimal() {
        this.decimal = true;
    }

    constructor(public navCtrl: NavController, public viewCtrl: ViewController) {
    }

    ionViewDidLoad() {
        console.log('ionViewDidLoad CalculatorModalPage');
    }

    closeModal() {
        this.viewCtrl.dismiss({});
    }

    confirmModal() {
        this.viewCtrl.dismiss({ 'display_value': this.display });
    }

}
