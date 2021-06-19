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
            success: function(response){
                console.log('success')
                //insert notes tr
                let tickerRow = document.getElementById(ticker);
                tickerRow.insertAdjacentHTML('afterend', response.tr);

            },
            error: function(response){
                console.log('error')
                console.log(response)
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
        success: function(response){
            console.log(response);
        },
        error: function(response){
            console.log(response);
        }
    })

}

//use event delegation vs just assigning 
function addTagAjax(url){
    //get all tags-textarea elements
    const tableId = '#watchlist-table'
    $(tableId).on('keypress', 'textarea', function (e){
        if(e.which === 13 && !e.shiftKey) {
            if(e.target.id.includes('tags-text-area')){
                const element = e.target;
                e.preventDefault();
                if ($(element).val() != ''){
                    //get the tag text
                    const tag = $(element).val();
                    const ticker = $(element).attr('id').split('-')[0]
                    //ajax call to send to url 
                    $.ajax({
                        url: url,
                        type: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify(
                            {   ticker: ticker,
                                tag: tag
                            }
                        ),
                        success: function(response){
                            //insert span element from server next to textarea
                            $(element).val('')
                            console.log(response)
                            //
                            let tdId = ticker + '-tags'
                            $('#' + tdId).append(response.element)
                            
                        },
                        error: function(response){
                            //do something 
                            console.log(response)
                        }
                    })
                };
            };
        };
    });
}

function deleteTagAjax(clicked, url){
    const id = clicked.id
    const tagId = id.split('-')[1]
    console.log(tagId)


    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        data: JSON.stringify(
            {tagId : tagId}
        ),
        success: function(response){
            console.log(response);
            $('#tag-' + tagId).remove();
        },
        error: function(response){
            console.log(response)
        }
    })
};

//function to allow sector to be edited (onclick, then enter to submit)
function spanToTextArea(clicked, url){
    let textArea = $('<textarea></textarea>');
    const spanText = $(clicked).html();
    const ticker = clicked.id.split('-')[0];
    const spanId = '#' + clicked.id;
    $(textArea).html(spanText);
    $(textArea).attr('id', ticker+'-sector-textArea')
    $(textArea).data('url', url)
    $(textArea).addClass('form-control');
    $(textArea).css({
        'font-size': '11px',
        'height': '2.5em',
    });
    //replace span element with this 
    $(spanId).replaceWith(textArea);
}

function editSectorAjax(url){
    //get all tags-textarea elements
    const tableId = '#watchlist-table'
    $(tableId).on('keypress', 'textarea', function (e){
        if(e.which === 13 && !e.shiftKey) {
            if(e.target.id.includes('sector-textArea')){
                const element = e.target;
                e.preventDefault();
                if ($(element).val() != ''){
                    //get the tag text
                    const sector = $(element).val();
                    const ticker = $(element).attr('id').split('-')[0]
                    //ajax call to send to url 
                    $.ajax({
                        url: url,
                        type: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        data: JSON.stringify(
                            {   ticker: ticker,
                                sector: sector
                            }
                        ),
                        success: function(response){
                            //insert span element from server next to textarea
                            let newSpan = response.newSpan;
                            $('#' + element.id).replaceWith(newSpan)
                        },
                        error: function(response){
                            //do something 
                            console.log(response)
                        }
                    })
                };
            };
        };
    });
}

window.addAjax=addAjax;
window.deleteRow=deleteRow;
window.toggleNotes=toggleNotes;
window.saveNotes=saveNotes;
window.addTagAjax=addTagAjax;
window.deleteTagAjax=deleteTagAjax;
window.spanToTextArea=spanToTextArea;
window.editSectorAjax=editSectorAjax;


