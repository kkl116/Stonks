
import { formAjax, modifyErrorKeys } from './helpers.js';

/*
 *
 * login-register modal
 * Autor: Creative Tim
 * Web-autor: creative.tim
 * Web script: http://creative-tim.com
 * 
 */

function showRegisterForm(){
    let fadeSpeed = 400;
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
    let fadeSpeed = 400;
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
    let fadeSpeed = 400;
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
    let fadeSpeed = 400;
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

function registerAjax(url){
    function successFunc(success, fields, form){
        $('#loginModal').modal('hide');
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'register-' + key
            return key.replace('_', '-')
        })
        console.log(modErrors)
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    fields[key].input.classList.remove('is-invalid');
                    fields[key].error.innerHTML = null
                }
            }
        })
        shakeModal();
    }
    function keyFunc(key){
        key = key.replace('register-', '')
        return key.replace('-', '_')
    }

    let formId = 'register-form'
    let fieldIds = ['register-csrf', 'register-username', 'register-email',
                    'register-password', 'register-confirm-password']

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}

function loginAjax(url){
    function successFunc(success, fields, form){
        $('#loginModal').modal('hide');
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        // only print email_username error if exists else print -- 
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'login-' + key
            return key.replace('_', '-')
        })
        console.log(Object.keys(modErrors))
        console.log(fields)
        Object.keys(fields).forEach((key) => {
            if (Object.keys(modErrors).includes(key)){
                let key = 'login-password';
                fields[key].input.classList.add('is-invalid');
                fields['login-email-username'].input.classList.add('is-invalid')
                fields[key].error.innerHTML = modErrors[key][0];   
            }
        })
        shakeModal();
    }

    function keyFunc(key){
        key = key.replace('login-', '')
        return key.replace('-', '_')
    }

    let formId = 'login-form';
    let fieldIds = ['login-csrf', 'login-email-username', 'login-password',
                    'login-remember'];
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}

function requestResetAjax(url){
    function successFunc(success, fields){
        //disable modal and populate succses message
        console.log(success)
        showRequestResetSubmitted();
        //clear form fields
        fields.email_username.input.value = '';
    }
    function errorFunc(errors, fields){
        console.log(errors)
        // open request submitted modal regardless
        showRequestResetSubmitted();
        fields.email_username.input.value = '';
    }
    function keyFunc(key){
        key = key.replace('request-reset-', '');
        return key.replace('-', '_')
    }
    let formId = 'request-reset-form';
    let fieldIds = ['request-reset-csrf', 'request-reset-email'];

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}


function resetPasswordAjax(url){
    function successFunc(success, fields){
        //pass
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        //remove the errors from the previous submit 
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'reset-' + key
            return key.replace('_', '-')
        })
        console.log(modErrors);
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    fields[key].input.classList.remove('is-invalid');
                    fields[key].error.innerHTML = null
                }
            }
        })
    }

    function keyFunc(key){
        key = key.replace('reset-', '')
        return key.replace('-', '_')
    }
    let formId = 'reset-password-form'
    let fieldIds = ['reset-password-csrf', 'reset-password', 'reset-confirm-password']
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}


//create an account button to trigger modal 
$('#create-account-button').click(function() {
    openRegisterModal();
})

$('#please-login-button').click(function(){
    openLoginModal();
})

window.registerAjax=registerAjax;
window.loginAjax=loginAjax;
window.showLoginForm=showLoginForm;
window.requestResetAjax=requestResetAjax;
window.showRequestResetForm=showRequestResetForm;
window.resetPasswordAjax=resetPasswordAjax;
window.openLoginModal=openLoginModal;
window.openRegisterModal=openRegisterModal;
window.showRegisterForm=showRegisterForm;