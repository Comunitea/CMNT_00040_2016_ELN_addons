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
    workline: Object = {};
    worklines: Object[];
    logged_ids: number[] = [];
    product_ids: number[] = [];
    consume_ids: number[] = [];
    registry_id;
    production;
    production_id;
    product;
    product_id;
    uom_id;
    uos_id;
    location_src_id;
    location_dest_id;
    consume_product_id;
    state;
    states;
    interval_list: any[] = [];

    start_checks: Object[];
    freq_checks: Object[];

    technical_reasons: Object[];
    organizative_reasons: Object[];
    scrap_reasons: Object[];

    consumptions: Object[];
    consumptions_in: Object[];
    consumptions_out: Object[];
    consumptions_scrapped: Object[];
    finished_products: Object[];

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
    product_max_date: string;
    product_lot_name: string;
    workline_name: string;
    review_consumptions: boolean = false;
    consumptions_done: boolean = false;
    bom_app_notes: string;
    note: string;
    consumptions_note: string;
    process_type: string;
    setup_end: boolean = false;

    constructor(private odooCon: OdooProvider) {
        this.states = {
            'waiting': 'ESPERANDO PRODUCCIÓN',
            'confirmed': 'PRODUCCIÓN CONFIRMADA',
            'setup': 'PREPARACIÓN PRODUCCIÓN',
            'started': 'PRODUCCIÓN INICIADA',
            'stopped': 'PRODUCCIÓN PARADA',
            'cleaning': 'PRODUCCIÓN EN LIMPIEZA',
            'finished': 'PRODUCCIÓN FINALIZADA'
        };
        this.operator_line_id = false;
        this.technical_reasons = [];
        this.organizative_reasons = [];
        this.consumptions = [];
        this.consumptions_in = [];
        this.consumptions_out = [];
        this.consumptions_scrapped = [];
        this.finished_products = [];
    }

    getUTCDateStr() {
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
    getAllowedOperators(reg) {
        var allowed_operators = reg['allowed_operators'];
        this.operators = allowed_operators;
        this.logged_ids = []
        this.active_operator_id = 0
        this.odooCon.operatorsById = {}
        for (let indx in allowed_operators) {
            let op = allowed_operators[indx];
            if (op.log == 'in') {
                this.logged_ids.push(op.id)
            }
            if (op.active) {
                this.active_operator_id = op.id
            }
            this.odooCon.operatorsById[op.id] = {
                'name': op.name,
                'let_active': op.let_active,
                'active': op.active,
                'operator_line_id': op.operator_line_id,
                'log': op.log
            }
        }
    }

    getLogInOperators() {
        var items2 = this.operators.filter(obj => this.odooCon.operatorsById[obj.id]['log'] == 'in');
        return items2;
    }

    getOperatorNames() {
        let str_names = ''
        var log_in_list = this.getLogInOperators()
        for (let indx in log_in_list) {
            let op = log_in_list[indx];
            str_names += op.name + ', ' 
        }
        return str_names
    }

    getActiveOperatorName() {
        let str_names = ''
        var log_in_list = this.getLogInOperators()
        for (let indx in log_in_list) {
            let op = log_in_list[indx];
            if (op.id === this.active_operator_id) {
                str_names = op.name;
            }
        }
        return str_names
    }

    getLots() {
        var model = 'production.app.registry'
        var method = 'get_available_lot'
        var values = {'product_ids': this.consume_ids}
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
                if (!(product_id in this.lotsByProduct)) {
                    this.lotsByProduct[product_id] = []
                }
                lot.product_id = product_id
                lot.location_id = false
                this.lotsByProduct[product_id].push(lot)
            }
        })
        .catch( (err) => {
            console.log("Error buscando lotes")
        });
    }

    getMaxUseDate() {
        var promise = new Promise( (resolve, reject) => {
            var model = 'production.app.registry'
            var method = 'get_max_use_date'
            var values = {'registry_id': this.registry_id}
            this.odooCon.execute(model, method, values).then((res) => {
                this.product_max_date = res['max_date'] || '';
                this.product_use_date = res['use_date'] || '';
                this.product_lot_name = res['lot_name'] || '';
                // console.log("product_lot_name:", this.product_lot_name, "product_use_date:", this.product_use_date, "product_max_date:", this.product_max_date);
                resolve();
            })
            .catch( (err) => {
                console.log("Error en get_max_use_date")
            });
        });
        return promise
    }

    logInOperator(operator_id) {
        this.odooCon.operatorsById[operator_id]['log'] = 'in'
        var index = this.logged_ids.indexOf(operator_id);
        if (index <= -1) {
            this.logged_ids.push(operator_id)
        }
        var values = {'registry_id': this.registry_id, 'operator_id': operator_id, 'date_in': this.getUTCDateStr()};
        this.odooCon.callRegistry('log_in_operator', values).then((res) => {
            this.odooCon.operatorsById[operator_id]['operator_line_id'] = res['operator_line_id'];
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    setActiveOperator(operator_id) {
        this.active_operator_id = operator_id;
    }

    logOutOperator(operator_id) {
        this.odooCon.operatorsById[operator_id]['log'] = 'out'
        var index = this.logged_ids.indexOf(operator_id);
        if (index > -1) {
            this.logged_ids.splice(index, 1);
        }
        if (this.active_operator_id === operator_id){
            this.active_operator_id = 0;
        }
        let operator_line_id = this.odooCon.operatorsById[operator_id]['operator_line_id']
        var values =  {'registry_id': this.registry_id, 'operator_line_id': operator_line_id, 'date_out': this.getUTCDateStr()};
        this.odooCon.callRegistry('log_out_operator', values).then((res) => {
            this.odooCon.operatorsById[operator_id]['operator_line_id'] = false;
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    setLoggedTimes() {
        for (let indx in this.logged_ids) {
            let operator_id =  this.logged_ids[indx]
            this.logInOperator(operator_id)
        }
    }

    loadStopReasons(reasons, workcenter_id) {
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
    }

    getStopReasons(workcenter_id) {
        var promise = new Promise( (resolve, reject) => {
            this.odooCon.searchRead('stop.reason', [], ['id', 'name', 'reason_type', 'workcenter_ids']).then((res) => {
                this.loadStopReasons(res, workcenter_id)
                resolve();
            })
            .catch( (err) => {
                console.log("GET STOP REASONS ERROR")
                reject();
            });
        });
        return promise
    }

    loadScrapReasons(reasons, workcenter_id) {
        this.scrap_reasons = []
        for (let indx in reasons) {
            var r = reasons[indx];
            if (r.workcenter_ids.indexOf(workcenter_id) >= 0){
                this.scrap_reasons.push(r);
            }
        }
    }

    getScrapReasons(workcenter_id) {
        var promise = new Promise( (resolve, reject) => {
            this.odooCon.searchRead('scrap.reason', [], ['id', 'name', 'workcenter_ids']).then((res) => {
                this.loadScrapReasons(res, workcenter_id);
                resolve();
            })
            .catch( (err) => {
                console.log("GET SCRAP REASONS ERROR")
                reject();
            });
        });
        return promise
    }

    getWorkcenterLines() {
        var promise = new Promise( (resolve, reject) => {
            var domain = [
                ['workcenter_id', '=', this.workcenter['id']],
                ['production_state', 'in', ['ready','confirmed','in_production','finished','validated']],
                '|',
                ['registry_id', '=', false],
                ['app_state', 'not in', ['finished','validated']],
                ['workorder_planned_state', '=', '1'],
            ];
            var fields = ['id', 'name', 'production_id', 'workcenter_id'];
            var order = 'sequence asc, priority desc, id asc';
            this.odooCon.searchRead('mrp.production.workcenter.line', domain, fields, 0, 0, order).then((res) => {
                this.worklines = [];
                for (let indx in res) {
                    var r = res[indx];
                    this.worklines.push(r)
                }
                resolve();
            })
            .catch( (err) => {
                console.log("getWorkcenterLines ERROR")
                reject();
            });
        });
        return promise
    }

    // Gets all the data needed from the app.regystry model
    loadProduction(vals) {
        var promise = new Promise( (resolve, reject) => {
            var method = 'app_get_registry'
            var values = {'workline_id': vals['workline_id'], 'workcenter_id': vals['workcenter_id'], 'workline_name': vals['workline_name']}
            this.odooCon.callRegistry(method, values).then((reg: Object) => {
                if ('id' in reg) {
                    this.initData(reg);
                    this.getAllowedOperators(reg);
                    this.getConsumptions();
                    this.getLots();           // TODO PUT PROMISE SYNTAX
                    this.getMaxUseDate();
                    this.getScrapReasons(vals['workcenter_id']);
                    this.getQualityChecks().then((res) => {
                        resolve(res);
                    })
                    .catch( (err) => {
                        console.log("Fallo al cargar los controles de calidad.");
			reject();
                    }); 
                } else {
                    var err = {'title': 'Aviso', 'msg': 'No hay órdenes de trabajo planificadas.'}
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
        this.scrap_qty = 0;
        this.production_qty = data.production_qty;
        this.production_uos_qty = data.production_uos_qty;
        this.uom = data.uom;
        this.uos = data.uos;
        this.uom_id = data.uom_id;
        this.uos_id = data.uos_id;
        this.location_src_id = data.location_src_id;
        this.location_dest_id = data.location_dest_id;
        this.uos_coeff = data.uos_coeff;
        this.product_ids = data.product_ids;
        this.consume_ids = data.consume_ids;
        this.workline = data.wc_line_id;
        this.workline_name = data.workline_name;
        this.review_consumptions = data.review_consumptions;
        this.consumptions_done = data.consumptions_done;
        this.bom_app_notes = data.bom_app_notes || '';
        this.note = data.note || '';
        this.consumptions_note = data.consumptions_note || '';
        this.process_type = data.process_type || '';
        this.setup_end = (data.setup_end != false);
    }
    
    // Load Quality checks in each type list
    loadQualityChecks(q_checks) {
        for (let indx in q_checks) {
            var qc = q_checks[indx];
            if (qc.quality_type == 'start') {
                this.start_checks.push(qc);
            } else if (qc.quality_type == 'freq') {
                this.freq_checks.push(qc);
            }
        }
    }

    // Ask odoo for quality checks
    getQualityChecks() {
        var promise = new Promise( (resolve, reject) => {
            var values = {
                'product_id': this.product_id,
                'workcenter_id': this.workcenter['id'],
            }
            var method = 'get_quality_checks'
            this.odooCon.callRegistry(method, values).then((res) => {
                this.loadQualityChecks(res);
                resolve();
            })
            .catch( (err) => {
                console.log("GET QUALITY CHECKS ERROR")
                reject();
            });
        });
        return promise
    }

    loadConsumptions(lines) {
        /* Cargo los movimientos en la propiedad consumptions
           Se usa tanto en la página de consumos como en la de alimentador
        */
        this.consumptions = [];
        for (var indx in lines) {
            var line = lines[indx];
            var vals = {
                'product_id': line['product_id'][0],
                'product_name': line['product_id'][1],
                'uom_id': line['product_uom'][0],
                'uom_name': line['product_uom'][1],
                'qty': line['product_qty'],
                'location_id': line['location_id'][0],
                'location_name': line['location_id'][1],
            };
            this.consumptions.push(vals);
        }
        var grouped_lines = this.consumptions.reduce(function(a, e) {
          let key = (e['product_id'] + '|' + e['uom_id'] + '|' + e['location_id']);
          (!a[key] ? a[key] = e : (a[key]['qty'] += e['qty']));
          return a;
        }, {});
        this.consumptions = []
        for (let key in grouped_lines) {
             this.consumptions.push(grouped_lines[key])
        }
    }

    loadConsumptionsLines(lines) {
        this.consumptions_in = [];
        this.consumptions_out = [];
        this.consumptions_scrapped = [];
        this.finished_products = [];
        for (let indx in lines) {
            var line = lines[indx];
            var lot_name = '';
            var lot_id = false;
            if (line['lot_id']){
                lot_name = line['lot_id'][1]
                lot_id = line['lot_id'][0]
            }
            var type = line['type']
            var scrap_type_name = 'Desconocido'
            if (line['scrap_type'] == 'losses') {
                scrap_type_name = 'Mermas'
            }
            if (line['scrap_type'] == 'scrap') {
                scrap_type_name = 'Desechado'
            }
            var vals = {
                'product_id': line['product_id'][0],
                'product_name': line['product_id'][1],
                'uom_id': line['product_uom'][0],
                'uom_name': line['product_uom'][1],
                'qty': line['product_qty'],
                'location_id': line['location_id'][0],
                'location_name': line['location_id'][1],
                'lot_id': lot_id,
                'lot_name': lot_name,
                'lot_required': line['lot_required'],
                'type': type,
                'scrap_type': line['scrap_type'],
                'scrap_type_name': scrap_type_name,
                'id': line['id']
            }
            if (type == 'in') {
                this.consumptions_in.push(vals);
            }
            if (type == 'out') {
                this.consumptions_out.push(vals);
            }
            if (type == 'finished') {
                this.finished_products.push(vals);
            }
            if (type == 'scrapped') {
                this.consumptions_scrapped.push(vals);
            }
        }
    }

    getConsumptions() {
        var promise = new Promise( (resolve, reject) => {
            var domain = [['registry_id', '=', this.registry_id], ['type', '=', 'scheduled']]
            var fields = []
            this.odooCon.searchRead('consumption.line', domain, fields).then((lines) => {
                this.loadConsumptions(lines)
                resolve();
            })
            .catch( (err) => {
                console.log("Error obteniendo consumos");
            });
        });
        return promise
    }

    getConsumeInOut() {
        var promise = new Promise( (resolve, reject) => {
            var domain = [['registry_id', '=', this.registry_id]]
            var fields = []
            this.odooCon.searchRead('consumption.line', domain, fields).then((lines) => {
                this.loadConsumptionsLines(lines)
                resolve();
            })
            .catch( (err) => {
                console.log("Error obteniendo líneas de consumos");
            });
        });
        return promise
    }

    saveConsumptionLine(line) {
        var promise = new Promise( (resolve, reject) => {
            var values = {
                'registry_id': this.registry_id,
                'line': line,
            }
            this.odooCon.callRegistry('app_save_consumption_line', values).then((res) => {
                resolve();
            })
            .catch( (err) => {
                // this.manageOdooFail()
                reject();
            });
        });
        return promise
    }

    getMergedConsumptions() {
        var promise = new Promise( (resolve, reject) => {
            var values = {
                'registry_id': this.registry_id,
            }
            this.odooCon.callRegistry('get_merged_consumptions', values).then((res) => {
                let consumptions = res['lines']
                if (Array.isArray(consumptions) && consumptions.length) {
                    resolve(consumptions);
                } else {
                    reject();
                }
            })
            .catch( (err) => {
                reject();
            });
        });
        return promise
    }

    saveQualityChecks(data) {
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
        this.odooCon.callRegistry('app_save_quality_checks', values).then((res) => {
            console.log("RESULTADO GUARDADO")
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    manageOdooFail() {
        console.log("Guardo para escribir luego")
    }

    setStepAsync(method, values) {
        values['registry_id'] = this.registry_id;     
        this.odooCon.callRegistry(method, values).then((res) => {
            if (method == 'stop_production') {
                this.odooCon.stop_from_state = res['stop_from_state'];
            }
            if (res['state']) {
                this.state = res['state'];
            }
        })
        .catch( (err) => {
            this.manageOdooFail()
        });
    }

    setConsumptionsDone() {
        this.setStepAsync('set_consumptions_done', {});
    }

    unsetConsumptionsDone() {
        this.setStepAsync('unset_consumptions_done', {});
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

    stopProduction(reason_id, stop_start) {
        this.state = 'stopped'
        if (isNaN(Date.parse(stop_start))) {
            stop_start = this.getUTCDateStr()
        }
        var values = {'reason_id': reason_id,
                      'active_operator_id': this.active_operator_id,
                      'stop_start': stop_start}
        this.setStepAsync('stop_production', values);
    }

    restartProduction() {
        if (this.odooCon.stop_from_state in this.states) {
           this.state = this.odooCon.stop_from_state
        } else {
           this.state = 'started'
        }
        var values = {'stop_end': this.getUTCDateStr()}
        this.setStepAsync('restart_production', values);
    }

    cleanProduction(cleaning_start) {
        this.state = 'cleaning'
        if (isNaN(Date.parse(cleaning_start))) {
            cleaning_start = this.getUTCDateStr()
        }
        var values = {'cleaning_start': cleaning_start}
        this.setStepAsync('clean_production', values);
    }

    finishProduction() {
        this.state = 'finished'
        var values = {'qty': this.qty,
                      'cleaning_end': this.getUTCDateStr()}
        this.setStepAsync('finish_production', values);
    }

    restartAndCleanProduction(cleaning_start) {
        this.state = 'cleaning';
        if (isNaN(Date.parse(cleaning_start))) {
            cleaning_start = this.getUTCDateStr()
        }
        var values = {'cleaning_start': cleaning_start,
                      'stop_end': cleaning_start}
        this.setStepAsync('restart_and_clean_production', values);
    }

    scrapProduction() {
        var values = {'scrap_qty': this.scrap_qty, 'scrap_reason_id': this.scrap_reason_id};
        this.setStepAsync('scrap_production', values);
    }

    createMaintenanceOrder(reason_id) {
        var values = {'reason_id': reason_id}
        this.setStepAsync('create_maintenance_order', values);
    }

    editNote() {
        var values = {'note': this.note};
        this.setStepAsync('save_note', values);
    }

    editConsumptionsNote() {
        var values = {'consumptions_note': this.consumptions_note};
        this.setStepAsync('save_note', values);
    }

    registerMessage(msg) {
        var values = {'message': msg};
        this.setStepAsync('register_message', values);
    }

}
