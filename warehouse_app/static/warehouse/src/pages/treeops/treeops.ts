import { Component, ViewChild} from '@angular/core';
import { IonicPage, NavController, NavParams, AlertController } from 'ionic-angular';
import { PROXY } from '../../providers/constants/constants';
import {FormBuilder, FormGroup } from '@angular/forms';

import { HostListener } from '@angular/core';


/**
 * Generated class for the TreepickPage page.
 *
 * See https://ionicframework.com/docs/components/#navigation for more info on
 * Ionic pages and navigation.
 */
import { HomePage } from '../home/home';
import { SlideopPage } from '../slideop/slideop';
import { Storage } from '@ionic/storage';
import { TreepickPage } from '../treepick/treepick'

 declare var OdooApi: any

@IonicPage()
@Component({
  selector: 'page-treeops',
  templateUrl: 'treeops.html',
})
export class TreeopsPage {

  @ViewChild('scanPackage') myScanPackage;

  @HostListener('document:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent) { 
    this.myScanPackage.setFocus();
     }
  
  op_fields = ['id', 'pda_checked', 'pda_done', 'product_id', 'product_uom','product_qty', 'qty_done', 'package_id', 'lot_id', 'location_id']
  pick_fields = ['id', 'name', 'location_id_name', 'location_dest_id_name', 'min_date', 'picking_type_id_name', 'state', 'partner_id_name', 'done_ops', 'all_ops']
  items = [];
  picks = [];
  pick = {};
  cargar = true;
  pick_id = 0
  limit = 5
  offset = 0
  model = 'stock.pack.operation'
  domain = []
  pick_domain = []
  record_count = 0
  isPaquete: boolean = true;
  isProducto: boolean = false;
  pick_name = '';
  pick_type = '';
  selected_picking = {};
  scan = ''
  treeForm: FormGroup;
  ops = []
  model_fields = {'stock.quant.package': 'package_id', 'stock.location': 'location_id', 'stock.production.lot': 'lot_id'}
  whatOps: string
  
  constructor(public navCtrl: NavController, public navParams: NavParams,  private formBuilder: FormBuilder,public alertCtrl: AlertController, private storage: Storage) {
    
    this.items = [];
    this.picks = [];
    this.pick = {};
    this.pick_id = this.navParams.data.picking_id;
    this.domain = [['picking_id', '=', this.pick_id]];
    this.pick_domain = [['id', '=', this.pick_id]];
    this.record_count = 0;    
    this.pick_name = 'Nombre albarán'
    this.pick_type = 'pick_type'
    this.selected_picking = {}
    this.scan = '';
    this.whatOps = 'Todas'
    this.treeForm = this.formBuilder.group({
      scan: ['']
    });
    

  }

  ionViewWillEnter(){
    this.loadList();
  }
  seeAll(){
    if (this.whatOps=='Todas'){
      this.whatOps='Pendientes'
    }
    else
      {this.whatOps='Todas'}
  }

  ionViewLoaded() {
    
    setTimeout(() => {
      this.myScanPackage.setFocus();
    },150);
    
     }
  loadList(){
    var self = this;
    self.items = []
    this.storage.get('CONEXION').then((val) => {
        if (val == null) {
          console.log('No hay');
          self.navCtrl.setRoot(HomePage, {borrar: true, login: null});
        } else {
            console.log('hay');
            var con = val;
            var odoo = new OdooApi(PROXY, con.db);
            
            odoo.login(con.username, con.password).then(
              function (uid) {
                odoo.search_read(self.model, self.domain, self.op_fields, self.offset, self.limit).then(
                  function (value) {
                    self.items = [];
                    var newOP = {};
                    self.ops=[];
                    for (var key in value) {
                      self.items.push(value[key]);                      
                      }
                    for (var key in self.items) {
                      newOP = {'index': key, 
                               'id': self.items[key]['id'],
                               'pda_done': self.items[key['pda_done']]}
                      self.ops.push(newOP)
                    }
                    self.record_count = self.items.length;
                    self.cargar = false;
                    self.storage.set(self.model, value);                    
                    },
                    function () {self.navParams.data.op_id;
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

            odoo.login(con.username, con.password).then(
              function (uid) {
                odoo.search_read('stock.picking', self.pick_domain, self.pick_fields).then(
                  function (value) {
                    for (var key in value) {
                      self.picks.push(value[key]);                      
                      }
                    console.log("Pick " + self.picks['name']);
                    self.pick = self.picks[0];
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
                };
            self.selected_picking = {'pick': self.pick, 'ops': self.items}
    })
           
  }
 
   

  presentAlert(titulo, texto) {
    const alert = this.alertCtrl.create({
        title: titulo,
        subTitle: texto,
        buttons: ['Ok']
    });
    alert.present();
  }
  loadNext(){
    this.offset = Math.max(this.offset + this.limit, this.record_count - this.limit);
    this.loadList();
  }
  loadPrev(){
    this.offset = Math.min(0, this.offset - this.limit);
    this.loadList();
  }
  
  notify_do_op(op_id){
    console.log("Do op")
  }

  openOp(op_id, index){
    this.navCtrl.push(SlideopPage, {op_id: op_id, index: index, ops: this.ops});
  }

  submitScan (){
    this.getObjectId({'model': ['stock.location', 'stock.quant.package', 'stock.production.lot'], 'search_str' : this.treeForm.value['scan']})
    this.treeForm.reset();
  }

  findId (value){
    
    for (var op in this.items){
      
      var opObj = this.items[op];
      console.log(opObj);
      if (opObj[this.model_fields[value['model']]][0] == value['id']){
        return {'op_id': opObj['id'], 'index': op, 'ops': this.items, 'origin': true}

      }
    }
    return false

  }


  getObjectId(values){
    var self = this;
    var object_id = {}

    var model = 'warehouse.app'
    var method = 'get_object_id'
    
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

                  
                  setTimeout(() => {
                    var res = self.findId(value);
                    if (res) {
                      self.navCtrl.push(SlideopPage, res);}
                  },150);
                  
                  
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
            
              }
              
              
          });
    
      
        }

      
  doTransfer(id){
    var self = this;
    var model = 'stock.picking'
    var method = 'doTransfer'
    var values = {'id': id}
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
                  self.loadList()
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
              this.navCtrl.push(TreepickPage);
              
          });
    
      }

  
  doOp(id, do_id){
    var self = this;
    var model = 'stock.pack.operation'
    var method = 'doOp'
    var values = {'id': id, 'do_id': do_id}
    var object_id


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
                  /*self.ionViewLoaded()*/
                  self.loadList();
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
