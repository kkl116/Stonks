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
    fadeSpeed = 400;
    $('.loginBox').fadeOut(fadeSpeed,function(){
        $('.social').fadeIn(fadeSpeed);
        $('.division').fadeIn(fadeSpeed);
        $('.registerBox').fadeIn(fadeSpeed);
        $('.login-footer').fadeOut(fadeSpeed,function(){
            $('.register-footer').fadeIn(fadeSpeed);
        });
    }); 
    $('.error').removeClass('alert alert-danger').html('');
       
}
function showLoginForm(){
    fadeSpeed = 400;
    $('#loginModal .registerBox').fadeOut(fadeSpeed,function(){
        $('.resetSubmittedBox').fadeOut(fadeSpeed);
        $('.requestResetBox').fadeOut(fadeSpeed);
        $('.social').fadeIn(fadeSpeed);
        $('.division').fadeIn(fadeSpeed);
        $('.loginBox').fadeIn(fadeSpeed);
        $('.register-footer').fadeOut(fadeSpeed,function(){
            $('.login-footer').fadeIn(fadeSpeed);    
            $('.request-submitted-footer').fadeOut(fadeSpeed);
            $('.request-reset-footer').fadeOut(fadeSpeed);
        });
    });       
     $('.error').removeClass('alert alert-danger').html(''); 
}

function showRequestResetForm(){
        fadeSpeed = 400;
    $('.loginBox').fadeOut(fadeSpeed, function(){
        $('.social').fadeOut(fadeSpeed);
        $('.division').fadeOut(fadeSpeed);
        $('.loginBox').fadeOut(fadeSpeed);

        $('.requestResetBox').fadeIn(fadeSpeed);

        $('.login-footer').fadeOut(fadeSpeed, function(){
            $('.request-reset-footer').fadeIn(fadeSpeed);
    })
    });
    $('.error').removeClass('alert alert-danger').html('');
}

function showRequestResetSubmitted(){
    fadeSpeed = 400;
    $('.requestResetBox').fadeOut(fadeSpeed, function(){
        $('.resetSubmittedBox').fadeIn(fadeSpeed);
    })
    $('.request-reset-footer').fadeOut(fadeSpeed, function(){
        $('.request-submitted-footer').fadeIn(fadeSpeed);
    })
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

//js code from here: https://blog.carsonevans.ca/2019/08/20/validating-ajax-requests-with-wtforms-in-flask/

function registerAjax(url) {
    const form = document.getElementById('register-form');
    //put a const here to reference to a success flash message - called after modal closed
    const fields = {
        csrf_token: {
            input: document.getElementById('register-csrf'),
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
            let success = await response.json();
            if (success.redirect) {
                window.location.href = success.redirect;
            }
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
        },
        email_username: {
            input: document.getElementById('login-email-username'),
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
            let success = await response.json();
            if (success.redirect) {
                window.location.href = success.redirect;
            }
            //refresh page 
            //clear form fields
        } else {
            // only print email_username error if exists else print -- 
            let errors = await response.json();
            if (Object.keys(errors).includes('password')){
                let key = 'password';
                fields[key].input.classList.add('is-invalid');
                fields['email_username'].input.classList.add('is-invalid')
                fields[key].error.innerHTML = errors[key][0];   
            }
            shakeModal();
        }
    })
}

function requestResetAjax(url){
    const form = document.getElementById('request-reset-form');
    //put a const here to reference to a success flash message - called after modal closed
    const fields = {
        csrf_token: {
            input: document.getElementById('request-reset-csrf'),
        },
        email_username: {
            input: document.getElementById('request-reset-email-username'),
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
            })
        });
        if (response.ok) {
            //disable modal and populate succses message
            showRequestResetSubmitted();
            //clear form fields
            fields.email_username.input.value = ''
        } else {
            // open request submitted modal regardless
            showRequestResetSubmitted();
            fields.email_username.input.value = ''
        }
    })
}

function resetPasswordAjax(url){
    const form = document.getElementById('reset-password-form');
    //put a const here to reference to a success flash message - called after modal closed
    const fields = {
        csrf_token: {
            input: document.getElementById('reset-password-csrf'),
        },
        password: {
            input: document.getElementById('reset-password'),
            error: document.getElementById('reset-password-error')
        },
        
        confirm_password: {
            input: document.getElementById('reset-confirm-password'),
            error: document.getElementById('reset-confirm-password-error')
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
                password: fields.password.input.value, 
                confirm_password: fields.confirm_password.input.value
            })
        });
        if (response.ok) {
            //pass
            let success = await response.json();
            if (success.redirect) {
                window.location.href = success.redirect;
            }
        } else {
            //remove the errors from the previous submit 
            let errors = await response.json();
            console.log(errors);
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
        }
    })
}

//create an account button to trigger modal 
$('#create-account-button').click(function() {
    openRegisterModal();
})

$('#please-login-button').click(function(){
    openLoginModal();
})
