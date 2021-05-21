import { formAjax, modifyErrorKeys, deleteRow } from './helpers.js';

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
            row.remove();
        }
        table.insertAdjacentHTML('afterbegin', success.newItem);

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
    }
    function keyFunc(key){
        return key.replace('-', '_')
    }
    let formId = 'add-form'
    let fieldIds = ['add-csrf', 'ticker-name', 'quantity', 'purchase-price']
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}


window.addAjax=addAjax
window.deleteRow=deleteRow
