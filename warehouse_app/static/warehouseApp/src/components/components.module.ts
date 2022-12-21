import { NgModule } from '@angular/core';

import { ProductProductComponent } from './product-product/product-product';
import { ProductionLotComponent } from './production-lot/production-lot';
import { StockLocationComponent } from './stock-location/stock-location';
//import { StockPickingComponent } from './stock-picking/stock-picking';
//import { StockOperationComponent } from './stock-operation/stock-operation';
@NgModule({
    declarations: [
        ProductProductComponent,
        ProductionLotComponent,
        StockLocationComponent,
        //StockPickingComponent,
        //StockOperationComponent
    ],
    imports: [],
    exports: [
        ProductProductComponent,
        ProductionLotComponent,
        StockLocationComponent
        //StockPickingComponent,
        //StockOperationComponent
    ]
})
export class ComponentsModule { }
