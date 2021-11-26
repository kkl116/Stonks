function escapeSpecialChars(id){
    //escape special chars in ticker name so that jquery can still find it in the DOM
    const special = '!@#$^&%*()+=-[]{}|:<>?,.';
    let newString = '';
    for (var i = 0; i < id.length; i++){
        if (special.includes(id[i])){
            newString = newString + '\\' + id[i]
        } else {
            newString = newString + id[i]
        }
    }
    return newString;
}

function tickerFromId(id, pop_n){
    //pop_n is how many elements to ignore at the end
    let split = id.split('-');
    let i = 0;
    if (split.length == 2){
        return split[0]
    } else if (split.length > 2){
        for (i; i<pop_n; i++){
            split.pop();
        }
        return split.join('-')
    }
}

function formAjax(url=null, formId=null, fieldIds=[], successFunc=null, errorFunc=null,
    keyFunc=null, waitFunc=null, dataFunc=null){
    /*
    formAjax template: 
        url
        form id
        field ids (array)
        success func - takes response json and does something
        error func - takes response json and does something
        key func - processes key values of fields object to match wtforms field names
        waitFunc - do something before response comes back
    */
   function dataFromFields(fields){
       let data = {};
       
       Object.keys(fields).forEach((key) => {
           console.log(key)
           let value = keyFunc(key);
           data[value] = fields[key].input.value
       })
       console.log(data)
       return data
   }

   if (dataFunc == null){
        dataFunc=dataFromFields;
   }

    const form = document.getElementById(formId);
    const fields = {};
    fieldIds.forEach((id) => {
        if (id.includes('csrf')) {
            fields['csrf_token'] = {input: document.getElementById(id)}
        } else {
            fields[id] = {input: document.getElementById(id),
                        error: document.getElementById(id + '-error')
                    }
        }
    });

    form.addEventListener('submit', async(e) => {
        e.preventDefault();
        if (waitFunc) {
            waitFunc()
        }
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                dataFunc(fields)
            )
        })

        if (response.ok){
            const success = await response.json();
            successFunc(success, fields, form)
        } else {
            const errors = await response.json();
            errorFunc(errors, fields)
        }
    })
}

function modifyErrorKeys(errors, modFunc){
    let errorKeys = Object.keys(errors);
    let modErrors = {};
    errorKeys.forEach((key) => {
        let modKey = modFunc(key)
        modErrors[modKey] = errors[key]
    })
    return modErrors
}

//delete button function
function deleteRow(clicked, successFunc=null, errorFunc=null, waitFunc=null, 
                dataFunc=null){
    /*successfunc and errorfunc gives the option to do additional things after
    delete success and failure - */
    const id = clicked.id;
    const ticker = tickerFromId(id, 1);
    const url = $(clicked).data('targ-url');
    const processedTicker = escapeSpecialChars(ticker);

    if (waitFunc) {
        waitFunc()
    };

    function defaultDataFunc(ticker){
        return {ticker: ticker}
    };

    if (dataFunc == null) {
        dataFunc = defaultDataFunc;
    };

    console.log(dataFunc)

    $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            data: JSON.stringify(
                dataFunc(ticker)
            ),
            success: function(response){
                console.log(response);
                let row_id = '#' + processedTicker;
                //delete row here
                $(row_id).fadeOut('slow', function(){
                    $(this).remove();
                });
                if (successFunc){
                    successFunc(response);
                }
            },
            error: function(response){
                console.log(response);

                if (errorFunc){
                    errorFunc(response);
                }
            }
    });
}

function error500Redirect(response){
    const url = response.url_500;
    if (url){
        window.location.href = url;
    } else {
        console.log('500 Error but no URL provided')
    };
}

export {escapeSpecialChars, tickerFromId, formAjax,
        modifyErrorKeys, deleteRow, error500Redirect}