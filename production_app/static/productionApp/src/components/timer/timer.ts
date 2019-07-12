import { Component, Input } from '@angular/core';

export interface CountupTimer {
    seconds: number;
    secondsCounter: number;
    runTimer: boolean;
    hasStarted: boolean;
    hasFinished: boolean;
    displayTime: string;
}

@Component({
    selector: 'timer',
    templateUrl: 'timer.html'
})
export class TimerComponent {

    @Input() timeInSeconds: number;
    timer: CountupTimer;
    intervalObj: any;

    ngOnInit() {
        this.initTimer();
    }

    hasFinished() {
        return this.timer.hasFinished;
    }

    initTimer() {
    clearInterval(this.intervalObj);
    if (!this.timeInSeconds) { this.timeInSeconds = 0; }

    this.timer = <CountupTimer>{
        seconds: this.timeInSeconds,
        runTimer: false,
        hasStarted: false,
        hasFinished: false,
        secondsCounter: this.timeInSeconds
    };

    this.timer.displayTime = this.getSecondsAsDigitalClock(this.timer.secondsCounter);
    }

    startTimer() {
        this.timer.hasStarted = true;
        this.timer.runTimer = true;
        this.timerTick();
    }

    pauseTimer() {
        clearInterval(this.intervalObj);
        this.timer.runTimer = false;
    }

    resumeTimer() {
        this.startTimer();
    }

    restartTimer(){
        this.pauseTimer();
        this.initTimer()
        this.startTimer();
    }

    timerTick() {
        this.intervalObj = setInterval(() => {
            if (!this.timer.runTimer) { return; }
                this.timer.secondsCounter++;
                this.timer.displayTime = this.getSecondsAsDigitalClock(this.timer.secondsCounter);
            if (this.timer.secondsCounter > 0) {
            } else {
                this.timer.hasFinished = true;
            }
        }, 1000);
    }

    getSecondsAsDigitalClock(inputSeconds: number) {
        const secNum = parseInt(inputSeconds.toString(), 10); // don't forget the second param
        const hours = Math.floor(secNum / 3600);
        const minutes = Math.floor((secNum - (hours * 3600)) / 60);
        const seconds = secNum - (hours * 3600) - (minutes * 60);
        let hoursString = '';
        let minutesString = '';
        let secondsString = '';
        hoursString = (hours < 10) ? '0' + hours : hours.toString();
        minutesString = (minutes < 10) ? '0' + minutes : minutes.toString();
        secondsString = (seconds < 10) ? '0' + seconds : seconds.toString();
        return hoursString + ':' + minutesString + ':' + secondsString;
    }

}

