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
    if (split.length == 2){
        return split[0]
    } else if (split.length > 2){
        for (i=0; i<pop_n; i++){
            split.pop();
        }
        return split.join('-')
    }
}

function formAjaxTemplate()

export {escapeSpecialChars, tickerFromId}