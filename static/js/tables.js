//helper functions
function percent_to_integer_band(percent) {
    const bound_check = (lower_bound, upper_bound) => {
        if (percent >= lower_bound && percent < upper_bound)
            return true
        return false
    }

    if (bound_check(0,9.5))
        return 0
    else if (bound_check(9.5,14.5))
        return 1
    else if (bound_check(14.5,19.5))
        return 2
    else if (bound_check(19.5,23.5))
        return 3
    else if (bound_check(23.5,26.5))
        return 4
    else if (bound_check(26.5,29.5))
        return 5
    else if (bound_check(29.5,33.5))
        return 6
    else if (bound_check(33.5,36.5))
        return 7
    else if (bound_check(36.5,39.5))
        return 8
    else if (bound_check(39.5,43.5))
        return 9
    else if (bound_check(43.5,46.5))
        return 10
    else if (bound_check(46.5,49.5))
        return 11
    else if (bound_check(49.5,53.5))
        return 12
    else if (bound_check(53.5,56.5))
        return 13
    else if (bound_check(56.5,59.5))
        return 14
    else if (bound_check(59.5,63.5))
        return 15
    else if (bound_check(63.5,66.5))
        return 16
    else if (bound_check(66.5,69.5))
        return 17
    else if (bound_check(69.5,73.5))
        return 18
    else if (bound_check(73.5,78.5))
        return 19
    else if (bound_check(78.5,84.5))
        return 20
    else if (bound_check(84.5,91.5))
        return 21
    else if (percent >= 91.5)
        return 22
}

//FORMATTERS
formatter_to_band_letter = function(cell, formatterParams, onRendered){
    if (cell.getValue() == "N/A"){
        cell.getElement().style.backgroundColor = "#E06666"
        return cell.getValue()
    }
    let integer_band = percent_to_integer_band(cell.getValue())
    let boundary_map = {
        0: "H",

        1: "G2",
        2: "G1",

        3: "F3",
        4: "F2",
        5: "F1",

        6: "E3",
        7: "E2",
        8: "E1",

        9: "D3",
        10: "D2",
        11: "D1",

        12: "C3",
        13: "C2",
        14: "C1",
        
        15: "B3",
        16: "B2",
        17: "B1",
 
        18: "A5",
        19: "A4",
        20: "A3",
        21: "A2",
        22: "A1",
    }
    return boundary_map[integer_band] 
}

formatter_to_band_integer = function(cell, formatterParams, onRendered){
    if (cell.getValue() == "N/A"){
        cell.getElement().style.backgroundColor = "#E06666"
        return cell.getValue()
    }
    return percent_to_integer_band(cell.getValue())
}

formatter_to_percentage = function(cell, formatterParams, onRendered){
    if (cell.getValue() == "N/A"){
        cell.getElement().style.backgroundColor = "#E06666"
        return cell.getValue()
    } 
    return cell.getValue() + "%"
}

const default_formatter = formatter_to_percentage

function init_table(table_id, columns, prefil_data = null, extra_constructor_params = {}) {
    let table_constructor = {
        // layout:"fitColumns",
        // responsiveLayout:"hide",
        // data: table_data,
        columns: columns,
        pagination: true,
        paginationMode: "local",
        columnHeaderVertAlign:"middle",

        selectable:true,

        paginationSize: 100,
        paginationSizeSelector:[25, 50, 100, 1000],
        layout:"fitDataTable", //fitDataStretch
        movableColumns: true,
        // layoutColumnsOnNewData:true
        downloadConfig:{
            columnHeaders:true, //do not include column headers in downloaded table
            columnGroups:true, //do not include column groups in column headers for downloaded table
            rowGroups:false, //do not include row groups in downloaded table
            columnCalcs:false, //do not include column calcs in downloaded table
        },
        downloadRowRange:"selected", //download selected rows
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
                table.dispatchEvent("extra_cols_loaded")
                return response.data
            } else
                return response;
        }
    }

    for (let key in extra_constructor_params){
        table_constructor[key] = extra_constructor_params[key]
    }

    let table_element = document.getElementById(table_id)
    let table = new Tabulator(table_element, table_constructor)
    table.extra_cols = []
    // table.get_cols = columns

    table.getElement = () => table_element
    table.reformatTable = function(formatter=null, cssClass=null) {
        let existing_cols = {}
        table.getColumns().forEach(function(col){
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
                    if (col_inner.cssClass && col_inner.cssClass.includes(cssClass)) {
                        if (formatter)
                            col_inner.formatter = formatter
                        else
                            delete col_inner.formatter
                    }
                })
            } else {
                if (col.cssClass && col.cssClass.includes(cssClass)) {
                    if (formatter)
                        col.formatter = formatter
                    else
                        delete col.formatter
                }
            }
        })
        table.setColumns(extract_cols)
    }

    let wrapper = wrap(table_element, document.createElement('div'))
    wrapper.classList.add('tabulator-wrapper')
    table.getWrapper = () => wrapper
    let table_components = document.createElement('div')
    table_components.classList.add('tabulator-components')
    wrapper.prepend(table_components)

    table.on("dataLoaded", function(){
        table.reformatTable(default_formatter, "format_grade")
        //handle formatting stuff
        var select_element = string_to_html_element(
            `   
                <select>
                    <option value="P">percent</option>
                    <option value="B">band</option>
                    <option value="I">band integer</option>
                </select>
            `
        )

        select_element.addEventListener("change", function(e){
            if (this.value == "P") {
                table.reformatTable(formatter_to_percentage, "format_grade")
            } else if (this.value == "B") {
                table.reformatTable(formatter_to_band_letter, "format_grade")
            } else if (this.value == "I") {
                table.reformatTable(formatter_to_band_integer, "format_grade")
            }
        })

        let download_excel = string_to_html_element(`<button class="tabulator-download">Download excel</button>`)
        let download_pdf = string_to_html_element(`<button class="tabulator-download">Download pdf</button>`)

        download_excel.addEventListener("click", function(e){
            table.download("xlsx", "data.xlsx", {});
        })
        download_pdf.addEventListener("click", function(e){
            table.downloadToTab("pdf", "data.pdf", {
                orientation:"landscape", //set page orientation to landscape
            });
        })

        let table_wrapper = table.getWrapper()

        table_wrapper.querySelector(".tabulator-components").prepend(select_element)
        table_wrapper.querySelector(".tabulator-components").appendChild(download_excel)
        table_wrapper.querySelector(".tabulator-components").appendChild(download_pdf)
    })

    // table.on("rowClick", function(e, row){
    //     if (typeof row.getData().page_url !== 'undefined') {
    //         window.location.href = row.getData().page_url
    //     }
    // });

    return table
}

var headerMenu = [
    {
        label:"Hide Column",
        action:function(e, column){
            column.toggle();
        }
    },
]

//define various table setups below
function load_students_table(extra_constructor_params = {}, extra_cols=true){
    let columns = [
        {formatter:"rowSelection", titleFormatter:"rowSelection", align:"center", headerSort:false},
        {title: "GUID", field: "GUID", topCalc: "count", headerFilter: "input", "frozen": true, headerContextMenu:headerMenu},
        {title: "Name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            headerMenu: headerMenu,
            columns: [
                {title: "Title", field: "degree_title"},
                {title: "Name", field: "degree_name"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross"},
            ],
            "headerHozAlign": "center",
        },
        {
            title: "Year data",
            headerMenu: headerMenu,
            columns: [
                {title: "Current level", field: "current_year"},
                {title: "Start year", field: "start_year"},
                {title: "End year", field: "end_year"},
            ],
            "headerHozAlign": "center",
        }
    ]

    let ajaxParams = {
        "fetch_table_data": true,
        "students": true,
    }
    if (typeof search_term !== "undefined") {
        ajaxParams.search_term = search_term
    }

    let final_extra_constructor_params = { ...extra_constructor_params,
        // groupBy: function(data){
        //     return data.start_year + " - " + data.end_year; //groups by data and age
        // },
        //context menus
        "ajaxParams": ajaxParams,
        rowContextMenu:[
            {
                label:"Hide Student",
                action:function(e, row){
                    row.delete();
                }
            },
            {
                label:"View Student Page",
                    action:function(e, row){
                        if (typeof row.getData().page_url !== 'undefined') {
                            window.location.href = row.getData().page_url
                        }
                    }
            },
        ],
        groupBy: 'current_year',
        initialSort: [{column: 'current_year', dir: 'dsc'}]
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
}

function load_courses_table(extra_constructor_params = {}, extra_cols=true){
    let columns = [
        {formatter:"rowSelection", titleFormatter:"rowSelection", align:"center", headerSort:false},
        {title: "Name", field: "name", topCalc: "count", headerFilter: "input"},
        {title: "Code", field: "code", headerFilter: "input"},
        {title: "Academic year", field: "academic_year"},
        {title: "Credits", field: "credits", bottomCalc: "sum"},
        {title: "Taught now?", field: "is_taught_now", formatter: "tickCross"},
    ]
    if (extra_cols) {
        columns.push({
            title: "Student performance",
            headerHozAlign: "center",
            columns: [
                {title: "Coursework grade", field: "coursework_avg", cssClass: "format_grade"},
                {title: "Exam grade", field: "exam_avg", cssClass: "format_grade"},
                {title: "Final weighted grade", field: "final_grade", cssClass: "format_grade"},
            ]
        })
    }
    let ajaxParams = {
        "fetch_table_data": true,
        "courses": true,
    }
    if (typeof search_term !== "undefined") {
        ajaxParams.search_term = search_term
    }

    let final_extra_constructor_params = { ...extra_constructor_params,
        "ajaxParams": ajaxParams,
        rowContextMenu:[
            {
                label:"Hide Course",
                action:function(e, row){
                    row.delete();
                }
            },
            {
                label:"View Course Page",
                    action:function(e, row){
                        if (typeof row.getData().page_url !== 'undefined') {
                            window.location.href = row.getData().page_url
                        }
                    }
            },
        ],
        groupBy: ['academic_year'],
        initialSort: [{column: 'academic_year', dir: 'dsc'}]
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
                chart_data[data[i].academic_year] = (chart_data[data[i].academic_year] || 0) + 1;
            }
            chart.data.labels = Object.keys(chart_data);
            chart.data.datasets[0].data = Object.values(chart_data);
            chart.update('active');
        }
    })
}