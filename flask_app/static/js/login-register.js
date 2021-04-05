//const express = require("express");

/*
 *
 * login-register modal
 * Autor: Creative Tim
 * Web-autor: creative.tim
 * Web script: http://creative-tim.com
 * 
 */
function showRegisterForm(){
    $('.loginBox').fadeOut('fast',function(){
        $('.registerBox').fadeIn('fast');
        $('.login-footer').fadeOut('fast',function(){
            $('.register-footer').fadeIn('fast');
        });
        $('.modal-title').html('Register with');
    }); 
    $('.error').removeClass('alert alert-danger').html('');
       
}
function showLoginForm(){
    $('#loginModal .registerBox').fadeOut('fast',function(){
        $('.loginBox').fadeIn('fast');
        $('.register-footer').fadeOut('fast',function(){
            $('.login-footer').fadeIn('fast');    
        });
        
        $('.modal-title').html('Login with');
    });       
     $('.error').removeClass('alert alert-danger').html(''); 
}

function openLoginModal(){
    showLoginForm();
    setTimeout(function(){
        $('#loginModal').modal('show');    
    }, 230);
    
}
function openRegisterModal(){
    showRegisterForm();
    setTimeout(function(){
        $('#loginModal').modal('show');    
    }, 230);
    
}

function removeShake(){
    $('#loginModal .modal-dialog').removeClass('shake');
}

function shakeModal(){
    $('#loginModal .modal-dialog').addClass('shake');
    setTimeout(removeShake, 1000); 
}

//use in form error check 
function add(accumulator, a) {
    return accumulator + a;
}

function checkErrorString(errors) {
    let i;
    for (i = 0; i < errors.length; i++) {
        errors[i] = errors[i] != '()' && errors[i] != '[]'
    }
    return errors
}

//js code from here: https://blog.carsonevans.ca/2019/08/20/validating-ajax-requests-with-wtforms-in-flask/

function registerAjax(url) {
    const form = document.getElementById('register-form');
    //put a const here to reference to a success flash message - called after modal closed
    const fields = {
        csrf_token: {
            input: document.getElementById('register-csrf'),
            error: document.getElementById('register-csrf-error')
        },
        username: {
            input: document.getElementById('register-username'),
            error: document.getElementById('register-username-error')
        },
        email: {
            input: document.getElementById('register-email'),
            error: document.getElementById('register-email-error')
        },
        
        password: {
            input: document.getElementById('register-password'),
            error: document.getElementById('register-password-error')
        },
        
        confirm_password: {
            input: document.getElementById('register-confirm-password'),
            error: document.getElementById('register-confirm-password-error')
        }
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
                username: fields.username.input.value,
                email: fields.email.input.value,
                password: fields.password.input.value, 
                confirm_password: fields.confirm_password.input.value
            })
        });

        console.log(response)

        if (response.ok) {
            //disable modal and populate succses message
            $('#loginModal').modal('hide');
            form.reset();
            document.getElementById('login-register-success').classList.add("alert", 'alert-success');
            document.getElementById('login-register-success').innerHTML = 'Your account has been created!';
            //clear form fields
        } else {
            //remove the errors from the previous submit 
            let errors = await response.json();

            Object.keys(fields).forEach((key) => {
                if (key != 'csrf_token') {
                    if (Object.keys(errors).includes(key)) {
                        fields[key].input.classList.add('is-invalid');
                        fields[key].error.innerHTML = errors[key][0];
                    } else {
                        fields[key].input.classList.remove('is-invalid');
                        fields[key].error.innerHTML = null
                    }
                }
            })
            shakeModal();
        }
    })
}

function loginAjax(url){
    const form = document.getElementById('login-form');
    //put a const here to reference to a success flash message - called after modal closed
    const fields = {
        csrf_token: {
            input: document.getElementById('login-csrf'),
            error: document.getElementById('login-csrf-error')
        },
        email_username: {
            input: document.getElementById('login-email-username'),
            error: document.getElementById('login-email-username-error')
        },
        password: {
            input: document.getElementById('login-password'),
            error: document.getElementById('login-password-error')
        },
        remember: {
            input: document.getElementById('login-remember')
        }
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
                email_username: fields.email_username.input.value,
                password: fields.password.input.value,
                remember: fields.remember.input.value
            })
        });
        if (response.ok) {
            //disable modal and populate succses message
            $('#loginModal').modal('hide');
            form.reset();
            document.getElementById('login-register-success').classList.add("alert", 'alert-success');
            document.getElementById('login-register-success').innerHTML = 'You are logged in!';
            //clear form fields
        } else {
            // only print email_username error if exists else print -- 
            let errors = await response.json();
            if (Object.keys(errors).includes('email_username')){
                let key = 'email_username';
                fields[key].input.classList.add('is-invalid');
                fields[key].error.innerHTML = errors[key][0];
                fields['password'].error.innerHTML = null;
                fields['password'].input.classList.remove('is-invalid');
            } else {
                let key = 'password';
                fields[key].input.classList.add('is-invalid');
                fields[key].error.innerHTML = errors[key][0];   
                fields['email_username'].error.innerHTML = null;
                fields['email_username'].input.classList.remove('is-invalid')

            }
            shakeModal();
        }
    })
}

//create an account button to trigger modal 
$('#create-account-button').click(function() {
    openRegisterModal();
})
