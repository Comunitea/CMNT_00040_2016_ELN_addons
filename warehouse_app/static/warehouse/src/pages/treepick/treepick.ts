import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';

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
import { BarcodeScanner } from '../../providers/odoo-connector/barcode_scanner';
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

  constructor(public Scanner: BarcodeScanner, public navCtrl: NavController, private formBuilder: FormBuilder, public navParams: NavParams, public alertCtrl: AlertController, private storage: Storage, public auxProvider: AuxProvider,  private odoo: OdooProvider) {
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
    this.get_picking_types();
    this.filter_picks(0) ;
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

  get_picks(){
    
    this.cargar = true
    this.picks=[];
    let domain = [['show_in_pda', '=', true]];
    //domain.push(['pack_operation_exist', '!=', false])

    if (this.domain_state!=[]) {domain.push(this.domain_state);}
    if (this.domain_types!=[]) {domain.push(this.domain_types);}
    if (this.filter_user=='assigned') {domain.push(['user_id', '=', this.odoo.uid]);} else {domain.push(['user_id','=', false]);}
    //domain = [self.domain_types]

    console.log(domain)
    this.odoo.searchRead('stock.picking', domain, this.fields, 0, 0).then((value) =>{
      this.picks=[];
      if (value) {
        for (var key in value) {
          value[key]['model']='stock.picking';
          this.picks.push(value[key]);
        }
        if (this.waves){this.get_waves(domain)}
        this.storage.set('stock.picking', value);
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

  get_picking_types(){
    let domain = [['show_in_pda', '=', true]];
    let fields = ['id', 'name', 'short_name']


    this.odoo.searchRead('stock.picking.type', domain, fields, 0,0).then((value) =>{
      this.picking_types = [];
      if (value) {
        for (var key in value) {
          this.picking_types.push(value[key]);
        }
        this.storage.set('stock.picking.type', value);
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

  filter_picks(picking_type_id=0, domain=[]){
    
    if (Boolean(picking_type_id)){
      this.picking_type_id = picking_type_id}
    if (this.picking_type_id==0)
      {this.domain_types =  ['picking_type_id', '!=', false];}
    else 
      {this.domain_types = ['picking_type_id', '=', this.picking_type_id];}
    this.get_picks();
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
  showtreeop_ids(pick_id, model='stock.picking') {
    this.navCtrl.push(TreeopsPage, {picking_id: pick_id, model: model});
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

Scan(scan){
  this.cargar=true
  let domain = [['name', '=', scan]]
  let model = 'stock.picking'
  let fields = ['id']
  console.log(domain)
  this.odoo.searchRead(model, domain, fields, 0,0).then((value)=>{
    console.log(value)
    if (value && value[0]){
      this.navCtrl.push(TreeopsPage, {picking_id: value[0]['id'], model: model});
    }
    else {
      //busco wave
      model = 'stock.picking.wave'
      this.odoo.searchRead(model, domain, fields, 0,0).then((value)=>{
        console.log(value)
        if (value && value[0]){
          this.navCtrl.push(TreeopsPage, {picking_id: value[0]['id'], model: model});
        }
        else {
          this.presentAlert('Aviso !', 'No se ha encontrado el albarán: ' + scan);
          this.cargar=false
        }
      })
    }
  })
  .catch(() => {
    this.error_odoo('Error al recuperar el albarán escaneado')
  });	


}


submitScan(){
  this.cargar=true
  let domain = [['name', '=',  this.barcodeForm.value['scan']]]
  let model = 'stock.picking'
  let fields = 'id'

  this.odoo.searchRead(model, domain, fields, 0,0).then((value)=>{
    if (value && value[0]){
      this.navCtrl.push(TreeopsPage, {picking_id: value[0]['id'], model: 'stock.picking'});
    }
    else {
      this.presentAlert('Aviso !', 'No se ha encontrado el albarán: ' + this.barcodeForm.value['scan']);
    }

  })
  .catch(() => {
    this.error_odoo('Error al recuperar el albarán escaneado')
  });	


}
}

