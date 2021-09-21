import { formAjax, modifyErrorKeys, escapeSpecialChars } from './helpers.js';

function toggleLoading(){
    $('#wait').toggle()
    $('#main-content').toggle()
}

function addAjax(url){

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
                fields[key].input.value= '';
                fields[key].input.classList.remove('is-invalid');
                fields[key].error.style.display="none";    
            }
        })
    }
    function errorFunc(errors, fields){

        let modErrors = modifyErrorKeys(errors, function(key){
            return key.replace('_', '-')
        })
        console.log(modErrors)
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    fields[key].input.classList.remove('is-invalid')
                    fields[key].error.innerHTML = null
                }
            }
        })
        toggleLoading();
    }

    function keyFunc(key){
        return key.replace('-', '_')
    }

    function waitFunc(){
        toggleLoading();
    }

    function dataFunc(fields){
        let data = {};
        Object.keys(fields).forEach((key) => {
            let value = keyFunc(key);
            data[value] = fields[key].input.value
        })
        //append necessary values from table - just get the innerHTML of the different columns
        //get current summary row values -- 
        data['summary-market_value'] = $('#summary-market_value').html();
        console.log(data)
        return data
    }

    let formId = 'add-form'
    let fieldIds = ['add-csrf', 'ticker-name', 'quantity', 'purchase-price']
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc, waitFunc=waitFunc, dataFunc=dataFunc);
}

function fillSellFormTicker(clicked){
    const fieldId = 'sell-ticker-name';
    const ticker = clicked.id.split('-')[0];
    $('#' + fieldId).val(ticker);
}


function sellAjax(url){

    function successFunc(success, fields){
        console.log(success)
        const emptyMessage = document.getElementById('empty-message');
        const table = document.getElementById('portfolio-table')
        if (emptyMessage){
            emptyMessage.style.display="none";
        }
        //append item to table - 
        //actually here it's a bit different - replaces original row if it's the same ticker
        let row = document.getElementById(success.id);
        if (row && success.newItem){
            //replace row if newItem contains new element
            $('#'+success.id).replaceWith(success.newItem)
        } else if (row && !success.newItem){
            //if row exists and newItem does not contain new element - remove row 
            $('#'+success.id).remove()
        };
        //replace summary row 
        $('#summary').replaceWith(success.summary);

        toggleLoading();

        //remove error messages and clear fields
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token'){
                fields[key].input.value= '';
                fields[key].input.classList.remove('is-invalid');
                fields[key].error.style.display="none";    
            }
        })
    }
    function errorFunc(errors, fields){

        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'sell-' + key
            return key.replace('_', '-')
        })
        console.log(modErrors)
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    fields[key].input.classList.remove('is-invalid')
                    fields[key].error.innerHTML = null
                }
            }
        })
        toggleLoading();
    }

    function keyFunc(key){
        return key.replace('sell-', '').replace('-', '_')
    }

    function waitFunc(){
        toggleLoading();
    }

    function dataFunc(fields){
        let data = {};
        Object.keys(fields).forEach((key) => {
            let value = keyFunc(key);
            data[value] = fields[key].input.value
        })
        //append necessary values from table - just get the innerHTML of the different columns
        //get current summary row values -- 
        const tickerName = data['ticker_name'].toUpperCase().trim();
        data['summary-market_value'] = $('#summary-market_value').html();
        //need to find id of ticker-current-price 
        data['ticker-current-price'] = $('#' + escapeSpecialChars(tickerName) + '-current_price').html();

        console.log(data)
        return data
    }

    let formId = 'sell-form'
    let fieldIds = ['sell-csrf', 'sell-ticker-name', 'sell-quantity', 'sell-price']
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc, waitFunc=waitFunc, dataFunc=dataFunc);
}

function tableAjax(urlAdd, urlLoadTable, urlSell){
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
                addAjax(urlAdd);
                sellAjax(urlSell);
            },
            error: function(response){
                console.log('error')
                console.log(response)
            }
        })
    }

    loadTableAjax(urlLoadTable);
}

window.fillSellFormTicker=fillSellFormTicker;
window.tableAjax=tableAjax;
