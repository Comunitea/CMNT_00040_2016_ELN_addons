import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { AuxProvider } from '../../providers/aux/aux'
/**
 * Generated class for the SettingsPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */

@IonicPage()
@Component({
  selector: 'page-settings',
  templateUrl: 'settings.html',
})
export class SettingsPage {
  public preferences:any;
  public PREF_DISCOVERABLE:string;
  public PREF_NOTIFY_MESSAGES:string;
  public PREF_NOTIFY_INVITES:string;

  constructor(public navCtrl: NavController, public navParams: NavParams, public settings: AuxProvider) {
    this.preferences = {};

    this.PREF_DISCOVERABLE = AuxProvider.PREF_DISCOVERABLE;
    this.PREF_NOTIFY_MESSAGES = AuxProvider.PREF_NOTIFY_MESSAGES;
    this.PREF_NOTIFY_INVITES = AuxProvider.PREF_NOTIFY_INVITES;
  }

  ionViewDidLoad() {
    console.log('ionViewDidLoad SettingsPage');
  }
  public ionViewWillEnter(){
    this.preferences[AuxProvider.PREF_DISCOVERABLE]
      = this.settings.getPreference(AuxProvider.PREF_DISCOVERABLE);
    this.settings[AuxProvider.PREF_NOTIFY_MESSAGES]
      = this.settings.getPreference(AuxProvider.PREF_NOTIFY_MESSAGES);
    this.preferences[AuxProvider.PREF_NOTIFY_INVITES]
      = this.settings.getPreference(AuxProvider.PREF_NOTIFY_INVITES);
  
  }
  
  public changePreference(event, key){
    this.settings.setPreference(key, event.checked);
    
  }
}
