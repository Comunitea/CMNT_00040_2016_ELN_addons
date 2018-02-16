import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { PROXY } from '../../providers/constants/constants';
import { AuxProvider } from '../../providers/aux/aux'
/**
 * Generated class for the TreepickPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
import { HomePage } from '../../pages/home/home';
import { TreeopsPage } from '../../pages/treeops/treeops';
import { Storage } from '@ionic/storage';

 declare var OdooApi: any

@IonicPage()
@Component({
  selector: 'page-treepick',
  templateUrl: 'treepick.html',
})
export class TreepickPage {

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

  constructor(public navCtrl: NavController, public navParams: NavParams, public alertCtrl: AlertController, private storage: Storage, public Configs: AuxProvider) {
    
    this.states_show = Configs.get_pick_states_visible();
    this.uid = 0
    this.picks = [];
    this.picking_types = [];
    this.picking_type_id = 0
    this.domain_types = []
    this.user = this.navParams.data.user || 'assigned'
    this.domain_state = ['state', 'in', this.states_show]
    this.fields = ['id', 'name', 'state', 'state_2', 'done_ops', 'partner_id_name', 'location_id_name', 'location_dest_id_name', 'ops_str', 'picking_type_id_name', 'user_id'];
    this.get_picking_types();
    //this.filter_picks(0) ;
    
    
        }
  ionViewWillEnter(){
    this.filter_picks(0) ;
  }
 

  get_picks(){
    var self = this
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
          self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          var con = val;
          var domain = [];
          var odoo = new OdooApi(PROXY, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              self.uid = uid;
              if (self.domain_state!=[]) { domain.push(self.domain_state);}
              if (self.domain_types!=[]) { domain.push(self.domain_types);}
              if (self.user=='assigned') { domain.push(['user_id', '=', uid]);} else {domain.push(['user_id','=', false]);}
              console.log(domain)
              odoo.search_read('stock.picking', domain, self.fields, 0, 0).then(
                function (value) {
                  self.picks=[];
                  for (var key in value) {
                    self.picks.push(value[key]);
                  }

                  for (var i in self.picks){
                    var pick = self.picks[i];
                    pick['allow_validate'] = (pick['state'] == 'assigned' && pick['ops_done'] >= 1);
                    }

                  self.cargar = false;
                  self.storage.set('stock.picking', value);
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
                  self.cargar = false;
              }
          });
      

  }        
  get_picking_types(){
    var self = this
    this.storage.get('CONEXION').then((val) => {
      if (val == null) {
          self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
      } else {
          var con = val;
          var odoo = new OdooApi(PROXY, con.db);
          odoo.login(con.username, con.password).then(
            function (uid) {
              odoo.search_read('stock.picking.type', [['show_in_pda', '=', true]], ['id', 'name', 'short_name'], 0, 0).then(
                function (value) {
                  self.picking_types = []
                  for (var key in value) {
                    self.picking_types.push(value[key]);
                  }
                  self.storage.set('stock.picking.type', value);
                },
                function () {
                  self.cargar = false;
                  self.presentAlert('Falla!', 'Imposible conectarse');
                }
                          );
                      },
                      function () {
                          self.cargar = false;
                          self.presentAlert('Falla!', 'Imposible conectarse');
                      }
                  );
                  self.cargar = false;
              }
          });
      

  }  
filter_picks(picking_type_id){

  var self = this
  self.picking_type_id = picking_type_id
  if (picking_type_id==0)
    {self.domain_types =  ['picking_type_id', '!=', false];}
  else 
    {self.domain_types = ['picking_type_id', '=', picking_type_id];}
  self.get_picks();
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
showtreeop_ids(pick_id) {
  
  this.navCtrl.push(TreeopsPage, {picking_id: pick_id});
}

doAsign(pick_id){
  this.change_pick_value(pick_id, 'user_id', this.uid);
  this.user='assigned';
  this.filter_picks(this.picking_type_id);
}
doDeAsign(pick_id){
  
  this.change_pick_value(pick_id, 'user_id', false);
  this.user='no_assigned';
  this.filter_picks(this.picking_type_id);
}
change_pick_value(id, field, new_value){
  var self = this;
  var model = 'stock.picking'
  var method = 'change_pick_value'
  var values = {'id': id, 'field': field, 'value': new_value}
  var object_id


  self.storage.get('CONEXION').then((val) => {

    if (val == null) {
      console.log('No hay conexión');
      self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
    } else {
        console.log('Hay conexión');
        var con = val;
        var odoo = new OdooApi(PROXY, con.db);
        odoo.login(con.username, con.password).then(
          function (uid) {
            odoo.call(model, method, values).then(
              function (value) {
                if (new_value){
                  self.user=''
                }else {self.user='no_assigned'}

              },
              function () {
                self.cargar = false;
                self.presentAlert('Falla!', 'Imposible conectarse');
              }
                        );
                    },
                    function () {
                        self.cargar = false;
                        self.presentAlert('Falla!', 'Imposible conectarse');
                    }
                );
                self.cargar = false;

           
            }
            
            
        });
}
   
doTransfer(id){
  var self = this;
  var model = 'stock.picking'
  var method = 'doTransfer'
  var values = {'id': id}
  var self = this;
  var object_id = {}

  
  this.storage.get('CONEXION').then((val) => {
    if (val == null) {
      console.log('No hay conexión');
      self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
    } else {
        console.log('Hay conexión');
        var con = val;
        var odoo = new OdooApi(PROXY, con.db);
        odoo.login(con.username, con.password).then(
          function (uid) {
            odoo.call(model, method, values).then(
              function (value) {
                object_id = value;
                self.cargar = false;
                this.navCtrl.push(TreepickPage);
              },
              function () {
                self.cargar = false;
                self.presentAlert('Falla!', 'Imposible conectarse');
              }
                        );
                    },
                    function () {
                        self.cargar = false;
                        self.presentAlert('Falla!', 'Imposible conectarse');
                    }
                );
                self.cargar = false;

           
            }
            
            
            
            
        });
  
    }
}
