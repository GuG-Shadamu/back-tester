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
            var ack_msg = { ack: 'Connected!' };
            socket.send(JSON.stringify(ack_msg));
            console.log('Sent ack:', ack_msg);

        };

        socket.onmessage = function (event) {
            var bars = JSON.parse(event.data);
            console.log('Received data:', bars); // debug
            var ack_msg = {ack: "received"};
            for (var i = 0; i < bars.length; i++) {
                var bar = bars[i];
                candleSeries.update({
                    time: bar.time,
                    open: bar.open,
                    high: bar.high,
                    low: bar.low,
                    close: bar.close,
                });
            }
            // Send acknowledgement back to the server
            
            socket.send(JSON.stringify(ack_msg));
            console.log('Sent ack:', ack_msg);
        };

        socket.onclose = function (event) {
            var elapsedTime = Date.now() - connectionStartTime;
            if (elapsedTime < maxReconnectionTime) {
                setTimeout(connect, 0.1); // try to reconnect after 0.1 second
            } else {
                console.log('Disconnected!');
            }
        };

        socket.onerror = function (event) {
            console.log('Error:', event);
        }

        // start the heartbeat mechanism
        setInterval(function() {
            if (socket.readyState === WebSocket.OPEN) {
                var ack_msg = { ack: 'Ping' };
                socket.send(JSON.stringify(ack_msg));
                // console.log('Sent ack:', ack_msg);
            }
        }, 100); // send a ping every 5 seconds
    }

    connect();
});
