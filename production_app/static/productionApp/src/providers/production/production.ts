import { Injectable } from '@angular/core';
import { OdooProvider } from '../odoo/odoo';

/*
  Generated class for the ProductionProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
@Injectable()
export class ProductionProvider {
    workcenter;
    registry_id;
    production;
    product;
    product_id;
    state;
    states;

    start_checks: Object[];
    freq_checks: Object[];

    last_stop_id;
    cdb;
    weight;

    constructor(private odooCon: OdooProvider) {
        this.states = {
            'waiting': 'ESPERANDO PRODUCCIÓN',
            'confirmed': 'PRODUCCIÓN CONFIRMADA',
            'setup': 'PREPARACIÓN PRODUCCION',
            'started': 'PRODUCCIÓN INICIADA',
            'stoped': 'PRODUCCIÓN PARADA',
            'cleaning': 'PRODUCCIÓN EN LIMPIEZA',
            'finished': 'PRODUCCIÓN FINALIZADA'
        };
    }

    // Gets all the data needed fom the app.regystry model
    loadProduction(workcenter){
        var promise = new Promise( (resolve, reject) => {
            var values = {'workcenter_id': workcenter.id}
            var method = 'app_get_registry'
            this.odooCon.callRegistry(method, values).then( (reg: Object) => {

                if ('id' in reg){
                    this.initData(reg);
                    resolve(reg);
                }
                else {
                    var err = {'title': 'Aviso', 'msg': 'No hay ordenes de trabajo planificadas.'}
                    reject(err)
                }
            })
            .catch( (err) => {
                reject(err);
            });
        });
        return promise
    }

    initData(data) {
        this.workcenter = data.workcenter_id[1];
        this.registry_id = data.id;
        this.production = data.production_id[1];
        this.product_id = data.product_id[0];
        this.product = data.product_id[1];
        this.state = data.state;
        this.last_stop_id = false;
    }

    manageOdooFail(){
        console.log("Guardo para escribir luego")
    }

    setStepAsync(method) {
        var values =  {'registry_id': this.registry_id};
        this.odooCon.callRegistry(method, values).then( (res) => {
            this.state = res['state'];
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    confirmProduction() {
        this.state = 'confirmed'
        this.setStepAsync('confirm_production');
    }

    setupProduction() {
        this.state = 'setup'
        this.setStepAsync('setup_production');
    }
    startProduction() {
        this.state = 'start'
        this.setStepAsync('start_production');
    }
    stopProduction() {
        this.state = 'stoped'
        this.setStepAsync('stop_production');

    }
    restartProduction() {
        this.state = 'started'
        this.setStepAsync('restart_production');
    }
    cleanProduction() {
        this.state = 'cleaning'
        this.setStepAsync('clean_production');
    }
    finishProduction() {
        this.state = 'finished'
        this.setStepAsync('finish_production');
    }





}
