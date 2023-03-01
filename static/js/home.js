    let chart_data = {};
    let boundaries = ["A","B","C","D","E","F","G","H","MV","CW","CR"]
    for (let x in boundaries) {
        chart_data[boundaries[x]] = 0
    }
    let total = 0
    let colors = [c_good,c_good,c_good,c_mid,c_poor,c_poor,c_poor,c_poor, chart_colors[1], chart_colors[3], chart_colors[6]]
    assessment_count_distribution_data.forEach(function(row){
        if (row.grade != undefined) {
            band_grade = boundary_map[Math.round(row.grade)][0]
            chart_data[band_grade] = (chart_data[band_grade] || 0) + row.count
            total += row.count
        } else {
            if (row.preponderance != "NA")
                chart_data[row.preponderance] = row.count
        }
    })

    let data = {
        data: {
            labels: Object.keys(chart_data),
            datasets: [
                {
                    label: "Grade band",
                    data: Object.values(chart_data),
                    barPercentage: 0.90,
                    backgroundColor: colors,
                }
            ]
        },
        extra_settings: {
            y_title: "Number of grades",
            x_title: "Final assessment band",
            tooltip_extra: "Percentage across all: ",
            tooltip_extra_data_size: total,
            legend_display: false,
        }
    }
    new Chart(document.getElementById("assessment_count_distribution"), defaultChartSetup(data))

    chart_data = {}
    for (let row of assessment_avg_distribution_data) {
        let year = row.course__academic_year
        let type = row.assessment__type
        let avg = row.grade__avg
        if (chart_data[year] == undefined) {
            chart_data[year] = {}
        }
        chart_data[year][type] = Math.round(avg * 100) / 100
    }

    data = { 
        data: {
            labels: Object.keys(chart_data),
            datasets: [
                {
                    label: "Average Coursework GPA",
                    data: Object.values(chart_data).map(x => x.C),
                    barPercentage: 0.90,
                    backgroundColor: chart_colors[1],
                },
                {
                    label: "Average of all Exam results",
                    data: Object.values(chart_data).map(x => x.E),
                    backgroundColor: chart_colors[4],
                },
                {
                    label: "Average of all Group project assessed work",
                    data: Object.values(chart_data).map(x => x.G),
                    backgroundColor: chart_colors[3],
                    hidden: true,
                },
                {
                    label: "Average of all Individual project assessed work",
                    data: Object.values(chart_data).map(x => x.I),
                    backgroundColor: chart_colors[5],
                    hidden: true,
                },
            ]
        },
        extra_settings: {
            y_title: "GPA",
            x_title: "Academic Year",
        }
    }
    
    new Chart(document.getElementById("assessment_avg_distribution"), defaultChartSetup(data))