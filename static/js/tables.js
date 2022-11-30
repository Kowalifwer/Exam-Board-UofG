//FORMATTERS
custom_formatter = function(cell, formatterParams, onRendered){
    let cell_value = cell.getValue().toString()
        if (cell_value.includes("%")) {
            let boundary_map = {
            20: "F",
            40: "D",
            60: "C",
            80: "B",
            90: "A",
        }
        //make cell value an integer
        cell_value = parseInt(cell_value.replace("%", ""))
        let boundaries = Object.keys(boundary_map).sort((a, b) => a - b)
        //find what cell.getValue() is closest too from boundaries
        let closest = boundaries.reduce(function(prev, curr) {
            return (Math.abs(curr - cell_value) < Math.abs(prev - cell_value) ? curr : prev);
        });
        let color = boundary_map[closest]

        return color
    }
    else return cell.getValue();
}


function init_table(table_id, columns, prefil_data = null, extra_constructor_params = {}) {
    let table_constructor = {
        // layout:"fitColumns",
        // responsiveLayout:"hide",
        // data: table_data,
        columns: columns,
        pagination: true,
        paginationMode: "local",
        paginationSize: 100,
        columnHeaderVertAlign:"middle",
    }

    if (prefil_data){
        table_constructor.data = prefil_data
    } else {
        table_constructor.ajaxURL = window.location.href
        table_constructor.ajaxParams = {
            "fetch_table_data": true,
            // "size": pagination_size,
            // "page": page_count,
        }
        table_constructor.ajaxConfig = "GET"
        table_constructor.ajaxResponse = function(url, params, response) {
            if (typeof response.extra_cols !== 'undefined') {
                table.extra_cols = response.extra_cols
                // table.get_cols = columns.concat(response.extra_cols)
                return response.data
            } else
                return response;
        }
    }

    for (let key in extra_constructor_params){
        table_constructor[key] = extra_constructor_params[key]
    }

    let table = new Tabulator("#" + table_id, table_constructor)
    table.extra_cols = []
    // table.get_cols = columns

    //extra methods for table object.
    table.reformatTable = function(formatter=null) {
        let existing_cols = {}
        table.getColumns().forEach(function(col){
            // console.log(col.getDefinition());
            // console.log(col.getParentColumn())
            var parent_col = col.getParentColumn()
            if (parent_col) {
                var parent_defition = parent_col.getDefinition()
                existing_cols[parent_defition.title] = parent_defition
            } else {
                var col_definition = col.getDefinition()
                existing_cols[col_definition.title] = col_definition
            }
        });
        var extract_cols = Object.values(existing_cols)
        extract_cols.forEach(function(col){
            if (col.columns) {
                col.columns.forEach(function(col_inner) {
                    if (formatter)
                        col_inner.formatter = formatter
                    else
                        delete col_inner.formatter
                })
            } else {
                if (formatter)
                    col.formatter = formatter
                else
                    delete col.formatter
            }
        })
        table.setColumns(extract_cols)
    }
    return table
}

//define various table setups below
function load_students_table(extra_constructor_params = {}){
    let columns = [
        {title: "GUID", field: "GUID", topCalc: "count", headerFilter: "input"},
        {title: "Name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            columns: [
                {title: "Title", field: "degree_title"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross"},
            ],
            "headerHozAlign": "center",
        },
        {
            title: "Year data", columns: [
                {title: "Start year", field: "start_year"},
                {title: "End year", field: "end_year"},
            ],
            "headerHozAlign": "center",
        }
    ]
    let final_extra_constructor_params = { ...extra_constructor_params,
        // groupBy: function(data){
        //     return data.start_year + " - " + data.end_year; //groups by data and age
        // },
        // groupBy: 'start_year'
    }
    let table = init_table("students_table", columns, null, final_extra_constructor_params)
    
    table.on("dataLoaded", function(data){
        // page_count += 1
        console.log("data loaded");
        
        for (let i = 0; i < table.extra_cols.length; i++){
            table.addColumn(table.extra_cols[i])
        }
        // api(page_count, pagination_size).then(server_data => {
        //     table.addData(server_data.data)
        //     if (page_count < server_data.last_page) {
        //         table.dispatchEvent("dataLoaded") 
        //     } else {
        //         table.dispatchEvent("dataLoadedAll")
        //     }
        // })
        if (typeof chart !== 'undefined') {
            var chart_data = {};
            for (var i = 0; i < data.length; i++) {
                chart_data[data[i].start_year] = (chart_data[data[i].start_year] || 0) + 1;
            }
            chart.data.labels = Object.keys(chart_data);
            chart.data.datasets[0].data = Object.values(chart_data);
            chart.update('active');
        }
    })

    table.on("rowClick", function(e, row){
        if (typeof row.getData().page_url !== 'undefined') {
            window.location.href = row.getData().page_url
        }
    });

    var button = document.getElementById("change_format")
    if (button) {
        button.addEventListener("click", function(){
            table.reformatTable(custom_formatter)
        })
    }
    var reset_formatters = document.getElementById("reset_format")
    if (reset_formatters) {
        reset_formatters.addEventListener("click", ()=>{
            table.reformatTable()
        })
    }

    // table.on('dataFiltered', function(filters, rows){
    //     console.log("data filtered");
    // });

    // document.getElementById('table_action').addEventListener('click', function(e){
    //     table.updateColumnDefinition("GUID", {formatter: function(cell, formatterParams, onRendered) {
    //         cell.getElement().style.backgroundColor = "red";
    //         return cell.getValue();
    //     }})
    // });

    // document.getElementById('table_action_2').addEventListener('click', function(e){
    //     table.updateColumnDefinition("name", {formatter: "textarea"})
    //     table.updateColumnDefinition("GUID", {formatter: function(cell, formatterParams, onRendered) {
    //         cell.getElement().style.backgroundColor = "transparent";
    //         return cell.getValue();
    //     }})
    // })
}

function load_courses_table(extra_constructor_params = {}){
    let columns = [
        {title: "Name", field: "name", topCalc: "count", headerFilter: "input"},
        {title: "Code", field: "code", headerFilter: "input"},
        {title: "Academic year", field: "academic_year"},
        {title: "Credits", field: "credits", bottomCalc: "sum"},
        {title: "Taught now?", field: "is_taught_now", formatter: "tickCross"},
        {
            title: "Student performance",
            headerHozAlign: "center",
            columns: [
                {title: "Average coursework grade", field: "coursework_avg"},
                {title: "Average exam grade", field: "exam_avg"},
                {title: "Average overall grade", field: "overall_avg"},
                {title: "Final grade (weighted)", field: "final_grade"},
            ]
        }
    ]
    let final_extra_constructor_params = { ...extra_constructor_params,
        groupBy: ['academic_year']
    }
    let table = init_table("courses_table", columns, null, final_extra_constructor_params)

    table.on("dataLoaded", function(data){
        // page_count += 1
        console.log("data loaded");
        // api(page_count, pagination_size).then(server_data => {
        //     table.addData(server_data.data)
        //     if (page_count < server_data.last_page) {
        //         table.dispatchEvent("dataLoaded") 
        //     } else {
        //         table.dispatchEvent("dataLoadedAll")
        //     }
        // })
        if (typeof chart !== 'undefined') {
            var chart_data = {};
            for (var i = 0; i < data.length; i++) {
                chart_data[data[i].start_year] = (chart_data[data[i].start_year] || 0) + 1;
            }
            chart.data.labels = Object.keys(chart_data);
            chart.data.datasets[0].data = Object.values(chart_data);
            chart.update('active');
        }
    })

    table.on("rowClick", function(e, row){
        if (typeof row.getData().page_url !== 'undefined') {
            window.location = row.getData().page_url
        }
    });
}