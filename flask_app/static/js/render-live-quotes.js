// takes in quote data 
function renderLiveQuote(quote_route, prev_close, q){
    $(document).ready(function (){
        //get previous close data from json 
        prev_close = +prev_close
        //create chart
        const chart = Highcharts.stockChart('liveQuote', {
            series: [{
                name: q,
                data: []
            }],
            rangeSelector: {
                selected: 1,
                inputEnabled: false
            },
            yAxis: {
                title: {
                    text: 'Price'
                },
                plotLines:[{
                    value: prev_close,
                    color: 'green',
                    dashStyle: 'shortdash',
                    width: 2,
                    label: {
                        text: 'Previous Close'
                    }
                }]
            }
        })

        var source = new EventSource(quote_route)
        source.onmessage = function(event){
            var data = JSON.parse(event.data);
            x = (new Date()).getTime();
            y = data.value;
            chart.series[0].addPoint([x,y]);
        }
    })
}
