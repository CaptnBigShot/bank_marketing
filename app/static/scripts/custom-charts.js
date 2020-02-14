function createStackedBarChartForPersonalLoanOffers(elementId, data) {
    let ctx = document.getElementById(elementId).getContext('2d');

    let acceptedData = [data['accepted_predicted_to_accept'], data['accepted_predicted_to_decline']];
    let declinedData = [data['declined_predicted_to_accept'], data['declined_predicted_to_decline']];
    let noResponseData = [data['no_response_predicted_to_accept'], data['no_response_predicted_to_decline']];

    let barChartData = {
        labels: ['Predicted to Accept', 'Predicted to Decline'],
        datasets: [{
            label: 'Accepted',
            backgroundColor: 'rgba(78,192,148,0.4)',
            data: acceptedData
        }, {
            label: 'Declined',
            backgroundColor: 'rgba(255, 99, 132, 0.4)',
            data: declinedData
        }, {
            label: 'No Response',
            backgroundColor: 'rgba(36,97,168,0.4)',
            data: noResponseData
        }]
    };

    return new Chart(ctx, {
        type: 'horizontalBar',
        data: barChartData,
        options: {
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true
                }]
            },
            title: {
                display: true,
                text: 'Customer Personal Loan Offer Predictions Segmented By Their Actual Responses'
            }
        }
    });
}

function createPieChartForPersonalLoanOffers(elementId, data) {
    let accuracyPieData = data;
    let accurateCount = accuracyPieData[0];
    let inaccurateCount = accuracyPieData[1];
    let accuracyPct = ((accurateCount / (accurateCount + inaccurateCount)) * 100).toFixed(2);

    return new Chart(document.getElementById(elementId), {
        "type":"doughnut",
        "data": {
            "labels": ["Accurate", "Inaccurate"],
            "datasets": [{
                "data": accuracyPieData,
                "backgroundColor":[
                    "rgba(78,192,148,0.4)",
                    "rgba(255, 99, 132, 0.4)",
                ]
            }]
        },
        options: {
            title: {
                display: true,
                text: accuracyPct + '% Prediction Accuracy for Responded Personal Loan Offers'
            }
        }
    });
}

function createLineChartForPersonalLoanOffers(elementId, chartInfo) {
        let labels = chartInfo['labels'];
        let data = chartInfo['data'];

		var config = {
			type: 'line',
			data: {
				labels: labels,
				datasets: [{
					label: 'Prediction',
					backgroundColor: 'rgba(41,148,192,0.4)',
					borderColor: 'rgba(41,148,192,0.4)',
					data: data,
					fill: true,
				}]
			},
			options: {
				responsive: true,
				title: {
					display: true,
					text: 'Number of Predictions Given Probability/Confidence Percentages'
				},
				tooltips: {
					mode: 'index',
					intersect: false,
				},
				hover: {
					mode: 'nearest',
					intersect: true
				},
				scales: {
					xAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Prediction Probability/Confidence (%)'
						}
					}],
					yAxes: [{
						display: true,
						scaleLabel: {
							display: true,
							labelString: 'Number Of Predictions'
						}
					}]
				}
			}
		};

		let ctx = document.getElementById(elementId).getContext('2d');
		return new Chart(ctx, config);
}