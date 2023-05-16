/**
 * @Author: Tairan Gao
 * @Date:   2023-05-15 02:16:32
 * @Last Modified by:   Tairan Gao
 * @Last Modified time: 2023-05-15 21:40:20
 */


document.addEventListener('DOMContentLoaded', (event) => {
    var chart = LightweightCharts.createChart(document.getElementById('chart'), {
        width: 1200,
        height: 600,
        timeScale: {
                visible: true,
                timeVisible: true,
                secondsVisible: true
        }
    });

    var candleSeries = chart.addCandlestickSeries();
    var socket = io('http://localhost:4000');
    
    console.log('started!');
    socket.on('connect', function () {
        console.log('Connected!');
    });

    socket.on('data', function (bar) {
        console.log('Received data:', bar); 
        bar.time = new Date(bar.time).valueOf() / 1000;
        candleSeries.update({
            time: bar.time,
            open: bar.open,
            high: bar.high,
            low: bar.low,
            close: bar.close,
        });
    });
});
