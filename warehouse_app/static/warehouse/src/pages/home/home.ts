import {NavController, NavParams, AlertController} from 'ionic-angular';
import {Component} from '@angular/core';

import {Storage} from '@ionic/storage';
import { TreepickPage} from '../../pages/treepick/treepick';
import { AuxProvider } from '../../providers/aux/aux';
import { OdooProvider } from '../../providers/odoo-connector/odoo-connector';



@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})

export class HomePage {

    loginData = {password: '', username: ''};
    CONEXION_remote = {
        url: 'http://elnapp.livingodoo.com/',
        port: '8069',
        db: 'elnapp',
        username: 'pda',
		password: 'cmnt',
		user: {}
	};
	CONEXION_local = {
        url: 'http://192.168.0.121/',
        port: '8069',
        db: 'pistola2',
        username: 'pda',
		password: 'cmnt',
		user: {}
	};
	CONEXION = {
		url: '',
        port: '',
        db: '',
        username: '',
		password: '',
		user: {}
	}
	
    cargar = false;
	mensaje = '';
	login_server: boolean = false

    constructor(public navCtrl: NavController, public navParams: NavParams,
                private storage: Storage, public alertCtrl: AlertController,
                private odoo: OdooProvider) {
		
		this.login_server = false
		
		if (this.navParams.get('login')){
			this.CONEXION.username = this.navParams.get('login')};

		this.check_storage_conexion(this.navParams.get('borrar'))
    }

	check_storage_conexion(borrar){
		if (borrar){
			this.CONEXION = this.CONEXION_local;
		}	
		else {
			this.storage.get('CONEXION').then((val) => {
				if (val && val['login']){
					this.CONEXION = val
				}
				else{
					this.CONEXION = this.CONEXION_local;
					this.storage.set('CONEXION', this.CONEXION).then(()=>{
				})
			}
			})
		}
	}

    presentAlert(titulo, texto) {
        const alert = this.alertCtrl.create({
            title: titulo,
            subTitle: texto,
            buttons: ['Ok']
        });
        alert.present();
    }


	conectarApp(verificar){
		this.cargar = true;
		if (verificar){
			this.storage.set('CONEXION', this.CONEXION).then(() => {
				this.check_conexion(this.CONEXION)
			})
		}

		else {
			this.storage.get('CONEXION').then((val) => {
				var con;
				if (val == null) {//no existe datos         
					this.cargar = false;
					con = this.CONEXION;
					if (con.username.length < 3 || con.password.length < 3) {
						if (verificar) {
							this.presentAlert('Alerta!', 'Por favor ingrese usuario y contraseña');
						}
					return;
					}
		
				} else {
				//si los trae directamente ya fueron verificados
					con = val;
					if (con.username.length < 3 || con.password.length < 3) {
						this.cargar = false;
						return
					}
				}
				if (con){
					this.storage.set('CONEXION', con).then(() => {
						this.check_conexion(con)
						this.cargar=false
					})
				}
			})
		}
	}
	check_conexion(con) {	
		var model = 'res.users'
		var domain = [['login', '=', con.username]]
		var fields = ['id', 'login', 'image', 'name', 'company_id']
		this.odoo.login(con.username, con.password).then ((uid)=>{
			this.odoo.uid = uid
			this.odoo.searchRead(model, domain, fields).then((value)=>{
				var user = {id: null, name: null, image: null, login: null, cliente_id: null, company_id: null};
				if (value) {
					if (!con.user || value[0].id != con.user['id'] || value[0].company_id[0] != con.user['company_id']){
						user = value[0];
						//user.id = value[0].id;
						//user.name = value[0].name;
						//user.login = value[0].login;
						//user.company_id = value[0].company_id[0];
						//user.company = value[0].company_id
						con.user = user
					}
					this.storage.set('CONEXION', con).then(()=>{
						this.navCtrl.setRoot(TreepickPage);
					})
				}})
			.catch(() => {
				this.cargar = false;
				this.presentAlert('Error!', 'No se pudo encontrar el usuario:' + con.username);
			});
		})
		.catch (()=>{
			this.presentAlert('Error!', 'No se pudo conectar a Odoo');
			this.cargar = false;
		})
	}
}
