
    $(document).ready(function() {
        var myChartData; // 用於存儲 chartBig1 圖表實例
        var myChartHistoricalData; // 用於存儲 chartLineData 圖表實例
        var myChartReceiveTotal; // 用於存儲 RecevieTotal 圖表實例
    
        function fetchSensors() {
            $.ajax({
                url: "{% url 'get_sensors' %}",
                method: "GET",
                success: function(sensors) {
                    const sensorButtons = $("#sensor-buttons");
                    sensorButtons.empty();
                    sensors.slice(0, 10).forEach((sensor, index) => {
                        const activeClass = index === 0 ? 'active' : '';
                        sensorButtons.append(`
                            <label class="btn btn-sm btn-primary btn-simple ${activeClass}" id="btn-${sensor.name}">
                                <input type="radio" name="options" ${index === 0 ? 'checked' : ''}>
                                <span class="d-none d-sm-block d-md-block d-lg-block d-xl-block">${sensor.name}</span>
                                <span class="d-block d-sm-none">
                                    <i class="tim-icons icon-single-02"></i>
                                </span>
                            </label>
                        `);
                    });
                    if (sensors.length > 0) {
                        const firstSensorName = sensors[0].name;
                        fetchSensorData(firstSensorName);
                        sensors.forEach(sensor => {
                            $(`#btn-${sensor.name}`).off('click').on('click', function() {
                                fetchSensorData(sensor.name);
                            });
                        });
                    }
                },
                error: function(error) {
                    console.error("Error fetching sensors", error);
                }
            });
        }
    
        function fetchSensorData(sensorName) {
            $.ajax({
                url: `/get_sensor_data/${sensorName}/`,
                method: "GET",
                success: function(responseData) {
                    const data = responseData.current_data;
                    const historicalData = responseData.historical_data;
    
                    // 修改 card-title 成感測器名稱
                    $(".sensor-data-title").text(sensorName);
    
                    const labels = data.map(item => new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
                    const chartData = data.map(item => item.data);
    
                    var ctx = document.getElementById("chartBig1").getContext('2d');
    
                    // 清空之前的圖表
                    if (myChartData) {
                        myChartData.destroy();
                    }
    
                    var gradientStroke = ctx.createLinearGradient(0, 230, 0, 50);
                    gradientStroke.addColorStop(1, 'rgba(72,72,176,0.1)');
                    gradientStroke.addColorStop(0.4, 'rgba(72,72,176,0.0)');
                    gradientStroke.addColorStop(0, 'rgba(119,52,169,0)');
    
                    var config = {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: "接收數據",
                                fill: true,
                                backgroundColor: gradientStroke,
                                borderColor: '#d346b1',
                                borderWidth: 2,
                                borderDash: [],
                                borderDashOffset: 0.0,
                                pointBackgroundColor: '#d346b1',
                                pointBorderColor: 'rgba(255,255,255,0)',
                                pointHoverBackgroundColor: '#d346b1',
                                pointBorderWidth: 20,
                                pointHoverRadius: 4,
                                pointHoverBorderWidth: 15,
                                pointRadius: 4,
                                data: chartData,
                            }]
                        },
                        options: {
                            maintainAspectRatio: false,
                            legend: {
                                display: false
                            },
                            tooltips: {
                                backgroundColor: '#f5f5f5',
                                titleFontColor: '#333',
                                bodyFontColor: '#666',
                                bodySpacing: 4,
                                xPadding: 12,
                                mode: "nearest",
                                intersect: 0,
                                position: "nearest"
                            },
                            responsive: true,
                            scales: {
                                yAxes: [{
                                    barPercentage: 1.6,
                                    gridLines: {
                                        drawBorder: false,
                                        color: 'rgba(29,140,248,0.0)',
                                        zeroLineColor: "transparent",
                                    },
                                    ticks: {
                                        suggestedMin: 60,
                                        suggestedMax: 125,
                                        padding: 20,
                                        fontColor: "#9a9a9a"
                                    }
                                }],
                                xAxes: [{
                                    barPercentage: 1.6,
                                    gridLines: {
                                        drawBorder: false,
                                        color: 'rgba(225,78,202,0.1)',
                                        zeroLineColor: "transparent",
                                    },
                                    ticks: {
                                        padding: 20,
                                        fontColor: "#9a9a9a"
                                    }
                                }]
                            }
                        }
                    };
    
                    myChartData = new Chart(ctx, config); // 存儲新創建的圖表實例
    
                    // 更新歷史數據圖表
                    updateHistoricalChart(historicalData);
    
                    // 更新接收數據量圖表
                    updateReceiveTotalChart(historicalData);
    
                    // 更新本日最高和最低數據
                    if (chartData.length > 0) {
                        const todayMax = Math.max(...chartData);
                        const todayMin = Math.min(...chartData);
                        $('#today-max').text(todayMax);
                        $('#today-min').text(todayMin);
                    } else {
                        $('#today-max').text('N/A');
                        $('#today-min').text('N/A');
                    }
    
                    // 更新本日接收數據量
                    $('#today-receive-total').text(data.length);
                },
                error: function(error) {
                    console.error("Error fetching sensor data", error);
                }
            });
        }
    
        function updateHistoricalChart(historicalData) {
            const labels = historicalData.map(item => item.date);
            const maxData = historicalData.map(item => item.max);
            const minData = historicalData.map(item => item.min);
    
            var ctx = document.getElementById("chartLineData").getContext('2d');
    
            // 清空之前的圖表
            if (myChartHistoricalData) {
                myChartHistoricalData.destroy();
            }
    
            var config = {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "最高數據",
                            fill: false,
                            borderColor: 'red',
                            borderWidth: 2,
                            data: maxData,
                        },
                        {
                            label: "最低數據",
                            fill: false,
                            borderColor: 'Aqua',
                            borderWidth: 2,
                            data: minData,
                        }
                    ]
                },
                options: {
                    maintainAspectRatio: false,
                    legend: {
                        display: true
                    },
                    tooltips: {
                        backgroundColor: '#f5f5f5',
                        titleFontColor: '#333',
                        bodyFontColor: '#666',
                        bodySpacing: 4,
                        xPadding: 12,
                        mode: "nearest",
                        intersect: 0,
                        position: "nearest"
                    },
                    responsive: true,
                    scales: {
                        yAxes: [{
                            barPercentage: 1.6,
                            gridLines: {
                                drawBorder: false,
                                color: 'rgba(29,140,248,0.0)',
                                zeroLineColor: "transparent",
                            },
                            ticks: {
                                suggestedMin: 60,
                                suggestedMax: 125,
                                padding: 20,
                                fontColor: "#9a9a9a"
                            }
                        }],
                        xAxes: [{
                            barPercentage: 1.6,
                            gridLines: {
                                drawBorder: false,
                                color: 'rgba(225,78,202,0.1)',
                                zeroLineColor: "transparent",
                            },
                            ticks: {
                                padding: 20,
                                fontColor: "#9a9a9a"
                            }
                        }]
                    }
                }
            };
    
            myChartHistoricalData = new Chart(ctx, config); // 存儲新創建的圖表實例
        }
    
        function updateReceiveTotalChart(historicalData) {
            const labels = historicalData.map(item => item.date);
            const receiveTotalData = historicalData.map(item => item.count); // 假設數據中包含 count 屬性
    
            var ctx = document.getElementById("RecevieTotal").getContext('2d');
    
            // 清空之前的圖表
            if (myChartReceiveTotal) {
                myChartReceiveTotal.destroy();
            }
    
            var config = {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: "接收數據量",
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        data: receiveTotalData,
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    legend: {
                        display: false
                    },
                    tooltips: {
                        backgroundColor: '#f5f5f5',
                        titleFontColor: '#333',
                        bodyFontColor: '#666',
                        bodySpacing: 4,
                        xPadding: 12,
                        mode: "nearest",
                        intersect: 0,
                        position: "nearest"
                    },
                    responsive: true,
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                padding: 20,
                                fontColor: "#9a9a9a"
                            },
                            gridLines: {
                                drawBorder: false,
                                color: 'rgba(29,140,248,0.1)',
                                zeroLineColor: "transparent",
                            }
                        }],
                        xAxes: [{
                            barPercentage: 0.5,
                            gridLines: {
                                drawBorder: false,
                                color: 'rgba(225,78,202,0.1)',
                                zeroLineColor: "transparent",
                            },
                            ticks: {
                                padding: 20,
                                fontColor: "#9a9a9a"
                            }
                        }]
                    }
                }
            };
    
            myChartReceiveTotal = new Chart(ctx, config); // 存儲新創建的圖表實例
        }
    
        fetchSensors();
    });
    
    
    
    $(document).ready(function () {
        // Javascript method's body can be found in assets/js/demos.js
        demo.initDashboardPageCharts();

    });