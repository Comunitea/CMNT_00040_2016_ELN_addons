import { HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';


import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';

/*
  Generated class for the OdooConnectorProvider provider.

  See https://angular.io/guide/dependency-injection for more info on providers
  and Angular DI.
*/

export class BDUser {
  id: number;
  name: string;
 
  quantity: number;
  constructor(values: Object = {}) {
       Object.assign(this, values);
  }
} 

class Cookies { // cookies doesn't work with Android default browser / Ionic

    private session_id: string = null;

    delete_sessionId() {
        this.session_id = null;
        document.cookie = "session_id=; expires=Wed, 29 Jun 2016 00:00:00 UTC";
    }

    get_sessionId() {
        return document
                .cookie.split("; ")
                .filter(x => { return x.indexOf("session_id") === 0; })
                .map(x => { return x.split("=")[1]; })
                .pop() || this.session_id || "";
    }

    set_sessionId(val: string) {
        document.cookie = `session_id=${val}`;
        this.session_id = val;
    }
}


@Injectable()
export class OdooConnectorProvider {

  private odoo_server: string;
  private http_auth: string;
  private db: string;
  private db_user: string;
  private db_pass: string
  private cookies: Cookies;
  private context: Object = {"lang": "es_ES"};

  constructor(public http: HttpClient) {
    console.log('Hello OdooConnectorProvider Provider');
    
  }
  
  public init(configs: any) {
    this.odoo_server = 'odoopistola.com';
    this.http_auth = configs.http_auth || null;
    this.db = 'pistola';
    this.db_user ='admin';
    this.db_pass = 'admin';
    //this.cookies = new Cookies();
}

  get_http_headers(){
   
    let $this = this;  
    let headers = {
      "Content-Type": "text/plain",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "origin, x-requested-with, content-type",
      "Access-Control-Allow-Methods": "PUT, GET, POST, DELETE, OPTIONS",
      "X-Openerp-Session-Id": $this.cookies.get_sessionId()
      };
    return headers;
  }

  public login() {
   
    let $this = this;  
    this.init('');
    let params = {
              db : this.db,
              login : this.db_user,
              password : this.db_pass
          };
    let headers = {
      "Content-Type": "text/plain",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "origin, x-requested-with, content-type",
      "Access-Control-Allow-Methods": "PUT, GET, POST, DELETE, OPTIONS"
      };  
    this.http.post("http://odoopistola.com/web/session/authenticate", {params, headers})
        .toPromise()
        .then(function(result: any) {
          console.log('Then .....');
          console.log(result.result);
          if (!result.result['uid']) {
            console.log(result.result['uid'])
              $this.cookies.delete_sessionId();
              return Promise.reject({
                  title: "wrong_login",
                  message: "Username and password don't match",
                  fullTrace: result
              })
        .catch(this.handleHttpErrors);;
          }
    $this.context = result.result['user_context'];
    localStorage.setItem("user_context", result.result['user_context']) ;
    $this.cookies.set_sessionId(result.result['session_id']);
    console.log(localStorage.getItem('user_context'));
    return Promise.resolve(result);
      });
  }

  public getUsers() {
    
     let $this = this;  
     //this.init('');
     let params = {
        //       db : this.db,
          //     login : this.db_user,
            //   password : this.db_pass,
           
            model: 'res.users',
            domain: [],
            fields: ['name'],
            context: this.context
        };
     let headers = {
       "Content-Type": "text/plain",
       "Access-Control-Allow-Origin": "*",
       "Access-Control-Allow-Headers": "origin, x-requested-with, content-type",
       "Access-Control-Allow-Methods": "PUT, GET, POST, DELETE, OPTIONS"
       };  
     return new Promise(resolve => {
       this.http.post("http://odoopistola.com/web/dataset/search_read", {params, headers}).subscribe (data=> {
       resolve(data);}
      )
    }
  )
           
     //$this.context = result.result['user_context'];
     //localStorage.setItem("user_context", result.result['user_context']) ;
     //$this.cookies.set_sessionId(result.result['session_id']);
     //console.log(localStorage.getItem('user_context'));
     //return Promise.resolve(result);
       
  }


}
