'use strict';

window.chartColors = {
    green: '#75c181',
    gray: '#a9b5c9',
    text: '#252930',
    border: '#e7e9ed'
};

/* Random number generator for demo purpose */
var randomDataPoint = function() { return Math.round(Math.random() * 100); };

// Bar Chart Configuration for the first chart
var barChartConfig1 = {
    type: 'bar',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Orders',
            backgroundColor: window.chartColors.green,
            data: [23, 45, 76, 75, 62, 37, 83]
        }]
    },
    options: {
        responsive: true,
        aspectRatio: 1.5,
        legend: {
            position: 'bottom',
            align: 'end',
        },
        title: {
            display: true,
            text: 'Bar Chart Example 2',
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        scales: {
            xAxes: [{
                display: true,
                gridLines: {
                    drawBorder: false,
                    color: window.chartColors.border,
                },
            }],
            yAxes: [{
                display: true,
                gridLines: {
                    drawBorder: false,
                    color: window.chartColors.border,
                },
            }]
        }
    }
};

// Bar Chart Configuration for the second chart
var barChartConfig2 = {
    type: 'bar',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Orders',
            backgroundColor: window.chartColors.green,
            data: [23, 45, 76, 75, 62, 37, 83]
        }]
    },
    options: {
        responsive: true,
        aspectRatio: 1.5,
        legend: {
            position: 'bottom',
            align: 'end',
        },
        title: {
            display: true,
            text: 'Bar Chart Example 2',
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        scales: {
            xAxes: [{
                display: true,
                gridLines: {
                    drawBorder: false,
                    color: window.chartColors.border,
                },
            }],
            yAxes: [{
                display: true,
                gridLines: {
                    drawBorder: false,
                    color: window.chartColors.border,
                },
            }]
        }
    }
};

// Generate charts on load
window.addEventListener('DOMContentLoaded', function() {
    var barChart1 = document.getElementById('canvas-barchart-1').getContext('2d'); 
    window.myBar1 = new Chart(barChart1, barChartConfig1); // Use the barChartConfig1

    var barChart2 = document.getElementById('canvas-barchart-2').getContext('2d'); 
    window.myBar2 = new Chart(barChart2, barChartConfig2); // Use the barChartConfig2
});
