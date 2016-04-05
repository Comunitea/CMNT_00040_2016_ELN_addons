<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>


%for date in objects:
    <table style="page-break-after:always">
        <thead>
            <tr><th style="text-align:left">
            Fecha de Previsión: ${date[0]|entity}
            <hr>
            </th></tr>
        </thead>
        <tbody>
            <tr><td>
            %for route in date[1]:
                <table>

                    <thead>
                        <tr>
                            <th colspan = 6 >Ruta: ${route[0]|entity}</th>
                        </tr>
                        <tr>
                            <th>${_("Codigo")}</th>
                            <th>${_("Producto")}</th>
                            <th>${_("Qty")}</th>
                            <th>${_("UoM")}</th>
                            <th>${_("Qty (UoS)")}</th>
                            <th>${_("UoS")}</th>
                        </tr>
                    </thead>
                    <tbody>
                        %for product in route[1]:
                        <tr>
                            <td>${product[0]|entity}</td>
                            <td>${product[1]|entity}</td>
                            <td>${product[2]|entity}</td>
                            <td>${product[3]|entity}</td>
                            <td>${product[4]|entity}</td>
                            <td>${product[5]|entity}</td>
                        </tr>
                        %endfor
                    </tbody>
                </table>
            %endfor
            </td></tr>
            </tbody>
    </table>
%endfor
</body>
</html>
