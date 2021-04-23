//use prepend method to add a td element to the table (append/prepend is inside - before and after is well before and after)
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
            //pass
            //append item to table - 
            const emptyMessage = document.getElementById('empty-message')
            const table = document.getElementById('watchlist-table')
            if (emptyMessage){
                emptyMessage.style.display="none"
            }
            console.log(success)
            table.insertAdjacentHTML('afterbegin', success.newItem)
            
            //remove error message and clear search bar
            fields['ticker_name'].input.value = ''
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