//just a separate js that runs for every page - 
import { error500Redirect} from './helpers.js';


$.ajaxSetup({
    /*use of ajax setup isn't recommended usually.. but just creating a simple redirect for all ajax calls 
    so that it redirects to an error page and doesn't simply stall.. can revisit this in the future
    */
    statusCode: {
        500: function(response){
            error500Redirect(JSON.parse(response.responseText))
        }
    }
});
