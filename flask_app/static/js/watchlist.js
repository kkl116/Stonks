//use prepend method to add a td element to the table (append/prepend is inside - before and after is well before and after)
import { escapeSpecialChars, tickerFromId, formAjax, modifyErrorKeys, deleteRow } from "./helpers.js";
//to use import statements, requires script to be a module
//modules' functions reside within script itself, and cannot be accessed from html directly
//not the best practice, but can set functions as global var so that it can be called directly. 

function addAjax(url){
    function successFunc(success, fields){
        //append item to table - 
        const emptyMessage = document.getElementById('empty-message')
        const tableId = $("table[id^='watchlist-table']").attr('id')
        const table = document.getElementById(tableId)
        if (emptyMessage){
            emptyMessage.style.display="none"
        }
        console.log(success)
        table.insertAdjacentHTML('afterbegin', success.newItem);
        
        //remove error message and clear search bar
        fields['ticker-name'].input.value = '';
        document.getElementById('ticker-name').classList.remove('is-invalid');
        document.getElementById("ticker-name-error").style.display="none";
    };
    
    function errorFunc(errors, fields){
        //need to process error keys, b/c wtform fields different names as field keys
        let modErrors = modifyErrorKeys(errors, function(key){
            return key.replace('_', '-')
        })

        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                    document.getElementById("ticker-name-error").style.display="block";
                } else {
                    fields[key].input.classList.remove('is-invalid');
                    fields[key].error.innerHTML = null
                }
            }
        })
    };

    function keyFunc(key){
        return key.replace('-', '_')
    }

    let formId = 'add-form';
    let fieldIds = ['add-csrf', 'ticker-name'];

    formAjax(url=url, formId=formId,
    fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
    keyFunc=keyFunc);
}



/*toggle notes btn function
changing it here so that when it is clicked it will check wheter notes are already disaplyed - 
if not then will request from the server, and get tr to be displayed 
*/
function toggleNotes(clicked){
    const id = clicked.id;
    const ticker = tickerFromId(id, 1);
    const processedTicker = escapeSpecialChars(ticker)
    const notesId = '#' + processedTicker + '-notes';
    //check whether textarea is showing or not on page;
    if ($(notesId).length) {
        console.log('row exists')
        $(notesId).remove()
    } else {
        console.log('row does not exist')
        //textarea is not showing yet - get notes tr from server 
        const escapedId = escapeSpecialChars(id)
        const url = $('#' + escapedId).data('targ-url');
        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({
                ticker: ticker
            }),
            success: function(result){
                console.log('success')
                //insert notes tr
                let tickerRow = document.getElementById(ticker);
                tickerRow.insertAdjacentHTML('afterend', result.tr);

            },
            error: function(result){
                console.log('error')
                console.log(result)
            }
        })
    }

}

function saveNotes(clicked){
    const id = clicked.id;
    const ticker = tickerFromId(id, 2);
    const processedTicker = escapeSpecialChars(ticker)
    const notesTextId = processedTicker + '-text-area';
    const url = $(clicked).data('targ-url');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            ticker: ticker,
            notes: $('#' + notesTextId).val()
        }),
        success: function(result){
            console.log(result);
        },
        error: function(result){
            console.log(result);
        }
    })

}

window.addAjax=addAjax;
window.deleteRow=deleteRow;
window.toggleNotes=toggleNotes;
window.saveNotes=saveNotes;


