//use prepend method to add a td element to the table (append/prepend is inside - before and after is well before and after)
import { escapeSpecialChars, tickerFromId } from "./helpers.js";
//to use import statements, requires script to be a module
//modules' functions reside within script itself, and cannot be accessed from html directly
//not the best practice, but can set functions as global var so that it can be called directly. 

function addAjax(url){
    const form = document.getElementById('add-form');
    //put a const here to reference to a success flash message - called after modal closed
    const fields = {
        csrf_token: {
            input: document.getElementById('add-csrf'),
        },
        ticker_name: {
            input: document.getElementById('ticker-name'),
            error: document.getElementById('ticker-name-error')
        },
    }
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                csrf_token: fields.csrf_token.input.value,
                ticker_name: fields.ticker_name.input.value
            })
        });
        if (response.ok) {
            const success = await response.json();
            //append item to table - 
            const emptyMessage = document.getElementById('empty-message')
            const table = document.getElementById('watchlist-table')
            if (emptyMessage){
                emptyMessage.style.display="none"
            }
            console.log(success)
            table.insertAdjacentHTML('afterbegin', success.newItem);
            
            //remove error message and clear search bar
            fields['ticker_name'].input.value = '';
            document.getElementById('ticker-name').classList.remove('is-invalid');
            document.getElementById("ticker-name-error").style.display="none";
        } else {
            //remove the errors from the previous submit 
            const errors = await response.json();
            Object.keys(fields).forEach((key) => {
                if (key != 'csrf_token') {
                    if (Object.keys(errors).includes(key)) {
                        fields[key].input.classList.add('is-invalid');
                        fields[key].error.innerHTML = errors[key][0];
                        document.getElementById("ticker-name-error").style.display="block";
                    } else {
                        fields[key].input.classList.remove('is-invalid');
                        fields[key].error.innerHTML = null
                    }
                }
            })
        }
    })
}


//delete button function
function deleteRow(clicked){
    const id = clicked.id;
    const ticker = tickerFromId(id, 1);
    const url = $(clicked).data('targ-url');
    const processedTicker = escapeSpecialChars(ticker)

    $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            data: JSON.stringify({
                ticker: ticker,
            }),
            success: function(result){
                console.log(result);
                row_id = '#' + processedTicker;
                //delete row here
                $(row_id).fadeOut('slow', function(){
                    $(this).remove();
                })
            },
            error: function(result){
                console.log(result);
            }
    });
}

//toggle notes btn function
function toggleNotes(clicked){
    const id = clicked.id;
    const ticker = tickerFromId(id, 1);
    const processedTicker = escapeSpecialChars(ticker)
    const notesId = processedTicker + '-notes';

    $("#" + notesId).toggle();
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


