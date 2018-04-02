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

    constructor(private storage: Storage) {
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
                            odoo.call(model, method, values).then((res) => {
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
                                var err = {'title': 'Error!', 'msg': 'Fallo al llamar al método ' + method + 'del modelo app.regustry'}
                                reject(err);
                            });
                        })
                        .catch( ()  => {
                             console.log("err");
                        });
                           
                    })
                    .catch( () => {
                        this.pending_calls.push({'method': method, 'values': values})
                        var err = {'title': 'Error!', 'msg': 'No se pudo conectar con Odoo'}
                        reject(err);
                    });
                }
            });
        });
        return promise
    }

    searchRead(model, domain, fields){
        var model = model;
        var domain = domain;
        var fields = fields;
        var promise = new Promise( (resolve, reject) => {
            this.storage.get('CONEXION').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db);
                if (con_data == null) {
                    var err = {'title': 'Error!', 'msg': 'No hay datos para establecer la conexión'}
                    reject(err);
                } else {
                    odoo.login(con_data.username, con_data.password).then( (uid) => {
                        odoo.search_read(model, domain, fields, 0, 0).then((res) => {
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

}
