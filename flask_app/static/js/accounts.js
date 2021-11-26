
import { formAjax, modifyErrorKeys } from './helpers.js';

//ajax code references this: https://blog.carsonevans.ca/2019/08/20/validating-ajax-requests-with-wtforms-in-flask/

function registerAjax(url){
    function successFunc(success, fields, form){
        $('#registerModal').modal('hide');
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        $('#registerModalBody').show();
        $('#registerModalLoading').hide();

        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'register-' + key
            return key.replace('_', '-')
        })
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.remove('is-valid')
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    fields[key].input.classList.add('is-valid')
                    fields[key].input.classList.remove('is-invalid');
                    fields[key].error.innerHTML = null
                }
            }
        })
    }
    function keyFunc(key){
        key = key.replace('register-', '')
        return key.replace('-', '_')
    };

    function waitFunc(){
    $('#registerModalBody').hide();
    $('#registerModalLoading').attr('style', "display: inline !important");
    };

    let formId = 'register-form'
    let fieldIds = ['register-csrf', 'register-username', 'register-email',
                    'register-password', 'register-confirm-password']

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc, waitFunc=waitFunc);
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
        Object.keys(fields).forEach((key) => {
            if (Object.keys(modErrors).includes(key)){
                let key = 'login-password';
                fields[key].input.classList.add('is-invalid');
                fields['login-email-username'].input.classList.add('is-invalid')
                fields[key].error.innerHTML = modErrors[key][0];   
            }
        })
    }

    function keyFunc(key){
        key = key.replace('login-', '')
        return key.replace('-', '_')
    }

    let formId = 'login-form';
    let fieldIds = ['login-csrf', 'login-email-username', 'login-password'];
    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}

function requestResetAjax(url){
    function successFunc(success, fields){
        //disable modal and populate succses message
        $('#passwordResetBody').toggle()
        $('#resetModalLoading').toggle()

        $('#passwordResetModal').modal('toggle');
        $('#requestSubmittedModal').modal('toggle');
        //clear form fields
        $('#request-reset-email').val('');
    }
    function errorFunc(errors, fields){
        $('#passwordResetBody').toggle();
        $('#resetModalLoading').toggle();

        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'request-reset-' + key
            return key.split('_').join('-')
        })
        Object.keys(fields).forEach((key) => {
            if (Object.keys(modErrors).includes(key)){
                fields[key].input.classList.add('is-invalid');
                fields['request-reset-email'].input.classList.add('is-invalid')
                fields[key].error.innerHTML = modErrors[key][0];   
            }
        })
    }
    function keyFunc(key){
        key = key.replace('request-reset-', '');
        return key.replace('-', '_')
    }

    function waitFunc(){
        $('#passwordResetBody').hide();
        $('#resetModalLoading').attr('style', "display: inline !important");
    };
    
    let formId = 'request-reset-form';
    let fieldIds = ['request-reset-csrf', 'request-reset-email'];

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc, waitFunc=waitFunc);
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
        Object.keys(fields).forEach((key) => {
            if (key != 'csrf_token') {
                if (Object.keys(modErrors).includes(key)) {
                    fields[key].input.classList.remove('is-valid')
                    fields[key].input.classList.add('is-invalid');
                    fields[key].error.innerHTML = modErrors[key][0];
                } else {
                    fields[key].input.classList.add('is-valid')
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

window.registerAjax=registerAjax;
window.loginAjax=loginAjax;
window.requestResetAjax=requestResetAjax;
window.resetPasswordAjax=resetPasswordAjax;
