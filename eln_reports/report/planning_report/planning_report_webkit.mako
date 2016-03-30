<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>

%for route in objects:

    <p style="font-size:18;font-weight:bold;">${route.name|entity}(${route.code|entity}) </p>
    %if route.carrier:
        <p style="font-size:15;">${_("Carrier")}: route.carrier</p>
    %endif

    <table class="list_table">
        <thead>
            <tr>
                <th>${_("Code")}</th>
                <th>${_("Product")}</th>
                <th >${_("Qty")}</th>
                <th>${_("UoM")}</th>
                <th >${_("Qty (UoS)")}</th>
                <th>${_("UoS")}</th>
            </tr>
        </thead>

        %for product in route.lines :
        <tbody>
        <tr>
            <td>${product.code|entity}</td>
            <td>${product.name|entity}</td>
            <td>${product.qty|entity}</td>
            <td>${product.uom|entity}</td>
            <td>${product.uos_qty|entity}</td>
            <td>${product.uos|entity}</td>
        </tr>
        %endfor
        </tbody>
    </table>
%endfor

    <p style="page-break-after:always"></p>

</body>
</html>
