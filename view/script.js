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
            socket.send(JSON.stringify({type: "connection_ack"}));
            console.log('Connected!');
        };

        socket.onmessage = function (event) {
            var message = JSON.parse(event.data);

            if (message.type === "heartbeat") {
                socket.send(JSON.stringify({type: "heartbeat_ack"}));
                console.log('HeartBeap!');
            } else if (message.type === "bar") {
                var bar = JSON.parse(event.data);
                // console.log('Received data:', bar); // debug
                candleSeries.update({
                    time: bar.time,
                    open: bar.open,
                    high: bar.high,
                    low: bar.low,
                    close: bar.close,
                });
                // Send acknowledgement back to the server
                socket.send(JSON.stringify({type: "bar_ack"}));
            }
        };

        socket.onclose = function (event) {
            if (event.code !== 1000) {  // 1000 is the status code for a normal closure
                var elapsedTime = Date.now() - connectionStartTime;
                if (elapsedTime < maxReconnectionTime) {
                    setTimeout(connect, 100); // try to reconnect after 0.1 second
                }
            } else {
                console.log('Disconnected! Code:', event.code, 'Reason:', event.reason);
            }
        };

        socket.onerror = function (event) {
            console.log('Error:', event);
        }


        
    }

    connect();
});
