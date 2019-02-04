import { Injectable } from '@angular/core';
import { OdooProvider } from '../odoo/odoo';
import * as $ from 'jquery';

/*
  Generated class for the ProductionProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/
@Injectable()
export class ProductionProvider {
    operators: any;
    lots: any;
    
    lotsByProduct: Object = {};
    workcenter: Object = {};
    loged_ids: number[] = [];
    product_ids: number[] = [];
    consume_ids: number[] = [];
    registry_id;
    production;
    production_id;
    product;
    product_id;
    consume_product_id;
    state;
    states;

    start_checks: Object[];
    freq_checks: Object[];

    technical_reasons: Object[];
    organizative_reasons: Object[];
    scrap_reasons: Object[];

    consumptions: Object[];
    allowed_consumptions: Object[];

    operator_line_id;
    active_operator_id: number = 0;

    qty: number;
    scrap_qty: number;
    scrap_reason_id: number;
    production_qty: number;
    production_uos_qty: number;
    uom: string;
    uos: string;
    uos_coeff: number;
    lot_name;
    lot_date;
    product_use_date: string;
    change_lot_qc_id: number;

    constructor(private odooCon: OdooProvider) {
        this.states = {
            'waiting': 'ESPERANDO PRODUCCIÓN',
            'confirmed': 'PRODUCCIÓN CONFIRMADA',
            'setup': 'PREPARACIÓN PRODUCCIÓN',
            'started': 'PRODUCCIÓN INICIADA',
            'stoped': 'PRODUCCIÓN PARADA',
            'cleaning': 'PRODUCCIÓN EN LIMPIEZA',
            'finished': 'PRODUCCIÓN FINALIZADA'
        };
        this.operator_line_id = false;
        this.technical_reasons = [];
        this.organizative_reasons = [];
        this.consumptions = [];
    }

    getUTCDateStr(){
        var date = new Date();
        var year = date.getFullYear();
        var month = date.getMonth() + 1;
        var day = date.getDate();
        var hours = date.getUTCHours();
        var minutes = date.getMinutes();
        var seconds = date.getSeconds();

        var year_str = year.toString();
        var month_str = month.toString();
        var day_str = day.toString();
        var hours_str = hours.toString();
        var minutes_str = minutes.toString();
        var seconds_str = seconds.toString();
        if (month < 10) month_str = "0" + month_str;
        if (day < 10) day_str = "0" + day_str;
        if (hours < 10) hours_str = "0" + hours_str;
        if (minutes < 10) minutes_str = "0" + minutes_str;
        if (seconds < 10) seconds_str = "0" + seconds_str;

        var today = year_str + "-" + month_str + "-" + day_str + " " + hours_str + ":" + minutes_str + ":" + seconds_str;
        return today;
    }

    //Gets operators allowed, now all employees
    getAllowedOperators(reg){
        var allowed_operators = reg['allowed_operators'];
        this.operators = allowed_operators;
        for (let indx in allowed_operators) {
            let op = allowed_operators[indx];
            let log = 'out';
            let active = false;
            if (op.id in this.odooCon.operatorsById){
                log = this.odooCon.operatorsById[op.id].log
                active = this.odooCon.operatorsById[op.id].active
            }
            this.odooCon.operatorsById[op.id] = {'name': op.name, 'let_active': op.let_active, 'active': active, 'operator_line_id': false, 'log': log}    
        }
        console.log("OPERATORSALLOWEDBYID")
        //console.log(this.odooCon.operatorsById)
    }

    getLogInOperators(){
        var items2 = this.operators.filter(obj => this.odooCon.operatorsById[obj.id]['log'] == 'in');
        return items2;
    }

    getOperatorNames(){
        let str_names = ''
        var log_in_list = this.getLogInOperators()
        for (let indx in log_in_list) {
            let op = log_in_list[indx];
            str_names += op.name + ', ' 
        }
        return str_names

    }
    getActiveOperatorName(){
        let str_names = ''
        var log_in_list = this.getLogInOperators()
        for (let indx in log_in_list) {
            let op = log_in_list[indx];
            if (op.id === this.active_operator_id){
                str_names = op.name;
            }
        }
        return str_names

    }

    getLots(){
        var model = 'production.app'
        var method = 'get_available_lot'
        var values = {'product_ids': this.consume_ids, 'with_stock': true}
        this.lotsByProduct = {}
        this.odooCon.execute(model, method, values).then((lot_ids) => {
            for (let indx in lot_ids) {
                let lot = lot_ids[indx];
                let product_id = lot.product_id;
                if (!(product_id in this.lotsByProduct)){
                    this.lotsByProduct[product_id] = []
                }
                this.lotsByProduct[product_id].push(lot)
            }
            console.log("LOTSBYID1")
            console.log(this.lotsByProduct)
        })
        .catch( (err) => {
            console.log("Error buscando lotes")
        });

        model = 'stock.production.lot'
        var domain = [['product_id', 'in', this.product_ids]]
        var fields = ['id', 'name', 'use_date', 'product_id', 'qty_available']
        this.odooCon.searchRead(model, domain, fields, 0, 5, 'create_date DESC, use_date').then((lot_ids) => {
            for (let indx in lot_ids) {
                let lot = lot_ids[indx];
                let product_id = lot.product_id[0];
                if (!(product_id in this.lotsByProduct)){
                    this.lotsByProduct[product_id] = []
                }
		lot.product_id = product_id
                this.lotsByProduct[product_id].push(lot)
            }
            console.log("LOTSBYID2")
            //console.log(this.lotsByProduct, this)
        })
        .catch( (err) => {
            console.log("Error buscando lotes")
        });
    }

    logInOperator(operator_id){
        // if (this.loged_ids.length === 0){
        //     this.setActiveOperator(operator_id)
        // }
        this.odooCon.operatorsById[operator_id]['log'] = 'in'
        var index = this.loged_ids.indexOf(operator_id);
        if (index <= -1) {
            this.loged_ids.push(operator_id)
        }
        var values =  {'registry_id': this.registry_id, 'operator_id': operator_id, 'date_in': this.getUTCDateStr()};
        this.odooCon.callRegistry('log_in_operator', values).then( (res) => {
            this.odooCon.operatorsById[operator_id]['operator_line_id'] = res['operator_line_id'];
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    setActiveOperator(operator_id){
        this.active_operator_id = operator_id;
    }

    logOutOperator(operator_id){
        this.odooCon.operatorsById[operator_id]['log'] = 'out'
        var index = this.loged_ids.indexOf(operator_id);
        if (index > -1) {
            this.loged_ids.splice(index, 1);
        }
        if (this.active_operator_id = operator_id){
            this.active_operator_id = 0;
        }
        let operator_line_id = this.odooCon.operatorsById[operator_id]['operator_line_id']
        var values =  {'registry_id': this.registry_id, 'operator_line_id': operator_line_id, 'date_out': this.getUTCDateStr()};
        this.odooCon.callRegistry('log_out_operator', values).then( (res) => {
            this.odooCon.operatorsById[operator_id]['operator_line_id'] = false;
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    setLogedTimes(){
        for (let indx in this.loged_ids) {
            let operator_id =  this.loged_ids[indx]
            this.logInOperator(operator_id)
        }
    }

    loadReasons(reasons, workcenter_id) {
        this.technical_reasons = []
        this.organizative_reasons = []
        for (let indx in reasons) {
            var r = reasons[indx];
            if ( (r.reason_type == 'technical') && (r.workcenter_ids.indexOf(workcenter_id) >= 0) ){
                this.technical_reasons.push(r);
            }
            else if (r.reason_type == 'organizative'){
                this.organizative_reasons.push(r);
            }
        }
        console.log("ORGANIZATIVE REASONS");
        console.log(this.organizative_reasons);
        console.log("TECHNICAL REASONS");
        console.log(this.technical_reasons);
    }
    getStopReasons(workcenter_id){
        var promise = new Promise( (resolve, reject) => {
            this.odooCon.searchRead('stop.reason', [], ['id', 'name', 'reason_type', 'workcenter_ids']).then( (res) => {
                this.loadReasons(res, workcenter_id)
                resolve();
            })
            .catch( (err) => {
                console.log(" GET REASONS ERROR deberia ser una promesa, y devolver error, controlarlo en la página y lanzar excepción")
                reject();
            });
        });
        return promise
    }

    getScrapReasons(){
        var promise = new Promise( (resolve, reject) => {
            this.odooCon.searchRead('scrap.reason', [], ['id', 'name']).then( (res) => {
                this.scrap_reasons = [];
                for (let indx in res) {
                    var r = res[indx];
                    this.scrap_reasons.push(r)
                }
                resolve();
            })
            .catch( (err) => {
                console.log(" GET REASONS ERROR deberia ser una promesa, y devolver error, controlarlo en la página y lanzar excepción")
                reject();
            });
        });
        return promise
    }

    // Gets all the data needed fom the app.regystry model
    loadProduction(workcenter){
        this.workcenter = workcenter
        var promise = new Promise( (resolve, reject) => {
            var values = {'workcenter_id': workcenter.id}
            var method = 'app_get_registry'
            this.odooCon.callRegistry(method, values).then( (reg: Object) => {

                if ('id' in reg){
                    this.initData(reg);
                    this.getQualityChecks();  // Load Quality Checks. TODO PUT PROMISE SYNTAX
                    this.getConsumptions();  // Load Consumptions. TODO PUT PROMISE SYNTAX
                    this.setLogedTimes();  // Load Quality Checks. TODO PUT PROMISE SYNTAX
                    this.getLots();  // Load Quality Checks. TODO PUT PROMISE SYNTAX
                    this.getAllowedOperators(reg)
                    this.getScrapReasons();
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
        this.workcenter['id'] = data.workcenter_id[0];
        this.workcenter['name'] = data.workcenter_id[1];
        this.registry_id = data.id;
        this.production_id = data.production_id[0];
        this.production = data.production_id[1];
        this.product_id = data.product_id[0];
        this.product = data.product_id[1];
        this.state = data.state;
        this.start_checks = [];
        this.freq_checks = [];
        this.product_use_date = data.product_use_date
        this.scrap_qty = 0;
        this.production_qty = data.production_qty;
        this.production_uos_qty = data.production_uos_qty;
        this.uom = data.uom;
        this.uos = data.uos;
        this.uos_coeff = data.uos_coeff;
        this.change_lot_qc_id = data.change_lot_qc_id;
        this.product_ids = data.product_ids;
        this.consume_ids = data.consume_ids
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

    loadConsumptions(moves) {
        this.consumptions = [];
        this.allowed_consumptions = [];
        for (let indx in moves) {
            var move = moves[indx];
            var lot = '';
            var state='Para consumir'
            if (move['state'] == 'done' || move['state'] == 'cancel'){
                state = 'Consumido'
            }
            if (move['restrict_lot_id']){
                lot = move['restrict_lot_id'][1]
            }
            var vals = {
                'product': move['product_id'][1],
                'product_id': move['product_id'][0],
                'qty':  move['product_uom_qty'],
                'uom': move['product_uom'][1],
                'lot': lot,
                'state': state
            }
            this.consumptions.push(vals);
            if (move['show_in_app'] == true){
                this.allowed_consumptions.push(vals);
            }
        }
        console.log("MOVES");
        console.log(moves);
        console.log("LOADED CONSUMPTIONS");
        console.log(this.consumptions);   
    }

    getConsumptions(){
        var promise = new Promise( (resolve, reject) => {
            var domain = [['raw_material_production_id', '=', this.production_id]]
            var fields = ['id', 'show_in_app', 'product_id', 'product_uom_qty', 'product_uom', 'restrict_lot_id', 'state']
            this.odooCon.searchRead('stock.move', domain, fields).then( (res) => {
                this.loadConsumptions(res)
                resolve();
            })
            .catch( (err) => {
                console.log("Error obteniendo consumos");
            });
        });
        return promise
    }

    saveQualityChecks(data){
        console.log("RESULTADO A GUARDAR")
        console.log(data)

        // We want to pass by value the object
        var new_lines = []
        for (var index in data){
            var new_ = {}
            var obj = data[index]
            $.extend(new_, obj)
            new_lines.push(new_) 

        }
        var values = {
            'registry_id': this.registry_id,
            'lines': new_lines,
            'active_operator_id': this.active_operator_id,
            'qc_date': this.getUTCDateStr()
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

    setStepAsync(method, values) {
        values['registry_id'] = this.registry_id;     
        this.odooCon.callRegistry(method, values).then( (res) => {
            if (method == 'stop_production'){
                this.odooCon.last_stop_id = res['stop_id'];
            }
	    if (res['state']) {
                this.state = res['state'];
            }
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    confirmProduction() {
        this.state = 'confirmed'
        this.setStepAsync('confirm_production', {});
    }
    setupProduction() {
        this.state = 'setup'
        var values = {'setup_start': this.getUTCDateStr()}
        this.setStepAsync('setup_production', values);
    }
    startProduction() {
        this.state = 'started'
        var values = {'setup_end': this.getUTCDateStr(),
                      'lot_name': this.lot_name,
                      'lot_date': this.lot_date}
        this.setStepAsync('start_production', values);
    }
    stopProduction(reason_id, create_mo) {
        this.state = 'stoped'
        var values = {'reason_id': reason_id,
                      'create_mo': create_mo,
                      'active_operator_id': this.active_operator_id,
                      'stop_start': this.getUTCDateStr()}
        this.setStepAsync('stop_production', values);

    }
    restartProduction() {
        this.state = 'started'
        var values = {'stop_id': this.odooCon.last_stop_id,
                      'stop_end': this.getUTCDateStr()}
        this.setStepAsync('restart_production', values);
    }
    cleanProduction() {
        this.state = 'cleaning'
        var values = {'cleaning_start': this.getUTCDateStr()}
        this.setStepAsync('clean_production', values);
    }
    finishProduction() {
        this.state = 'finished'
        var values = {'qty': this.qty,
                      'cleaning_end': this.getUTCDateStr()}
        this.setStepAsync('finish_production', values);
    }
    restartAndCleanProduction() {
        this.state = 'cleaning';
        var values = {'stop_id': this.odooCon.last_stop_id, 'stop_end': this.getUTCDateStr()};
        this.setStepAsync('restart_and_clean_production', values);
    }
    scrapProduction() {
        var values = {'scrap_qty': this.scrap_qty, 'scrap_reason_id': this.scrap_reason_id};
        this.setStepAsync('scrap_production', values);
    }

}
