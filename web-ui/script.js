document.getElementById("upload-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("csv-file");
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file!");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        // Send the file to the backend
        const response = await fetch("", { //provide api endpoint address here
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to upload file");
        }

        // Get the data from the response
        const data = await response.json();

        // Render Tables and Charts
        clearContainers();
        renderMatrix(data.desc_matrix);
        renderAvgPaceTable(data.avg_pace_day_week);
        renderTotalsTable(data.totals);
        renderYearlyMetricsTable(data.yearly_statistics);
        renderHistograms(data.histogram_data);
        renderBestPerformancesTable(data.best_perf);
        renderTimeSeriesCharts(data.time_series_data);
    } catch (error) {
        alert("Error: " + error.message);
    }
});

function clearContainers() {
    document.getElementById("matrix-container").innerHTML = "";
    document.getElementById("charts-container").innerHTML = "";
}

// Render Functions for Tables
function renderMatrix(matrix) {
    const container = document.getElementById("matrix-container");
    const table = document.createElement("table");

    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>Metric</th>
        <th>Count</th>
        <th>Mean</th>
        <th>Std</th>
        <th>Min</th>
        <th>25%</th>
        <th>50%</th>
        <th>75%</th>
        <th>Max</th>
    `;
    table.appendChild(headerRow);

    for (let i = 0; i < matrix.index.length; i++) {
        const row = document.createElement("tr");
        const roundValue = (value) =>
            typeof value === "number" ? value.toFixed(2) : value;

        row.innerHTML = `
            <td>${matrix.index[i]}</td>
            <td>${roundValue(matrix.count[i])}</td>
            <td>${roundValue(matrix.mean[i])}</td>
            <td>${roundValue(matrix.std[i])}</td>
            <td>${roundValue(matrix.min[i])}</td>
            <td>${roundValue(matrix["25%"][i])}</td>
            <td>${roundValue(matrix["50%"][i])}</td>
            <td>${roundValue(matrix["75%"][i])}</td>
            <td>${roundValue(matrix.max[i])}</td>
        `;
        table.appendChild(row);
    }
    container.appendChild(table);
}

function renderAvgPaceTable(avgPaceData) {
    const container = document.getElementById("matrix-container");

    const header = document.createElement("h2");
    header.textContent = "Average Pace by Day of the Week";
    container.appendChild(header);

    const table = document.createElement("table");
    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>Day</th>
        <th>Average Pace</th>
    `;
    table.appendChild(headerRow);

    for (const [day, pace] of Object.entries(avgPaceData)) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${day}</td>
            <td>${pace}</td>
        `;
        table.appendChild(row);
    }
    container.appendChild(table);
}

function renderTotalsTable(totals) {
    const container = document.getElementById("matrix-container");

    const header = document.createElement("h2");
    header.textContent = "Totals";
    container.appendChild(header);

    const table = document.createElement("table");
    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>Metric</th>
        <th>Total</th>
    `;
    table.appendChild(headerRow);

    for (const [metric, value] of Object.entries(totals)) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${metric.replace("_", " ").toUpperCase()}</td>
            <td>${typeof value === "number" ? value.toFixed(2) : value}</td>
        `;
        table.appendChild(row);
    }
    container.appendChild(table);
}

function renderYearlyMetricsTable(yearlyStatistics) {
    const container = document.getElementById("matrix-container");
    const header = document.createElement("h2");
    header.textContent = "Yearly Metrics Overview";
    container.appendChild(header);

    const table = document.createElement("table");
    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>Year</th>
        ${Object.keys(yearlyStatistics).map(metric => `<th colspan="4">${metric}</th>`).join("")}
    `;
    table.appendChild(headerRow);

    const subHeaderRow = document.createElement("tr");
    subHeaderRow.innerHTML = `
        <th></th>
        ${Object.keys(yearlyStatistics).map(() => `
            <th>Mean</th>
            <th>Std</th>
            <th>Min</th>
            <th>Max</th>
        `).join("")}
    `;
    table.appendChild(subHeaderRow);

    const years = yearlyStatistics[Object.keys(yearlyStatistics)[0]].Year;
    years.forEach((year, rowIndex) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${year}</td>
            ${Object.entries(yearlyStatistics).map(([_, data]) => `
                <td>${data.mean[rowIndex].toFixed(2)}</td>
                <td>${data.std[rowIndex].toFixed(2)}</td>
                <td>${data.min[rowIndex].toFixed(2)}</td>
                <td>${data.max[rowIndex].toFixed(2)}</td>
            `).join("")}
        `;
        table.appendChild(row);
    });

    container.appendChild(table);
}

// Render Functions for Charts
function renderHistograms(histogramData) {
    const container = document.getElementById("charts-container");

    Object.entries(histogramData).forEach(([metric, data]) => {
        const canvas = document.createElement("canvas");
        canvas.classList.add("histogram"); // Assign histogram class
        container.appendChild(canvas);

        const binRanges = data.bins.map((bin, index) => {
            if (index < data.bins.length - 1) {
                return `${bin.toFixed(2)}–${data.bins[index + 1].toFixed(2)}`;
            }
            return `${bin.toFixed(2)}+`;
        });

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: binRanges,
                datasets: [{
                    label: `Frequency of ${metric}`,
                    data: data.counts,
                    backgroundColor: "rgba(75, 192, 192, 0.6)"
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: `${metric} Histogram`
                    }
                },
                scales: {
                    x: { title: { display: true, text: `${metric} Bins` } },
                    y: { title: { display: true, text: "Count" }, beginAtZero: true }
                }
            }
        });
    });
}


function renderBestPerformancesTable(bestPerfData) {
    const container = document.getElementById("matrix-container");

    const header = document.createElement("h2");
    header.textContent = "Best Performances";
    container.appendChild(header);

    const table = document.createElement("table");
    const headerRow = document.createElement("tr");
    headerRow.innerHTML = `
        <th>Distance (km)</th>
        <th>Date</th>
        <th>Time</th>
        <th>Avg Pace</th>
    `;
    table.appendChild(headerRow);

    Object.entries(bestPerfData).forEach(([distance, performances]) => {
        const sectionRow = document.createElement("tr");
        sectionRow.innerHTML = `
            <td colspan="4" style="font-weight: bold; background-color: #f2faff; text-align: left;">
                ${distance} km
            </td>
        `;
        table.appendChild(sectionRow);

        performances.forEach(performance => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${distance}</td>
                <td>${new Date(performance.Date).toLocaleDateString()}</td>
                <td>${performance.Time}</td>
                <td>${performance["Avg Pace"]}</td>
            `;
            table.appendChild(row);
        });
    });

    container.appendChild(table);
}

function renderTimeSeriesCharts(timeSeriesData) {
    const container = document.getElementById("charts-container");

    Object.entries(timeSeriesData).forEach(([metric, data]) => {
        const canvas = document.createElement("canvas");
        canvas.classList.add("line-chart"); // Assign line-chart class
        container.appendChild(canvas);

        const formattedDates = data.dates.map(date =>
            new Date(date).toLocaleDateString()
        );

        new Chart(canvas, {
            type: "line",
            data: {
                labels: formattedDates,
                datasets: [
                    {
                        label: `${metric} (Raw Values)`,
                        data: data.values,
                        borderColor: "rgba(75, 192, 192, 1)",
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: `${metric} (Moving Avg)`,
                        data: data.moving_average,
                        borderColor: "rgba(255, 99, 132, 1)",
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: `${metric} Over Time`
                    }
                },
                scales: {
                    x: { title: { display: true, text: "Date" } },
                    y: { title: { display: true, text: metric }, beginAtZero: true }
                }
            }
        });
    });
}

