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
    var socket;
    var maxReconnectionTime = 20000; // 10 seconds
    var connectionStartTime = Date.now();

    function connect() {
        socket = new WebSocket('ws://localhost:5000/ws');

        socket.onopen = function (event) {
            console.log('Connected!');
        };

        socket.onmessage = function (event) {
            var bar = JSON.parse(event.data);

            console.log('Received data:', bar);
            bar.time = new Date(bar.time).valueOf() / 1000;
            console.log('now', Date.now());
            candleSeries.update({
                time: bar.time,
                open: bar.open,
                high: bar.high,
                low: bar.low,
                close: bar.close,
            });
        };

        socket.onclose = function (event) {
            var elapsedTime = Date.now() - connectionStartTime;
            if (elapsedTime < maxReconnectionTime) {
                console.log('Trying to reconnect...');
                setTimeout(connect, 100); // try to reconnect after 0.1 second
            } else {
                console.log('Disconnected!');
            }
        };

        socket.onerror = function (event) {
            console.log('Error:', event);
        }
    }

    connect();
});
