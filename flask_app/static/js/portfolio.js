import { formAjax, modifyErrorKeys, escapeSpecialChars, error500Redirect} from './helpers.js';

function toggleLoading(){
    $('#wait').toggle()
    $('#main-content').toggle()
}

function orderAjax(url){

    function successFunc(success, fields){
        console.log(success)
        const emptyMessage = document.getElementById('empty-message');
        const table = document.getElementById('portfolio-table')
        if (emptyMessage){
            emptyMessage.style.display="none";
        }
        //append item to table - 
        //actually here it's a bit different - replaces original row if it's the same ticker
        let row = document.getElementById(success.id)
        if (row){
            $('#'+success.id).replaceWith(success.newItem)
        } else{
            table.insertAdjacentHTML('afterbegin', success.newItem);
        }
        //replace summary row 
        $('#summary').replaceWith(success.summary);

        toggleLoading();

        //remove error messages and clear fields
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token'){
                if (!key.includes('order-type')){
                    fields[key].input.value= '';
                    fields[key].input.classList.remove('is-valid');
                    fields[key].input.classList.remove('is-invalid');
                    fields[key].error.style.display="none";    
                }
            }
        })
    }
    function errorFunc(errors, fields){

        let modErrors = modifyErrorKeys(errors, function(key){
            return key.split('_').join('-')
        })

        console.log(errors)
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    console.log(key)
                    console.log('wrong')
                    fields[key].input.classList.remove('is-valid')
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    if (!key.includes('order-type')){
                        fields[key].input.classList.remove('is-invalid')
                        fields[key].input.classList.add('is-valid')
                        fields[key].error.innerHTML = null
                    }
                    
                }
            }
        })
        toggleLoading();
    }

    function keyFunc(key){
        return key.split('-').join('_')
    }

    function waitFunc(){
        toggleLoading();
    }

    function dataFunc(fields){
        let data = {};
        Object.keys(fields).forEach((key) => {
            let value = keyFunc(key);
            if (value.includes('order_type')){
                data['order_type'] = $('input:checked').val()
            } else{
                data[value] = fields[key].input.value;
            }

        })

        //append necessary values from table - just get the innerHTML of the different columns
        //get current summary row values -- 
        const tickerName = data['order_ticker_name'].toUpperCase().trim();
        data['summary-market_value'] = $('#summary-market_value').html();
        //need to find id of ticker-current-price 
        data['ticker-current-price'] = $('#' + escapeSpecialChars(tickerName) + '-current_price').html();

        console.log(data)
        return data
    }

    let formId = 'order-form'
    let fieldIds = ['order-csrf', 'order-ticker-name', 'order-quantity', 'order-price', 'order-type-0', 'order-type-1']
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc, waitFunc=waitFunc, dataFunc=dataFunc);
}

function fillSellFormTicker(clicked){
    const fieldId = 'order-ticker-name';
    const ticker = clicked.id.split('-')[0];
    $('#' + fieldId).val(ticker);
}


function tableAjax(urlOrder, urlLoadTable){
    //forms should be passed by default already - 
    function loadTableAjax(url){
        $.ajax({
            url: url,
            type: 'POST',
            success: function(response){
                //insert table
                const table = response.table;
                const empty = response.empty;
                const emptyMessage = document.getElementById('empty-message')
                if (empty) {
                    $('#empty-message').show()
                } else {
                    $('#empty-message').hide()
                };
                emptyMessage.insertAdjacentHTML('beforebegin', table);
                $('#portfolio-table').DataTable({
                    "order": [],
                });
                //toggle the main content and loading animation
                $('#loading').toggle();
                $('#main-content').toggle();

                //call rest of table ajax here 
                orderAjax(urlOrder);
            },
            error: function(response){
                console.log('error')
            }
        })
    }

    loadTableAjax(urlLoadTable);
}

window.fillSellFormTicker=fillSellFormTicker;
window.tableAjax=tableAjax;
