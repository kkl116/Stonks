function addAjax(url){
    const form = document.getElementById('add-form');
    const fields = {
        csrf_token: {
            input: document.getElementById('add-csrf')
        },
        ticker_name: {
            input: document.getElementById('ticker-name'),
            error: document.getElementById('ticker-name-error')
        },
        quantity: {
            input: document.getElementById('quantity'),
            error: document.getElementById('quantity-error')
        },
        purchase_price: {
            input: document.getElementById('purchase-price'),
            error: document.getElementById('purchase-price-error')
        },

    };


    form.addEventListener('submit', async(e) => {
        e.preventDefault();
        console.log('url ' + url)
        console.log('ticker_name '+ fields.ticker_name.input)
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                csrf_token: fields.csrf_token.input.value,
                ticker_name: fields.ticker_name.input.value,
                quantity: fields.quantity.input.value,
                purchase_price: fields.purchase_price.input.value,
            })
        });

        if (response.ok){
            const success = await response.json();
            console.log(success)
            const emptyMessage = document.getElementById('empty-message');
            if (emptyMessage){
                emptyMessage.style.display="none";
            }
            //append item to table - 
            table.insertAdjacentHTML('afterbegin', success.newItem);
            //remove error messages and clear fields
            Object.keys(fields).forEach((key) => {
                fields[key].input.value= '';
                document.getElementById(key).classList.remove('is-invalid');
                document.getElementById(key+'-error').style.display="none";

            })
        } else {
            const errors = await response.json();
            console.log(errors)
            Object.keys(fields).forEach((key) => {
                if (key != 'csrf_token') {
                    if (Object.keys(errors).includes(key)) {
                        fields[key].input.classList.add('is-invalid');
                        fields[key].error.innerHTML = errors[key][0];
                    } else {
                        fields[key].input.classList.remove('is-invalid')
                        fields[key].error.innerHTML = null
                    }
                }
            })
        }
    })
}

/*
Ajax template: 
    form id
    field ids
    success func 
    error func 
*/