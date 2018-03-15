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
                    this.getQualityChecks();  // Load Quality Checks. TODO PUT PROMISE SYNTAX
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
        this.start_checks = [];
        this.freq_checks = [];
    }
    
    // Load Quality checks in each type list
    loadQualityChecks(q_checks) {
        for (let indx in q_checks) {
            var qc = q_checks[indx];
            if (qc.quality_type == 'start'){
                this.start_checks.push(qc);
            }
            else{
                this.freq_checks.push(qc);
            }
        }
        console.log("START CHECKS");
        console.log(this.start_checks);
        console.log("FREQ CHECKS");
        console.log(this.freq_checks);
    }

    // Ask odoo for quality checks
    getQualityChecks() {
        var values =  {'product_id': this.product_id};
        var method = 'get_quality_checks'
        this.odooCon.callRegistry(method, values).then( (res) => {
            this.loadQualityChecks(res)
        })
        .catch( (err) => {
            // Si hay error aquí, convertir esta funcion en promesa y controlarla.
            console.log(err) 
        });
    }

    saveQualityChecks(data){
        console.log("RESULTADO A GUARDAR")
        console.log(data)
        var values = {
            'registry_id': this.registry_id,
            'lines': data
        }
        this.odooCon.callRegistry('app_save_quality_checks', values).then( (res) => {
            console.log("RESULTADO GUARDADO") 
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    manageOdooFail(){
        console.log("Guardo para escribir luego")
    }

    setStepAsync(method) {
        var values =  {'registry_id': this.registry_id};
        this.odooCon.callRegistry(method, values).then( (res) => {
            // this.state = res['state'];
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
        this.state = 'started'
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
