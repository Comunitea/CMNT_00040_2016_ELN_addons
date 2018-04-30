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
    CONEXION = {
        url: 'http://192.168.0.131',
        port: '8069',
        db: 'pistola',
        username: 'admin',
        password: 'admin',
    };
    cargar = true;
    mensaje = '';
  
    constructor(public navCtrl: NavController, public navParams: NavParams, 
                private storage: Storage, public alertCtrl: AlertController,
                private auxData: AuxProvider, private odoo: OdooProvider) {
    
		var borrar = this.navParams.get('borrar');
		
        this.CONEXION.username = this.navParams.get('login') || this.CONEXION.username;
            if (borrar == true) {
                this.cargar = false;
                this.storage.remove('CONEXION');
            } else {
                this.conectarApp(false);
			}
	
    } 

	

    loginSinDatos() {
        var self = this;
        this.storage.get('res.users').then((val) => {
            if (val == null) {//no existe datos
                self.presentAlert('Falla!', 'Imposible conectarse');
            } else {
                self.navCtrl.setRoot(TreepickPage);
            }
            self.cargar = false;
        });
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
		if (this.CONEXION.username.length < 3 || this.CONEXION.password.length < 3 || this.CONEXION.url.length < 3 || this.CONEXION.db.length < 2) {
			this.cargar = false;
			this.presentAlert('Alerta!', 'Por favor verifica los datos usuario y contraseña');
			return;
		}
		
		this.storage.set('CONEXION', this.CONEXION)
		var model = 'res.users'
		var domain = [['login', '=', this.CONEXION.username]]
		var fields = ['id', 'login', 'image', 'name']
		var user = {id: null, name: null, image: null, login: null, cliente_id: null};
		this.odoo.login(this.CONEXION.username, this.CONEXION.password).then ((uid)=>{
			this.odoo.uid = uid
			
			this.odoo.searchRead(model, domain, fields).then((value)=>{
				this.cargar = false;
				if (value) {
					this.storage.set('CONEXION', this.CONEXION).then(() => {
						user.id = value[0].id;
						user.name = value[0].name;
						user.login = value[0].login;
						this.auxData.user = value
						this.navCtrl.setRoot(TreepickPage); 
					})
							
				}})
			.catch(() => {
				this.cargar = false;
				this.presentAlert('Error!', 'No se pudo recuperar el usuario odoo');
			});	
		})
		.catch(() => {
			this.cargar = false;
			this.presentAlert('Error!', 'No se pudo recuperar el usuario odoo');
		});
			

		
		
	}


    conectarApp2(verificar) {
        this.cargar = true;


        var con;
        con = this.CONEXION;
        this.storage.get('CONEXION').then((val) => {
        if (val == null) {//no existe datos         
			this.cargar = false;
			con = this.CONEXION;
            if (con.username.length < 3 || con.password.length < 3) {
                if (verificar) {
                    this.presentAlert('Alerta!', 'Por favor ingrese usuario y contraseña');
                }
			return;
        	}

		} 
		else {
        //si los trae directamente ya fueron verificados
			con = val;
			if (con.username.length < 3 || con.password.length < 3) {
				return this.cargar = false;
			}
			else {
				this.storage.set('CONEXION', con).then(() => {
					var model = 'res.users'
					var domain = [['login', '=', con.username]]
					var fields = ['id', 'login', 'image', 'name']
					var user = {id: null, name: null, image: null, login: null, cliente_id: null};
					
					this.odoo.searchRead(model, domain, fields).then((value)=>{
						if (value) {
							this.storage.set('CONEXION', con).then(() => {
								user.id = value[0].id;
								user.name = value[0].name;
								user.login = value[0].login;
								this.auxData.user = value
								this.navCtrl.setRoot(TreepickPage); 
							})
									
						}})
						.catch(() => {
							this.presentAlert('Error!', 'No se pudo recuperar la lista de operaciones contra odoo');
					});
				}).catch()
					

			}}
			

		}
		)}		
	

}
