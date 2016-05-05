<html>

<head>
    <style type="text/css">
        ${css}
    </style>
</head>

<body>
    %for date in objects:
    <table style="page-break-after:avoid">
        <thead>
        </thead>
        <tbody>
            <tr>
                <td>
                    %for route in date[1]:
                    <table style="page-break-after:avoid">
                        <thead>
                            <tr>
                                <th colspan = 7>Desglose hasta la fecha: ${date[0]|entity}</th>
                            </tr>
                            <tr>
                                <th colspan = 7>Ruta: ${route[0]|entity} | Cajas: ${route[2]|entity} | Peso bruto: ${route[3]|entity} kg</th>
                            </tr>
                            <tr>
                                <th>${_("Codigo")}</th>
                                <th>${_("DUN-14/EAN-13")}</th>
                                <th>${_("Producto")}</th>
                                <th style="text-align:right">${_("Qty")}</th>
                                <th>${_("UoM")}</th>
                                <th style="text-align:right">${_("Qty (UoS)")}</th>
                                <th>${_("UoS")}</th>
                            </tr>
                        </thead>
                        <tbody>
                            %for product in route[1]:
                            <tr>
                            <tr height="20">
                                <td>${product[1]|entity}</td>
                                <td>${product[2]|entity}</td>
                                <td>${product[3]|entity}</td>
                                <td style="text-align:right">${product[4]|entity}</td>
                                <td>${product[5]|entity}</td>
                                <td style="text-align:right">${product[6]|entity}</td>
                                <td>${product[7]|entity}</td>
                                <td width="250">LOTES:</td>
                            </tr>
                                <td colspan="8"><hr/</td>
                            </tr>
                            %endfor
                        </tbody>
                    </table>
                    %endfor
                </td>
            </tr>
        </tbody>
    </table>
    %endfor
</body>

</html>
