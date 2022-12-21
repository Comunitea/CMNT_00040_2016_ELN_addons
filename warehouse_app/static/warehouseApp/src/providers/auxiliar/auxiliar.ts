//import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';
/*
  Generated class for the AuxProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
@Injectable()
export class AuxProvider {


    static get PREF_INITIALIZED() { return 'preferencesInitialized'; }
    static get PREF_DISCOVERABLE() { return 'pref_discoverable'; }
    static get PREF_NOTIFY_MESSAGES() { return 'pref_notification_messages'; }
    static get PREF_NOTIFY_INVITES() { return 'pref_notification_invites'; }

    public _preferences: any;
    pick_states_visible = []
    user = {}
    filter_user = 'assigned'
    picking_types = []
    location_badge
    op_validate_button
    auto: Boolean = true
    uom_id: Boolean = true

    constructor(public settings: Storage) {

        this._preferences = {};
        this.auto = true
        this.filter_user = 'assigned'
        this.picking_types = []
    }
    public initializePreferences() {
        console.log('initializePreferences');
        this.settings.get(AuxProvider.PREF_INITIALIZED).then((result) => {
            if (result == null || result == false) {
                console.log('initializePreferences with default values');
                this.settings.set(AuxProvider.PREF_INITIALIZED, true);
                this.settings.set(AuxProvider.PREF_DISCOVERABLE, true);
                this.settings.set(AuxProvider.PREF_NOTIFY_MESSAGES, true);
                this.settings.set(AuxProvider.PREF_NOTIFY_INVITES, true);

                //initialize in memory preferences
                this._preferences[AuxProvider.PREF_DISCOVERABLE] = true;
                this._preferences[AuxProvider.PREF_NOTIFY_MESSAGES] = true;
                this._preferences[AuxProvider.PREF_NOTIFY_INVITES] = true;
            } else {
                console.log('preferences obtained from storage');
                let prefs =
                    [
                        AuxProvider.PREF_DISCOVERABLE,
                        AuxProvider.PREF_NOTIFY_MESSAGES,
                        AuxProvider.PREF_NOTIFY_INVITES
                    ];

                let thisRef = this;
                this._getAllPreferences(prefs).then(function (results) {
                    //initialize in memory preferences
                    for (let i = 0; i < prefs.length; i++) {
                        thisRef._preferences[prefs[i]] = results[i];
                    }
                }, function (err) {
                    // If any of the preferences fail to read, err is the first error
                    console.log(err);
                });
            }
        });
    }

    public getPreference(key) {
        return this._preferences[key];
    }

    public setPreference(key, value) {
        this._preferences[key] = value;//update pref in memory
        this.settings.set(key, value);//update pref in db
    }

    public _getAllPreferences(prefs) {
        return Promise.all(prefs.map((key) => {
            return this.settings.get(key);
        }));
    }

    public _getPreference(key) {
        return this.settings.get(key);
    }

}