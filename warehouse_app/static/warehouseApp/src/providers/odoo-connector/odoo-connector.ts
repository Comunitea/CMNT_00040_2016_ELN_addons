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

    context
    uid
    constructor(private storage: Storage) {
        this.context = { 'lang': 'es_ES', 'from_pda': true }
        this.uid = 0
    }

    login(user, password) {
        var method = method
        var values = values
        var self = this
        var promise = new Promise((resolve, reject) => {
            self.storage.get('CONEXION_WH').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' }
                    reject(err);
                } else {
                    odoo.login(con_data.username, con_data.password).then((uid) => {
                        self.uid = uid
                        resolve(uid)
                    })
                        .catch((mierror) => {
                            var err = { 'title': 'Error!', 'msg': 'No se pudo conectar con Odoo' }
                            reject(err);
                        });
                }
            });
        });
        return promise
    }

    write(model, id, data) {
        var self = this
        var promise = new Promise((resolve, reject) => {
            self.storage.get('CONEXION_WH').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                odoo.context = self.context
                if (con_data == null) {
                    var err = { 'title': 'Error!', 'msg': 'No hay datos para establecer la conexión' }
                    reject(err);
                } else {
                    odoo.write(model, id, data).then((res) => {
                        resolve(res);
                    })
                        .catch(() => {
                            var err = { 'title': 'Error!', 'msg': 'Fallo al llamar al hacer un write' }
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
        var promise = new Promise((resolve, reject) => {
            this.storage.get('CONEXION_WH').then((con_data) => {
                if (con_data == null) {
                    var err = { 'title': '¡Error!', 'msg': 'No hay datos para establecer la conexión' }
                    reject(err);
                } else {
                    var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                    odoo.context = this.context
                    odoo.search_read(model, domain, fields, offset, limit, order).then((res) => {
                        resolve(res);
                    })
                        .catch(() => {
                            var err = { 'title': '¡Error!', 'msg': 'Fallo al llamar a search_read. Posiblemente no haya conexión con el servidor.' }
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
        var promise = new Promise((resolve, reject) => {
            self.storage.get('CONEXION_WH').then((con_data) => {
                var odoo = new OdooApi(con_data.url, con_data.db, con_data.uid, con_data.password);
                odoo.context = self.context
                if (con_data == null) {
                    var err = { 'title': '¡Error!', 'msg': 'No hay datos para establecer la conexión' }
                    reject(err);
                } else {
                    odoo.call(model, method, values).then((res) => {
                        resolve(res);
                    })
                        .catch(() => {
                            var err = { 'title': '¡Error!', 'msg': 'Fallo al llamar al método ' + method + 'del modelo warehouse_app. Posiblemente no haya conexión con el servidor.' }
                            reject(err);
                        });
                }
            });
        });
        return promise
    }

}