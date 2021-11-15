import { formAjax, modifyErrorKeys } from './helpers.js';

function changePasswordAjax(url){
    function successFunc(success, fields, form){
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'change-' + key
            return key.replace('_', '-')
        })

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
        key = key.replace('change-', '');
        return key.replace('-', '_')
    }

    let formId = 'change-password-form'
    let fieldIds = ['change-password-csrf', 'change-old-password', 'change-new-password',
                    'change-confirm-password']

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}


function changeUsernameAjax(url){
    function successFunc(success, fields, form){
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'change-' + key
            return key.replace('_', '-')
        })

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
        key = key.replace('change-', '');
        return key.replace('-', '_')
    }

    let formId = 'change-username-form'
    let fieldIds = ['change-username-csrf', 'change-username', 'change-confirm-username']

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}

function changeEmailAjax(url){
    function successFunc(success, fields, form){
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'change-' + key
            return key.replace('_', '-')
        })

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
        key = key.replace('change-', '');
        return key.replace('-', '_')
    }

    let formId = 'change-email-form'
    let fieldIds = ['change-email-csrf', 'change-email', 'change-confirm-email']

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}

function changeSettingsAjax(url){
    function successFunc(success, fields, form){
        form.reset();
        if (success.redirect) {
            window.location.href = success.redirect;
        }
    }
    function errorFunc(errors, fields){
        let modErrors = modifyErrorKeys(errors, function(key){
            key = 'change-' + key
            return key.replace('_', '-')
        })

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
        key = key.replace('change-', '');
        return key.replace('-', '_')
    }

    let formId = 'change-settings-form'
    let fieldIds = ['change-settings-csrf', 'change-currency']

    formAjax(url=url, formId=formId,
        fieldIds=fieldIds, successFunc=successFunc, errorFunc=errorFunc,
        keyFunc=keyFunc);
}

window.changePasswordAjax=changePasswordAjax;
window.changeUsernameAjax=changeUsernameAjax;
window.changeEmailAjax=changeEmailAjax;
window.changeSettingsAjax=changeSettingsAjax;

