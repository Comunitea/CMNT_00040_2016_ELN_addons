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

    stop_from_state;
    operatorsById: Object = {};
    context;
    uid;

    constructor(public storage: Storage) {
      this.context = {'lang': 'es_ES'}
      this.uid = 0
    }

    pendingCalls() {
        var promise = new Promise( (resolve, reject) => {
            if (this.pending_calls.length == 0) {
                resolve(); 
            } else {
                let pending = this.pending_calls[0]
                var method = pending['method']
                var values = pending['values']
                this.storage.get('CONEXION').then((con_data) => {
                    var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                    if (con_data == null) {
                        var err = {'title': '¡Error!', 'msg': 'No hay datos para establecer la conexión'}
                        reject(err);
                    } else {
                        var model = 'production.app.registry'
                        odoo.call(model, method, values).then((res) => {
                            if (method == 'stop_production') {
                                this.stop_from_state = res['stop_from_state'];
                            }
                            if (method == 'log_in_operator') {
                                this.operatorsById[values['operator_id']]['operator_line_id'] = res['operator_line_id'];
                            }
                            if (method == 'log_out_operator') {
                                this.operatorsById[values['operator_id']]['operator_line_id'] = false;
                            }
                            this.pending_calls.splice(0, 1);
                            this.pendingCalls().then(() => {
                                resolve();
                            })
                            .catch( () => {
                                reject();
                            }); 
                        })
                        .catch( () => {
                            console.log("Error al ejecutar las llamadas pendientes")
                            reject();
                        });
                    }
                })
                .catch( () => {
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
                var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                if (con_data == null) {
                    var err = {'title': '¡Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    this.pendingCalls().then(() => {
                        console.log("Hice lo que estaba pendiente");
                        var model = 'production.app.registry'
                        odoo.call(model, method, values).then((res) => {
                            resolve(res);
                        })
                        .catch( () => {
                            this.pending_calls.push({'method': method, 'values': values})
                            var err = {'title': '¡Error!', 'msg': 'Fallo al llamar al método ' + method + ' del modelo production.app.registry'}
                            reject(err);
                        });
                    })
                    .catch( () => {
                        this.pending_calls.push({'method': method, 'values': values})
                        var err = {'title': '¡Error!', 'msg': 'Fallo al llamar al método ' + method + ' del modelo production.app.registry'}
                        reject(err);
                    });
                }
            });
        });
        return promise
    }

    searchRead(model, domain, fields, offset = 0, limit = 0, order = '') {
        var model = model;
        var domain = domain;
        var fields = fields;
        var promise = new Promise( (resolve, reject) => {
            this.storage.get('CONEXION').then((con_data) => {
                if (con_data == null) {
                    var err = {'title': '¡Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                    odoo.context = this.context
                    odoo.search_read(model, domain, fields, offset, limit, order).then((res) => {
                        resolve(res);
                    })
                    .catch( () => {
                        var err = {'title': '¡Error!', 'msg': 'Fallo al llamar al hacer search_read'}
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
                var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                odoo.context = self.context
                if (con_data == null) {
                    var err = {'title': '¡Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    odoo.call(model, method, values).then((res) => {
                        resolve(res);
                    })
                    .catch( () => {
                        var err = {'title': '¡Error!', 'msg': 'Fallo al llamar al método ' + method + 'del modelo production.app.registry'}
                        reject(err);
                    });
                }
            });
        });
        return promise
    }

}
