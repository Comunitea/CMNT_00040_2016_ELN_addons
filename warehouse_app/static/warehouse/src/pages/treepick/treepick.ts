import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController, ToastController } from 'ionic-angular';

import { ViewChild } from '@angular/core';
//import { HostListener } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';

/*import { PROXY } from '../../providers/constants/constants';*/

/**
 * Generated class for the TreepickPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
import { HomePage } from '../../pages/home/home';
import { TreeopsPage } from '../../pages/treeops/treeops';
import { Storage } from '@ionic/storage';


import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';
//import { BarcodeScanner } from '../../providers/odoo-connector/barcode_scanner';
import { AuxProvider } from '../../providers/aux/aux'


@IonicPage()
@Component({
  selector: 'page-treepick',
  templateUrl: 'treepick.html',
})
export class TreepickPage {


  @ViewChild('scan') myScan ;
   
  barcodeForm: FormGroup;
  input   

  picks = [];
  cargar = true;
  fields = [];
  domain = [];
  uid = 0
  picking_types = [];
  domain_state = []
  domain_types = []
  states_show = []
  user= ''
  picking_type_id = 0
  login = false;
  filter_user = ''
  waves: boolean

  constructor(public navCtrl: NavController, private formBuilder: FormBuilder, public navParams: NavParams, public alertCtrl: AlertController, private storage: Storage, public auxProvider: AuxProvider,  private odoo: OdooProvider, private toast: ToastController) {
    
    this.barcodeForm = this.formBuilder.group({scan: ['']});
    this.states_show = auxProvider.pick_states_visible;
    if (this.navCtrl.getPrevious()){this.navCtrl.remove(this.navCtrl.getPrevious().index, 2);}
    this.waves = true
    this.uid = 0
    this.picks = [];
    this.picking_types = [];
    this.picking_type_id = 0
    this.domain_types = []
    this.filter_user = this.auxProvider.filter_user || 'assigned'
    this.domain_state = ['state', 'in', this.states_show]
    this.fields = ['id', 'name', 'state', 'partner_id', 'location_id', 'location_dest_id', 'picking_type_id', 'user_id', 'allow_validate'];
    this.filter_picks(0) ;

    setTimeout(() => {
      this.myScan.setFocus();
    },100);
    }
  

  logOut(){this.navCtrl.setRoot(HomePage, {borrar: true, login: null});}

  
  error_odoo(str){
    this.cargar = false;
    this.login = false;
    this.presentAlert('Error!', 'No al conectarse a odoo en '+str);
  }
  get_waves(domain){
    this.cargar = true
    console.log(domain)
    //domain.push(['picking_state','=','assigned'])
    this.odoo.searchRead('stock.picking.wave', domain, this.fields, 0, 0).then((value) =>{
      if (value) {
        for (var key in value) {
          value[key]['model']='stock.picking.wave';
          this.picks.push(value[key]);          
        }
        this.storage.set('stock.picking', this.picks);
        }
      else{
        
        this.presentAlert('Aviso!', 'No se ha recuperado ningún albarán');
      }
      this.cargar=false
    })
    .catch(() => {
      this.error_odoo('get_picks')
    });	
  }

  filter_picks(picking_type_id=0, domain=[]){
    domain.push(['show_in_pda', '=', true])

    if (picking_type_id==0)
      {domain.push(['picking_type_id', '!=', false]);}
    else 
      {domain.push(['picking_type_id', '=', picking_type_id]);}
    
    domain.push(['show_in_pda', '=', true]);
    domain.push(['pack_operation_exist', '!=', false])
    domain.push(this.domain_state)

    
    if (this.filter_user=='assigned') {domain.push(['user_id', '=', this.odoo.uid]);} else {domain.push(['user_id','=', false]);}
    //domain = [self.domain_types]

    
    var model = 'warehouse.app'
    var method = 'get_picks_info'
    var values = {'types': true, 'picks': true, 'waves': true, 'domain': domain}
    
  
    this.odoo.execute(model, method, values).then((value)=>{
      
      if (value) {
        //recupero types
        /*
        this.picking_types=[]
        let types = value['types']
        for (var key in types) {
          this.picking_types.push(types[key]);
        }
        
        //recupero
        this.picks = []
        let picks = value['types']
        for (var key in picks) {
          this.picks.push(picks[key]);
        }*/
        if (value['types']){
          this.picking_types = value['types']
        }
        if (value['picks']){
          this.picks = value['picks']
        }
        setTimeout(() => {
          this.myScan.setFocus();
        },100);

        }
      else{ this.cargar=false
        this.presentAlert('Aviso!', 'No se ha recuperado ningún tipo de alabrán');
      }
      this.cargar=false
    })
    .catch(() => {
      this.error_odoo('get_picking_types')
    });	

    
  }

  presentAlert(titulo, texto) {
    const alert = this.alertCtrl.create({
        title: titulo,
        subTitle: texto,
        buttons: ['Ok']
    });
    alert.present();
  }

  ionViewDidLoad() {

  }
  showtreeop_ids(pick_id, is_wave = false) {
    let model = is_wave && 'stock.picking.wave' || 'stock.picking'
    this.navCtrl.setRoot(TreeopsPage, {picking_id: pick_id, model: model});
  }

  doAsign(pick_id){
    this.filter_user='assigned'
    this.change_pick_value(pick_id, 'user_id', this.uid);
  }
  doDeAsign(pick_id){ 
    this.filter_user='no_assigned'
    this.change_pick_value(pick_id, 'user_id', false);
  }

  change_pick_value(id, field, new_value){

    var model = 'stock.picking'
    var method = 'change_pick_value'
    var values = {'id': id, 'field': field, 'value': new_value}
    var object_id
    this.cargar=true
    this.odoo.write(model, id, {field, new_value}).then((value)=>{
      this.filter_picks();
    })
    .catch(() => {
      this.error_odoo('get_picking_types')
    });	
  }
 
  doTransfer(id){
    var model = 'stock.picking'
    var method = 'doTransfer'
    var values = {'id': id}
    this.odoo.execute(model, method, values).then((value)=>{
      if (value) {
        this.filter_picks()
      }
      else {
        this.presentAlert('Error!', 'No se ha podido transferir el albarán');
      }
    })
    .catch(() => {
      this.error_odoo('get_picking_types')
    });	
}

find_pick(scan){
  let val = {}
  for (var op in this.picks){
    var opObj = this.picks[op];
    console.log(opObj);
    //Busco por nombre en la lista
    if (opObj['name'] == scan){
      val = {picking_id : opObj['id'], model : opObj['is_wave'] && 'stock.picking.wave' || 'stock.picking'}
      return val
    }
  }
  return false  
}

Scan(scan){
  this.barcodeForm.reset()
  let val = this.find_pick(scan)
  if (val){
    console.log(val)    
    this.navCtrl.setRoot(TreeopsPage, val);
  }
}

submitScan(){
  let scan = this.barcodeForm.value['scan']
  return this.Scan(scan)
  }

  presentToast(message, duration=30, position='top') {
    let toast = this.toast.create({
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

