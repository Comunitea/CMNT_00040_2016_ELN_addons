import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage';

/*
  Generated class for the OdooProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
declare var OdooApi: any;

@Injectable()
export class OdooProvider {

    pending_calls : Object[] = []

    last_stop_id;
    operatorsById: Object = {};
    context;
    uid;

    constructor(public storage: Storage) {
      this.context = {'lang': 'es_ES'}
      this.uid = 0
    }

    login(user, password){
        var method = method
        var values = values
        var self = this
        var promise = new Promise( (resolve, reject) => {
            self.storage.get('CONEXION').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db);
                // this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
                if (con_data == null) {
                    var err = {'title': 'Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    
                    odoo.login(con_data.username, con_data.password).then( (uid) => {
                    self.uid = uid
                    resolve(uid)
                    })
                    .catch( (mierror) => {
                      var err = {'title': 'Error!', 'msg': 'No se pudo conectar con Odoo'}
                      reject(err);
                    });
                }
            });
        });
        return promise
    }

    pendingCalls(){
        var promise = new Promise( (resolve, reject) => {
            console.log(this.pending_calls);
            if (this.pending_calls.length == 0) { 
                resolve(); 
            }
            else{
                let pending = this.pending_calls[0]
                var method = pending['method']
                var values = pending['values']
                this.storage.get('CONEXION').then((con_data) => {
                    var odoo = new OdooApi(con_data.url, con_data.db);
                    if (con_data == null) {
                        var err = {'title': 'Error!', 'msg': 'No hay datos para establecer la conexión'}
                        reject(err);
                    } else {
                        odoo.login(con_data.username, con_data.password).then( (uid) => {
                            var model = 'app.registry'

                            if (method == 'restart_production' || method == 'restart_and_clean_production'){
                                values['stop_id'] = this.last_stop_id;
                            }

                            odoo.call(model, method, values).then( (res) => {

                                if (method == 'stop_production'){
                                    this.last_stop_id = res['stop_id'];
                                }
                                if (method == 'log_in_operator'){
                                    this.operatorsById[values['operator_id']]['operator_line_id'] = res['operator_line_id'];
                                }
                                if (method == 'log_out_operator'){
                                    this.operatorsById[values['operator_id']]['operator_line_id'] = false;
                                }

                                this.pending_calls.splice(0, 1);
                                this.pendingCalls().then( () => {
                                    resolve();
                                })
                                .catch( () => {
                                    reject();
                                }); 
                            })
                            .catch( () => {
                                console.log("Err3")
                            });
                               
                        })
                        .catch( () => {
                            this.pending_calls.push({'method': method, 'values': values})
                            var err = {'title': 'Error!', 'msg': 'No se pudo conectar con Odoo'}
                            reject(err);
                        });
                    }
                })
                .catch( ()  => {
                    console.log("err");
                });
            }
           
        });
        return promise
    }

    callRegistry(method, values) {
        var method = method
        var values = values
        var promise = new Promise( (resolve, reject) => {
            this.storage.get('CONEXION').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db);
                // this.navCtrl.setRoot(HomePage, {borrar: true, login: null});
                if (con_data == null) {
                    var err = {'title': 'Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    odoo.login(con_data.username, con_data.password).then( (uid) => {
                        this.pendingCalls().then( () => {
                            var model = 'app.registry'
                            odoo.call(model, method, values).then((res) => {
                                resolve(res);
                            })
                            .catch( () => {
                                this.pending_calls.push({'method': method, 'values': values})
                                var err = {'title': 'Error!', 'msg': 'Fallo al llamar al método ' + method + ' del modelo app.registry'}
                                reject(err);
                            });
                        })
                        .catch( ()  => {
                             console.log("err");
                        });
                           
                    })
                    .catch( () => {
                        if (method !== 'app_get_registry'){
                            this.pending_calls.push({'method': method, 'values': values})
                        }
                        var err = {'title': 'Error!', 'msg': 'No se pudo conectar con Odoo'}
                        reject(err);
                    });
                }
            });
        });
        return promise
    }

    searchRead(model, domain, fields, offset = 0, limit = 0, order = ''){
        var model = model;
        var domain = domain;
        var fields = fields;
        var promise = new Promise( (resolve, reject) => {
            this.storage.get('CONEXION').then((con_data) => {
                if (con_data == null) {
                    var err = {'title': 'Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    var odoo = new OdooApi(con_data.url, con_data.db);
                    odoo.context = this.context
                    odoo.login(con_data.username, con_data.password).then( (uid) => {
                    odoo.search_read(model, domain, fields, offset, limit, order).then((res) => {
                        resolve(res);
                    })
                    .catch( () => {
                        var err = {'title': 'Error!', 'msg': 'Fallo al llamar al hacer search_read'}
                        reject(err);
                    });
                    })
                    .catch( () => {
                        var err = {'title': 'Error!', 'msg': 'No se pudo conectar con Odoo'}
                        reject(err);
                    });
                }
            });
        });
        return promise
    }

    execute(model, method, values) {
        var method = method
        var values = values
        var self = this
        var promise = new Promise( (resolve, reject) => {
            self.storage.get('CONEXION').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db);
                odoo.context = self.context
                if (con_data == null) {
                    var err = {'title': 'Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                }
		else {
                    odoo.login(con_data.username, con_data.password).then((uid) => {
                            odoo.call(model, method, values).then((res) => {
                                resolve(res);
                            })
                            .catch( () => {
                                var err = {'title': 'Error!', 'msg': 'Fallo al llamar al método ' + method + 'del modelo app.regustry'}
                                reject(err);
                            });
                    })
                    .catch( () => {
                        var err = {'title': 'Error!', 'msg': 'No se pudo conectar con Odoo'}
                        reject(err);
                    });
                }
            });
        });
        return promise
    }

}
