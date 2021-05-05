//ajax for dropdown to add additional charts if wanted
function addChart(clicked){
    const item = $(clicked).data('item-name');
    const url = $(clicked).data('targ-url');
    const ticker = $(clicked).data('ticker');
    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            addItem: item,
            ticker: ticker
        }),
        success: function(chartJSON){
            const chartId = item + '_chart'
            if (typeof(chartJSON) == 'string'){
                chartJSON = JSON.parse(chartJSON);
            }
            console.log('typeof chartJSON' + ' ' + typeof(chartJSON))

            //add new chart to new chart div, then recreate new chart div to prep
            //check that chart doesn't already exist
            if ($('#'+ chartId).length == 0){
                config = {response: true,
                displayModeBar: true,
                displayLogo: false};
                Plotly.setPlotConfig(config)
                //change id of newChart into item
                $('#newChart').attr('id', chartId);
                Plotly.plot(chartId, chartJSON);
                //add newChart div back in 
                $('<div><div id="newChart"></div></div>').insertAfter("#"+chartId)
            }

        },
        error: function(errorMsg){
            console.log(errorMsg)
        }
    })
}