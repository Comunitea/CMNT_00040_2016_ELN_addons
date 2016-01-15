<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <table class="list_table" >
        <thead>
            <tr>
                <th rowspan="2" >${_("Name")}</th><th colspan="3">${_("January")}</th>
                <th colspan="3" >${_("February")}</th><th colspan="3" >${_("March")}</th>
                <th colspan="3" >${_("April")}</th><th colspan="3" >${_("May")}</th>
                <th colspan="3" >${_("June")}</th><th colspan="3">${_("July")}</th>
                <th colspan="3" >${_("August")}</th><th colspan="3"  >${_("September")}</th>
                <th colspan="3" >${_("October")}</th><th colspan="3" >${_("November")}</th>
                <th colspan="3" >${_("December")}</th><th colspan="2" >${_("Tot")}</th>
            </tr>
            <tr>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th> <th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th><th>${_("%")}</th>
                <th>${_("Bdg.")}</th><th>${_("Real.")}</th>
            </tr>
        </thead>

        %for item in objects :
        <tbody>
        <tr style="background:#c4c4c4;">
            <td style="border-right:1px solid gray;text-align:left;">${item.name|entity}</td>

           %if item.jandiff < 0.00:
                <td class="negative">${item.jan_amount|entity}</td><td class="negative">${item.jan_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.jandiff|entity}</td>
           %elif item.jandiff > 0.00:
                <td class="positive">${item.jan_amount|entity}</td><td class="positive">${item.jan_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.jandiff|entity}</td>
           %else :
                <td class="normal">${item.jan_amount|entity}</td><td class="normal">${item.jan_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.jandiff|entity}</td>
           %endif

           %if item.febdiff < 0:
                <td class="negative">${item.feb_amount|entity}</td><td class="negative">${item.feb_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.febdiff|entity}</td>
           %elif item.febdiff > 0:
                <td class="positive">${item.feb_amount|entity}</td><td class="positive">${item.feb_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.febdiff|entity}</td>
           %else :
                <td class="normal">${item.feb_amount|entity}</td><td class="normal">${item.feb_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.febdiff|entity}</td>
           %endif

           %if item.mardiff < 0:
                <td class="negative">${item.mar_amount|entity}</td><td class="negative">${item.mar_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.mardiff|entity}</td>
           %elif item.mardiff > 0:
                <td class="positive">${item.mar_amount|entity}</td><td class="positive">${item.mar_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.mardiff|entity}</td>
           %else :
                <td class="normal">${item.mar_amount|entity}</td><td class="normal">${item.mar_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.mardiff|entity}</td>
           %endif

           %if item.aprdiff < 0:
                <td class="negative">${item.apr_amount|entity}</td><td class="negative">${item.apr_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.aprdiff|entity}</td>
           %elif item.aprdiff > 0:
                <td class="positive">${item.apr_amount|entity}</td><td class="positive">${item.apr_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.aprdiff|entity}</td>
           %else :
                <td class="normal">${item.apr_amount|entity}</td><td class="normal">${item.apr_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.aprdiff|entity}</td>
           %endif

           %if item.maydiff < 0:
                <td class="negative">${item.may_amount|entity}</td><td class="negative">${item.may_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.maydiff|entity}</td>
           %elif item.maydiff > 0:
                <td class="positive">${item.may_amount|entity}</td><td class="positive">${item.may_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.maydiff|entity}</td>
           %else :
                <td class="normal">${item.may_amount|entity}</td><td class="normal">${item.may_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.maydiff|entity}</td>
           %endif

           %if item.jundiff < 0:
                <td class="negative">${item.jun_amount|entity}</td><td class="negative">${item.jun_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.jundiff|entity}</td>
           %elif item.jundiff > 0:
                <td class="positive">${item.jun_amount|entity}</td><td class="positive">${item.jun_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.jundiff|entity}</td>
           %else :
                <td class="normal">${item.jun_amount|entity}</td><td class="normal">${item.jun_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.jundiff|entity}</td>
           %endif

           %if item.juldiff < 0:
                <td class="negative">${item.jul_amount|entity}</td><td class="negative">${item.jul_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.juldiff|entity}</td>
           %elif item.juldiff > 0:
                <td class="positive">${item.jul_amount|entity}</td><td class="positive">${item.jul_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.juldiff|entity}</td>
           %else :
                <td class="normal">${item.jul_amount|entity}</td><td class="normal">${item.jul_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.juldiff|entity}</td>
           %endif

           %if item.augdiff < 0:
                <td class="negative">${item.aug_amount|entity}</td><td class="negative">${item.aug_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.augdiff|entity}</td>
           %elif item.augdiff > 0:
                <td class="positive">${item.aug_amount|entity}</td><td class="positive">${item.aug_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.augdiff|entity}</td>
           %else :
                <td class="normal">${item.aug_amount|entity}</td><td class="normal">${item.aug_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.augdiff|entity}</td>
           %endif

           %if item.sepdiff < 0:
                <td class="negative">${item.sep_amount|entity}</td><td class="negative">${item.sep_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.sepdiff|entity}</td>
           %elif item.sepdiff > 0:
                <td class="positive">${item.sep_amount|entity}</td><td class="positive">${item.sep_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.sepdiff|entity}</td>
           %else :
                <td class="normal">${item.sep_amount|entity}</td><td class="normal">${item.sep_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.sepdiff|entity}</td>
           %endif

           %if item.octdiff < 0:
                <td class="negative">${item.oct_amount|entity}</td><td class="negative">${item.oct_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.octdiff|entity}</td>
           %elif item.octdiff > 0:
                <td class="positive">${item.oct_amount|entity}</td><td class="positive">${item.oct_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.octdiff|entity}</td>
           %else :
                <td class="normal">${item.oct_amount|entity}</td><td class="normal">${item.oct_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.octdiff|entity}</td>
           %endif

           %if item.novdiff < 0:
                <td class="negative">${item.nov_amount|entity}</td><td class="negative">${item.nov_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.novdiff|entity}</td>
           %elif item.novdiff > 0:
                <td class="positive">${item.nov_amount|entity}</td><td class="positive">${item.nov_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.novdiff|entity}</td>
           %else :
                <td class="normal">${item.nov_amount|entity}</td><td class="normal">${item.nov_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.novdiff|entity}</td>
           %endif

           %if item.decdiff < 0:
                <td class="negative">${item.dec_amount|entity}</td><td class="negative">${item.dec_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${item.decdiff|entity}</td>
           %elif item.decdiff > 0:
                <td class="positive">${item.dec_amount|entity}</td><td class="positive">${item.dec_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${item.decdiff|entity}</td>
           %else :
                <td class="normal">${item.dec_amount|entity}</td><td class="normal">${item.dec_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${item.decdiff|entity}</td>
           %endif
   
           <td>${ item.prev_amount |entity}</td>
            <td style="border-right:1px solid gray;">${item.real_amount|entity}</td>
            
        </tr>
            %for line in item.analytic_lines :
            <tr style="background:#e0e0e0;">
                <td style="border-right:1px solid gray;text-align:left;">${line.name|entity}</td>

               %if line.jandiff < 0.00:
                    <td class="negative">${line.jan_amount|entity}</td><td class="negative">${line.jan_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.jandiff|entity}</td>
               %elif line.jandiff > 0.00:
                    <td class="positive">${line.jan_amount|entity}</td><td class="positive">${line.jan_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.jandiff|entity}</td>
               %else :
                    <td class="normal">${line.jan_amount|entity}</td><td class="normal">${line.jan_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.jandiff|entity}</td>
               %endif

               %if line.febdiff < 0:
                    <td class="negative">${line.feb_amount|entity}</td><td class="negative">${line.feb_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.febdiff|entity}</td>
               %elif line.febdiff > 0:
                    <td class="positive">${line.feb_amount|entity}</td><td class="positive">${line.feb_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.febdiff|entity}</td>
               %else :
                    <td class="normal">${line.feb_amount|entity}</td><td class="normal">${line.feb_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.febdiff|entity}</td>
               %endif

               %if line.mardiff < 0:
                    <td class="negative">${line.mar_amount|entity}</td><td class="negative">${line.mar_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.mardiff|entity}</td>
               %elif line.mardiff > 0:
                    <td class="positive">${line.mar_amount|entity}</td><td class="positive">${line.mar_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.mardiff|entity}</td>
               %else :
                    <td class="normal">${line.mar_amount|entity}</td><td class="normal">${line.mar_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.mardiff|entity}</td>
               %endif

               %if line.aprdiff < 0:
                    <td class="negative">${line.apr_amount|entity}</td><td class="negative">${line.apr_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.aprdiff|entity}</td>
               %elif line.aprdiff > 0:
                    <td class="positive">${line.apr_amount|entity}</td><td class="positive">${line.apr_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.aprdiff|entity}</td>
               %else :
                    <td class="normal">${line.apr_amount|entity}</td><td class="normal">${line.apr_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.aprdiff|entity}</td>
               %endif

               %if line.maydiff < 0:
                    <td class="negative">${line.may_amount|entity}</td><td class="negative">${line.may_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.maydiff|entity}</td>
               %elif line.maydiff > 0:
                    <td class="positive">${line.may_amount|entity}</td><td class="positive">${line.may_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.maydiff|entity}</td>
               %else :
                    <td class="normal">${line.may_amount|entity}</td><td class="normal">${line.may_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.maydiff|entity}</td>
               %endif

               %if line.jundiff < 0:
                    <td class="negative">${line.jun_amount|entity}</td><td class="negative">${line.jun_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.jundiff|entity}</td>
               %elif line.jundiff > 0:
                    <td class="positive">${line.jun_amount|entity}</td><td class="positive">${line.jun_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.jundiff|entity}</td>
               %else :
                    <td class="normal">${line.jun_amount|entity}</td><td class="normal">${line.jun_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.jundiff|entity}</td>
               %endif

               %if line.juldiff < 0:
                    <td class="negative">${line.jul_amount|entity}</td><td class="negative">${line.jul_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.juldiff|entity}</td>
               %elif line.juldiff > 0:
                    <td class="positive">${line.jul_amount|entity}</td><td class="positive">${line.jul_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.juldiff|entity}</td>
               %else :
                    <td class="normal">${line.jul_amount|entity}</td><td class="normal">${line.jul_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.juldiff|entity}</td>
               %endif

               %if line.augdiff < 0:
                    <td class="negative">${line.aug_amount|entity}</td><td class="negative">${line.aug_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.augdiff|entity}</td>
               %elif line.augdiff > 0:
                    <td class="positive">${line.aug_amount|entity}</td><td class="positive">${line.aug_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.augdiff|entity}</td>
               %else :
                    <td class="normal">${line.aug_amount|entity}</td><td class="normal">${line.aug_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.augdiff|entity}</td>
               %endif

               %if line.sepdiff < 0:
                    <td class="negative">${line.sep_amount|entity}</td><td class="negative">${line.sep_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.sepdiff|entity}</td>
               %elif line.sepdiff > 0:
                    <td class="positive">${line.sep_amount|entity}</td><td class="positive">${line.sep_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.sepdiff|entity}</td>
               %else :
                    <td class="normal">${line.sep_amount|entity}</td><td class="normal">${line.sep_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.sepdiff|entity}</td>
               %endif

               %if line.octdiff < 0:
                    <td class="negative">${line.oct_amount|entity}</td><td class="negative">${line.oct_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.octdiff|entity}</td>
               %elif line.octdiff > 0:
                    <td class="positive">${line.oct_amount|entity}</td><td class="positive">${line.oct_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.octdiff|entity}</td>
               %else :
                    <td class="normal">${line.oct_amount|entity}</td><td class="normal">${line.oct_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.octdiff|entity}</td>
               %endif

               %if line.novdiff < 0:
                    <td class="negative">${line.nov_amount|entity}</td><td class="negative">${line.nov_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.novdiff|entity}</td>
               %elif line.novdiff > 0:
                    <td class="positive">${line.nov_amount|entity}</td><td class="positive">${line.nov_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.novdiff|entity}</td>
               %else :
                    <td class="normal">${line.nov_amount|entity}</td><td class="normal">${line.nov_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.novdiff|entity}</td>
               %endif

               %if line.decdiff < 0:
                    <td class="negative">${line.dec_amount|entity}</td><td class="negative">${line.dec_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${line.decdiff|entity}</td>
               %elif line.decdiff > 0:
                    <td class="positive">${line.dec_amount|entity}</td><td class="positive">${line.dec_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${line.decdiff|entity}</td>
               %else :
                    <td class="normal">${line.dec_amount|entity}</td><td class="normal">${line.dec_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${line.decdiff|entity}</td>
               %endif

               <td>${ line.prev_amount |entity}</td>
                <td style="border-right:1px solid gray;">${line.real_amount|entity}</td>

                
                %for product in line.product_lines :
                 <tr>
                    <td style="border-right:1px solid gray;text-align:left;">${product.name|entity}</td>
                        %if line.jandiff < 0.00:
                    <td class="negative">${product.jan_amount|entity}</td><td class="negative">${product.jan_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.jandiff|entity}</td>
                       %elif product.jandiff > 0.00:
                            <td class="positive">${product.jan_amount|entity}</td><td class="positive">${product.jan_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.jandiff|entity}</td>
                       %else :
                            <td class="normal">${product.jan_amount|entity}</td><td class="normal">${product.jan_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.jandiff|entity}</td>
                       %endif

                       %if product.febdiff < 0:
                            <td class="negative">${product.feb_amount|entity}</td><td class="negative">${product.feb_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.febdiff|entity}</td>
                       %elif product.febdiff > 0:
                            <td class="positive">${product.feb_amount|entity}</td><td class="positive">${product.feb_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.febdiff|entity}</td>
                       %else :
                            <td class="normal">${product.feb_amount|entity}</td><td class="normal">${product.feb_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.febdiff|entity}</td>
                       %endif

                       %if product.mardiff < 0:
                            <td class="negative">${product.mar_amount|entity}</td><td class="negative">${product.mar_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.mardiff|entity}</td>
                       %elif product.mardiff > 0:
                            <td class="positive">${product.mar_amount|entity}</td><td class="positive">${product.mar_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.mardiff|entity}</td>
                       %else :
                            <td class="normal">${product.mar_amount|entity}</td><td class="normal">${product.mar_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.mardiff|entity}</td>
                       %endif

                       %if product.aprdiff < 0:
                            <td class="negative">${product.apr_amount|entity}</td><td class="negative">${product.apr_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.aprdiff|entity}</td>
                       %elif product.aprdiff > 0:
                            <td class="positive">${product.apr_amount|entity}</td><td class="positive">${product.apr_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.aprdiff|entity}</td>
                       %else :
                            <td class="normal">${product.apr_amount|entity}</td><td class="normal">${product.apr_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.aprdiff|entity}</td>
                       %endif

                       %if product.maydiff < 0:
                            <td class="negative">${product.may_amount|entity}</td><td class="negative">${product.may_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.maydiff|entity}</td>
                       %elif product.maydiff > 0:
                            <td class="positive">${product.may_amount|entity}</td><td class="positive">${product.may_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.maydiff|entity}</td>
                       %else :
                            <td class="normal">${product.may_amount|entity}</td><td class="normal">${product.may_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.maydiff|entity}</td>
                       %endif

                       %if product.jundiff < 0:
                            <td class="negative">${product.jun_amount|entity}</td><td class="negative">${product.jun_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.jundiff|entity}</td>
                       %elif product.jundiff > 0:
                            <td class="positive">${product.jun_amount|entity}</td><td class="positive">${product.jun_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.jundiff|entity}</td>
                       %else :
                            <td class="normal">${product.jun_amount|entity}</td><td class="normal">${product.jun_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.jundiff|entity}</td>
                       %endif

                       %if product.juldiff < 0:
                            <td class="negative">${product.jul_amount|entity}</td><td class="negative">${product.jul_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.juldiff|entity}</td>
                       %elif product.juldiff > 0:
                            <td class="positive">${product.jul_amount|entity}</td><td class="positive">${product.jul_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.juldiff|entity}</td>
                       %else :
                            <td class="normal">${product.jul_amount|entity}</td><td class="normal">${product.jul_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.juldiff|entity}</td>
                       %endif

                       %if product.augdiff < 0:
                            <td class="negative">${product.aug_amount|entity}</td><td class="negative">${product.aug_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.augdiff|entity}</td>
                       %elif product.augdiff > 0:
                            <td class="positive">${product.aug_amount|entity}</td><td class="positive">${product.aug_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.augdiff|entity}</td>
                       %else :
                            <td class="normal">${product.aug_amount|entity}</td><td class="normal">${product.aug_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.augdiff|entity}</td>
                       %endif

                       %if product.sepdiff < 0:
                            <td class="negative">${product.sep_amount|entity}</td><td class="negative">${product.sep_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.sepdiff|entity}</td>
                       %elif product.sepdiff > 0:
                            <td class="positive">${product.sep_amount|entity}</td><td class="positive">${product.sep_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.sepdiff|entity}</td>
                       %else :
                            <td class="normal">${product.sep_amount|entity}</td><td class="normal">${product.sep_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.sepdiff|entity}</td>
                       %endif

                       %if product.octdiff < 0:
                            <td class="negative">${product.oct_amount|entity}</td><td class="negative">${product.oct_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.octdiff|entity}</td>
                       %elif product.octdiff > 0:
                            <td class="positive">${product.oct_amount|entity}</td><td class="positive">${product.oct_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.octdiff|entity}</td>
                       %else :
                            <td class="normal">${product.oct_amount|entity}</td><td class="normal">${product.oct_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.octdiff|entity}</td>
                       %endif

                       %if product.novdiff < 0:
                            <td class="negative">${product.nov_amount|entity}</td><td class="negative">${product.nov_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.novdiff|entity}</td>
                       %elif product.novdiff > 0:
                            <td class="positive">${product.nov_amount|entity}</td><td class="positive">${product.nov_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.novdiff|entity}</td>
                       %else :
                            <td class="normal">${product.nov_amount|entity}</td><td class="normal">${product.nov_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.novdiff|entity}</td>
                       %endif

                       %if product.decdiff < 0:
                            <td class="negative">${product.dec_amount|entity}</td><td class="negative">${product.dec_amount_real|entity}</td><td class="negative" style="border-right:1px solid gray;">${product.decdiff|entity}</td>
                       %elif product.decdiff > 0:
                            <td class="positive">${product.dec_amount|entity}</td><td class="positive">${product.dec_amount_real|entity}</td><td class="positive" style="border-right:1px solid gray;">${product.decdiff|entity}</td>
                       %else :
                            <td class="normal">${product.dec_amount|entity}</td><td class="normal">${product.dec_amount_real|entity}</td><td class="normal" style="border-right:1px solid gray;">${product.decdiff|entity}</td>
                       %endif

               <td>${ product.prev_amount |entity}</td>
                <td style="border-right:1px solid gray;">${product.real_amount|entity}</td>
                </tr>
                %endfor

             </tr>
            %endfor
        %endfor

        </tbody>
    </table>
    <p style="page-break-after:always"></p>

</body>
</html>