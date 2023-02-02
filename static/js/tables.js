//helper functions
const preponderance_list = ["NA", "MV", "CW", "CR"]
const boundary_map = {
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

const preponderance_formatter = function (cell) {
    let value = cell.getValue()
    if (value == "N/A"){
        cell.getElement().style.backgroundColor = "#E06666"
    } else if (value == "NA") {
        cell.getElement().style.backgroundColor = "#BBDBB4"
    } else if (value == "MV"){
        cell.getElement().style.backgroundColor = "#648DE5"
    } else if (value == "CW"){
        //set cell colour to dark gray
        cell.getElement().style.backgroundColor = "#EFF2F1"
    } else if (value == "CR"){
        //set cell colour to dark red
        cell.getElement().style.backgroundColor = "#A64253"
    }
    return value
}

const is_preponderance = function (cell) {
    if (cell.getValue() == "N/A")
        return true
    if (preponderance_list.includes(cell.getValue()))
        return true
    return false
}

function percent_to_integer_band(percent, round_up=true) {
    // if (round_up)
    //     return Math.ceil(percent/(100/22))
    // else
    //     return (percent/(100/22)).toFixed(1)

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
const formatter_to_band_letter = function(cell, formatterParams, onRendered){
    if (is_preponderance(cell)) {
        return preponderance_formatter(cell)
    }

    let integer_band = percent_to_integer_band(cell.getValue())
    return boundary_map[integer_band] 
}

const formatter_to_band_integer = function(cell, formatterParams, onRendered){
    if (is_preponderance(cell)) {
        return preponderance_formatter(cell)
    }
    return percent_to_integer_band(cell.getValue())
}

const formatter_to_percentage = function(cell, formatterParams, onRendered){
    if (is_preponderance(cell)) {
        return preponderance_formatter(cell)
    }
    return cell.getValue() + "%"
}

const custom_average_calculator = function(values, data, calcParams){
    let total = 0;
    let count = 0;

    let check_list = [...preponderance_list, "N/A", ""]

    values.forEach(function(value){
        if (!check_list.includes(value)) {
            total += parseInt(value);
            count++;
        }
    });

    if (count) {
        return total / count;
    } else {
        return "N/A";
    }
}

const default_formatter = formatter_to_band_letter

function init_table(table_id, columns, prefil_data = null, extra_constructor_params = {}, settings={}) {
    let title = ""
    if (settings.title)
        title = settings.title

    let table_constructor = {
        // layout:"fitColumns",
        // responsiveLayout:"hide",
        // data: table_data,
        columns: columns,
        pagination: true,
        paginationMode: "local",
        columnHeaderVertAlign:"middle",

        selectable:true,
        rowHeight: 30,
        groupToggleElement: "header",

        paginationSize: 100,
        paginationSizeSelector:[25, 50, 100, 1000],
        layout:"fitDataStretch", //fitDataStretch
        movableColumns: true,
        dataLoaderLoading:`<span>Loading ${title} table data</span>`,
        // layoutColumnsOnNewData:true
        downloadConfig:{
            columnHeaders:true, //do not include column headers in downloaded table
            columnGroups:true, //do not include column groups in column headers for downloaded table
            rowGroups:false, //do not include row groups in downloaded table
            columnCalcs:false, //do not include column calcs in downloaded table
        },
        rowContextMenu: []
        //downloadRowRange:"selected", //download selected rows
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
                table.dispatchEvent("dataLoadedInitial")
                return response.data
            } else {
                table.dispatchEvent("dataLoadedInitial")
                return response
            }
        }
    }

    for (let key in extra_constructor_params){
        table_constructor[key] = extra_constructor_params[key]
    }
    table_constructor.rowContextMenu.push({
        separator: true
    })
    table_constructor.rowContextMenu.push({
        label:"<div class='inline-icon' title='The following actions will affect all the selected rows. Note that all the actions in this category are reversible - so do not worry if you accidentally click something.'><img src='/static/icons/info.svg'></i><span>Multi-row actions</span></div>",
        menu:[
            {
                label:"<div class='inline-icon' title='Note that this is simply hiding the rows, meaning no table data gets manipulated.'><img src='/static/icons/info.svg'></i><span>Hide row(s)</span></div>",
                action:function(e, row){
                    let selected_rows = table.getSelectedRows()
                    selected_rows.forEach(function(inner_row){
                        table.hidden_rows.push(inner_row.getData())
                        inner_row.getElement().classList.add('hidden-row')
                    })
                    if (table.hidden_rows) {
                        document.getElementById('unhide-rows').classList.remove('hidden')
                    }
                }
            },
            {
                label:"<div class='inline-icon' title='Note that this action properly removes data from the table (locally, and not from the database), - this can be useful for preparing the table for data extraction, such as generating an excel file, for example.'><img src='/static/icons/info.svg'></i><span>Delete row(s)</span></div>",
                action:function(e, row){
                    let selected_rows = table.getSelectedRows()
                    selected_rows.forEach(function(inner_row){
                        table.deleted_rows.push(inner_row.getData())
                        inner_row.delete()
                    })
                    if (table.deleted_rows) {
                        document.getElementById('undelete-rows').classList.remove('hidden')
                    }
                }
            },
        ]
    })

    let table_element = (isElement(table_id)) ? table_id : document.getElementById(table_id)
    table_element.dataset.edit_mode = 0
    let table = new Tabulator(table_element, table_constructor)
    table.extra_cols = []
    table.settings = settings
    // table.get_cols = columns

    table.hidden_rows = []
    table.deleted_rows = []

    table.addNotification = function(message="Table in edit mode! Click on any of the <span class='tabulator-notification-hint'>outlined cells</span>, to edit the data inside.") {
        let notification = document.createElement('div')
        notification.classList.add('tabulator-notification')
        notification.innerHTML = message
        table.getWrapper().prepend(notification)
    }

    table.removeNotification = function() {
        let notification = table.getWrapper().querySelector('.tabulator-notification')
        if (notification) {
            notification.remove()
        }
    }

    table.getElement = () => table_element
    table.reformatTable = function(formatter=null, cssClass=null, new_bottom_calc_function=null) {
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
                        if (formatter) {
                            col_inner.formatter = formatter
                            if (new_bottom_calc_function) {
                                col_inner.bottomCalc = new_bottom_calc_function
                                col_inner.bottomCalcFormatter = formatter
                            }
                        }
                        else
                            delete col_inner.formatter
                    }
                })
            } else {
                if (col.cssClass && col.cssClass.includes(cssClass)) {
                    if (formatter) {
                        col.formatter = formatter
                        if (new_bottom_calc_function) {
                            col.bottomCalc = new_bottom_calc_function
                            col.bottomCalcFormatter = formatter
                        }
                    }
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

    table.on("dataLoadedInitial", function(){
        for (let i = 0; i < table.extra_cols.length; i++){
            table.addColumn(table.extra_cols[i])
        }
        
        table.reformatTable(default_formatter, "format_grade", custom_average_calculator)
        //handle formatting stuff
        var select_element = string_to_html_element(
            `
                <select>
                    <option value="B">band</option>
                    <option value="P">percent</option>
                    <option value="I">band integer</option>
                </select>
            `
        )

        select_element.addEventListener("change", function(e){
            if (this.value == "P") {
                table.reformatTable(formatter_to_percentage, "format_grade", custom_average_calculator)
            } else if (this.value == "B") {
                table.reformatTable(formatter_to_band_letter, "format_grade", custom_average_calculator)
            } else if (this.value == "I") {
                table.reformatTable(formatter_to_band_integer, "format_grade", custom_average_calculator)
            }
        })

        let download_excel = string_to_html_element(`<button class="tabulator-download">Download excel</button>`)
        let download_pdf = string_to_html_element(`<button class="tabulator-download">Download pdf</button>`)
        let unhide_rows = string_to_html_element(`<button id="unhide-rows" class="hidden">Unhide rows</button>`)
        let undelete_rows = string_to_html_element(`<button id="undelete-rows" class="hidden">Add back deleted rows</button>`)
        let column_manager = string_to_html_element(`<button class="column-manager">Column manager</button>`)

        column_manager.addEventListener("click", function(){
            var columns = table.getColumns();
            var menu_container = document.createElement("div");
            menu_container.classList = "tabulator-columns-menu";
            menu_container.width = "200px";
            menu_container.height = "500px";

            for(let column of columns){
                if (!column.getDefinition().title)
                    continue
                //create checkbox element using font awesome icons
                let checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.checked = column.isVisible();

                //build label
                let label = document.createElement("label");
                let title = document.createElement("span");

                title.textContent = " " + column.getDefinition().title;

                label.appendChild(title);
                label.appendChild(checkbox);

                //create menu item
                menu_container.appendChild(label);

                checkbox.addEventListener("change", function() {
                    //toggle current column visibility
                    column.toggle();
                })
            }
            Popup.init(menu_container)
        })
            

        unhide_rows.addEventListener("click", function(e){
            table.getElement().querySelectorAll(".hidden-row").forEach(function(row){
                row.classList.remove("hidden-row")
            })
            table.hidden_rows = []
            unhide_rows.classList.add("hidden")
        })

        undelete_rows.addEventListener("click", function(e){
            table.addData(table.deleted_rows)
            table.deleted_rows = []
            undelete_rows.classList.add("hidden")
        })

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
        table_wrapper.querySelector(".tabulator-components").appendChild(column_manager)

        let moderate_course_button = string_to_html_element(`<button class="tabulator-moderate">Moderate course</button>`)
        if (settings.backend_course_id) {
            moderate_course_button.addEventListener("click", function(e){
                render_course_moderation_section(settings.backend_course_id, table)
            })
            table_wrapper.querySelector(".tabulator-components").appendChild(moderate_course_button)
        }
        table_wrapper.querySelector(".tabulator-components").appendChild(unhide_rows)
        table_wrapper.querySelector(".tabulator-components").appendChild(undelete_rows)
    })

    table.on("dataProcessed", function(){
        table.reloadCharts()
    })

    table.setReloadFunction = (reload_function, reload_function_parameter_list) => {
        table.reload_function = reload_function
        table.reload_function_parameter_list = reload_function_parameter_list
    }


    table.destroyCharts = function(){
        for (var chart of table.charts) {
            chart.destroy()
        }
    }

    table.reloadTable = (message=null) => {
        table.destroyCharts()
        
        if (! table.reload_function || ! table.reload_function_parameter_list) {
            console.warn("No reload function set for table")
            return
        }
        let table_wrapper = table.getWrapper()
        //delete all children in wrapper, except for the tabulator element
        table_wrapper.querySelectorAll(":scope *:not(.tabulator)").forEach(child => child.remove())
        table.reload_function(...table.reload_function_parameter_list)
        if (message) {
            table_wrapper.prepend(string_to_html_element(`<p>${message}</p>`))
        }
    }

    table.chart_links = []

    table.addChartLink = function(chart_link){
        table.chart_links.push(chart_link)
    }

    table.charts = []

    table.reloadCharts = function(){
        for (var link_data of table.chart_links) {
            let chart_setup = link_data[1](table)

            let default_setup = {
                type: 'bar',
                data: {},
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                },
                responsive : true,            }
            let final_setup = {...default_setup, ...chart_setup}

            let chart = new Chart(link_data[0], final_setup)
            
            table.charts.push(chart)
        }
    }

    return table
}

//define various table setups below
function load_students_table(extra_constructor_params = {}, extra_cols=true, settings={'title': 'Students'}){
    let columns = [
        {formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false},
        {title: "GUID", field: "GUID", headerFilter: "input", "frozen": true},
        {title: "Name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            columns: [
                {title: "Title", field: "degree_title"},
                {title: "Name", field: "degree_name"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross"},
                {title: "Faster route?", field: "is_faster_route", formatter: "tickCross"},
            ],
            "headerHozAlign": "center",
        },
        {
            title: "Year data",
            columns: [
                {title: "Current level", field: "current_year"},
                {title: "Start year", field: "start_year"},
                {title: "End year", field: "end_year"},
            ],
            "headerHozAlign": "center",
        },
    ]

    let ajaxParams = {
        "fetch_table_data": true,
        "students": true,
    }
    if (typeof search_term !== "undefined") {
        ajaxParams.search_term = search_term
    }

    let rowContextMenu = [
        {
            label:"View Student breakdown page",
                action:function(e, row){
                    if (typeof row.getData().page_url !== 'undefined') {
                        window.location.href = row.getData().page_url
                    }
                }
        },
    ]
    if (typeof backend_course_id !== "undefined") {
        rowContextMenu.push({
            label: "Detailed Student assessment breakdown popup",
            action: function(e, row){
                create_student_course_detailed_table_popup(row.getData().GUID, backend_course_id, row.getTable())
            }   
        }) 
    }


    let final_extra_constructor_params = { ...extra_constructor_params,
        // groupBy: function(data){
        //     return data.start_year + " - " + data.end_year; //groups by data and age
        // },
        //context menus
        ajaxParams: ajaxParams,
        rowContextMenu:rowContextMenu,
        groupBy: 'current_year',
        initialSort: [{column: 'current_year', dir: 'dsc'}],
        placeholder: "Student data loading...",
    }
    let table = init_table("students_table", columns, null, final_extra_constructor_params, settings={...settings, ...{title: "Students"}})

    table.setReloadFunction(load_students_table, [extra_constructor_params, extra_cols, settings])

    table.on("tableBuilt", function() {
        table.setGroupHeader(function(value, count, data, group){
            return `Number of ${value} students:<span class='info-text'>${count}</span>`; //return the header contents
        });
    })

    if (document.getElementById("students_final_grade")) {
    table.addChartLink([
        document.getElementById("students_final_grade"), function(table_inner) {
            let table_data = table_inner.getData()
            let chart_data = {};
            let boundaries = ["A","B","C","D","E","F","G","H"]
            for (let x in boundaries) {
                chart_data[boundaries[x]] = 0
            }
            table_data.forEach(function(row){
                let band_grade = boundary_map[percent_to_integer_band(row.final_grade)][0]
                chart_data[band_grade] = (chart_data[band_grade] || 0) + 1;
            })

            //make abc grades pleasant green color, d grade yellow, and e f g h red
            let colors = ["#7DDE92","#7DDE92","#7DDE92","#FF9B71","#F15156","#F15156","#F15156","#F15156"]

            return {
                data: {
                    labels: Object.values(boundaries),
                    datasets: [
                        {
                            label: "Number of students",
                            data: Object.values(chart_data),
                            barPercentage: 0.90,
                            backgroundColor: colors,
                        }
                    ]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: "Number of students",
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: "Final grade for course",
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                footer: function(tooltipItems) {
                                    return "Percentage of students: " + (tooltipItems[0].parsed.y / table_data.length * 100).toFixed(2) + "%"
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: "Final grade distribution for course",
                        }

                    }
                }
            } 
            
        }
    ])
    }
    
    table.on("dataLoaded", function(data){
        // page_count += 1
        // api(page_count, pagination_size).then(server_data => {
        //     table.addData(server_data.data)
        //     if (page_count < server_data.last_page) {
        //         table.dispatchEvent("dataLoaded") 
        //     } else {
        //         table.dispatchEvent("dataLoadedAll")
        //     }
        // })
        // if (typeof chart !== 'undefined') {
        //     var chart_data = {};
        //     for (var i = 0; i < data.length; i++) {
        //         chart_data[data[i].start_year] = (chart_data[data[i].start_year] || 0) + 1;
        //     }
        //     chart.data.labels = Object.keys(chart_data);
        //     chart.data.datasets[0].data = Object.values(chart_data);
        //     chart.update('active');
        // }
    })
}

function load_degree_classification_table(level=4) {
    let columns = [
        {formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false},
        {title: "GUID", field: "GUID", topCalc: "count", headerFilter: "input", "frozen": true},
        {title: "Name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            columns: [
                {title: "Title", field: "degree_title"},
                {title: "Name", field: "degree_name"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross"},
                {title: "Faster route?", field: "is_faster_route", formatter: "tickCross"},
            ],
            "headerHozAlign": "center",
        },
        {
            title: "Year data",
            columns: [
                {title: "Current level", field: "current_year"},
                {title: "Start year", field: "start_year"},
                {title: "End year", field: "end_year"},
            ],
            "headerHozAlign": "center",
        },
        {title: "Degree classification", field: "class"},
        {title: "Final band", field: "final_band"},
        {title: "Final GPA", field: "final_gpa"},
        {title: "L5 band", field: "l5_band"},
        {title: "L5 GPA", field: "l5_gpa"},
        {title: "L4 band", field: "l4_band"},
        {title: "L4 GPA", field: "l4_gpa"},
        {title: "L3 band", field: "l3_band"},
        {title: "L3 GPA", field: "l3_gpa"},
        {title: "> A", field: "greater_than_a"},
        {title: "> B", field: "greater_than_b"},
        {title: "> C", field: "greater_than_c"},
        {title: "> D", field: "greater_than_d"},
        {title: "> E", field: "greater_than_e"},
        {title: "> F", field: "greater_than_f"},
        {title: "> G", field: "greater_than_g"},
        {title: "> H", field: "greater_than_h"},
        {title: "Team (lvl 3 Hons)", field: "team"},
        {title: "Individual (lvl 4 Hons)", field: "project"},
        {title: "Individual (lvl 5 M)", field: "project_masters"},
    ]

    if (level != 5) {
        for (let i = 0; i < columns.length; i++) {
            if (["l5_band", "l5_gpa", "project_masters"].includes(columns[i].field)) {
                columns.splice(i, 1);
                i--;
            }
        }
    }

    let table = init_table("degree_classification_table_"+level, columns, null, {
        rowContextMenu: [{
            label:"View Student breakdown page",
                action:function(e, row){
                    if (typeof row.getData().page_url !== 'undefined') {
                        window.location.href = row.getData().page_url
                    }
                } 
        }],
        "ajaxParams": {
            "fetch_table_data": true,
            "level": level,
        }
    }, {'title': 'Degree classification data for level '+level+' students'})

    table.addChartLink([document.getElementById("degree_classification_chart_"+level), function(table_inner) {
        let table_data = table_inner.getData()
        let classes = ["Fail", "3rd", "2:2", "2:1", "1st"]
        let chart_data = []
        for (let x in classes) {
            chart_data[classes[x]] = 0
        }
        table_data.forEach(function(row){
            chart_data[row.class] = (chart_data[row.class] || 0) + 1;
        })
        return {
            data: {
                labels: classes,
                datasets: [
                    {
                        label: "Number of students",
                        data: Object.values(chart_data),
                    }
                ]
            }
        }
    }])

    // table.addChartLink([document.getElementById("degree_classification_chart2_"+level), function(table_data) {
    //     let classes = ["Fail", "3rd", "2:2", "2:1", "1st"]
    //     let chart_data = []
    //     for (let x in classes) {
    //         chart_data[x[1]] = 0
    //     }
    //     table_data.forEach(function(row){
    //         chart_data[row.class] = (chart_data[row.class] || 0) + 1;
    //     })
    //     return {
    //         labels: classes,
    //         datasets: [
    //             {
    //                 label: "Number of students",
    //                 data: Object.values(chart_data),
    //             }
    //         ]
    //     }
    // }])

}

function create_student_course_detailed_table_popup(student_GUID=null, course_id=null, parent_table_to_reload=null){
    if (student_GUID && course_id) {
        let columns = [
            // {formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false},
            {title: "Assessment type", field: "type"},
            {title: "Assessment name", field: "name"},
            {title: "Weighting", field: "weighting", bottomCalc: "sum", formatter: "money", formatterParams: {precision: 0, symbol: "%", symbolAfter: true}},
            {title: "Grade", field: "grade", cssClass: "format_grade"},
            {title: "Preponderance", field: "preponderance", cssClass: "edit-mode", formatter: preponderance_formatter, editor: "list", editorParams: {
                values: preponderance_list
            }},
            {title: "AssessmentResult ID", field: "result_id", visible: false},
        ]
    
        let ajaxParams = {
            "fetch_table_data": true,
            "students": true,
            "student_GUID": student_GUID,
            "course_id": course_id,
        }
    
        let final_extra_constructor_params = {
            "ajaxParams": ajaxParams,
            "selectable": false,
            "placeholder": "Popup loading...",
            "pagination": false,
        }
        
        let elt = document.createElement("div")
        document.body.appendChild(elt)
        let table = init_table(elt, columns.map((col) => {
            return {...col, editor: false, cssClass: ""}
        }), null, final_extra_constructor_params)
        table.getElement().style.marginTop = "10px"
        table.getElement().style.marginBottom = "10px"
        
        let wrapper = table.getWrapper()
        let popup = Popup.init(wrapper)

        let edit_button = document.createElement("button")
        let table_element = table.getElement()
        edit_button.innerHTML = "Edit preponderance"
        edit_button.addEventListener('click', function(){
            if (table_element.dataset.edit_mode == 1) {
                if (confirm("Are you sure you want to save the changes? - this will overwrite the current preponderance values for this student, and reload the tables on the page.")) {
                    this.innerHTML = "Edit preponderance"
                    table.removeNotification()
                    table_element.dataset.edit_mode = 0
                    table.setColumns(columns.map(col => {
                        return {...col, editor: false, cssClass: ""}
                    }))
                    let table_data = table.getData()
                    // if (JSON.stringify(table_data) === JSON.stringify(data_json)) {
                    //     console.log("no changes")
                    // } else {
                    //     console.log("changes")
                    // }
                    //api call here to save the data.
                    api_post("update_preponderance", table_data).then(response => {
                        if (response.data) {
                            parent_table_to_reload.reloadTable()
                            popup.close()
                            console.log(response.status)
                                //TODO: add a success message here
                        } else {
                            alert(response.status)
                        }
                    })
                }
            } else {
                table.addNotification()
                this.innerHTML = "Save changes!"
                table.setColumns(columns)
                console.log(columns)
                table_element.dataset.edit_mode = 1
            }
        })
        popup.content.appendChild(edit_button)
    
    } else {
        alert("Please select a student first!")
    }
    
}

function load_courses_table(extra_constructor_params = {}, extra_cols=true, settings={}){
    console.log(settings)
    let columns = [
        {formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false},
        {title: "Name", field: "name", headerFilter: "input"},
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
    } else {
        columns.push({
            title: "Cohort average performance",
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

    let rowContextMenu = [
        {
            label:"View Course Page",
                action:function(e, row){
                    if (typeof row.getData().page_url !== 'undefined') {
                        window.location.href = row.getData().page_url
                    }
                }
        },
        {
            label:"Moderate course grades",
            action:function(e, row){
                render_course_moderation_section(row.getData().course_id)
            }
        }
    ]

    if (settings.student) {
        rowContextMenu.push({
            label: "Detailed Student assessment breakdown popup",
            action: function(e, row){
                create_student_course_detailed_table_popup(settings.student.GUID, row.getData().course_id, row.getTable())
            }
        })
    }

    let final_extra_constructor_params = { ...extra_constructor_params,
        ajaxParams: ajaxParams,
        rowContextMenu:rowContextMenu,
        groupBy: ['academic_year'],
        initialSort: [{column: 'academic_year', dir: 'dsc'}],
        placeholder: "Course data loading...",
    }
    let table = init_table("courses_table", columns, null, final_extra_constructor_params, settings)

    table.on("tableBuilt", function() {
        table.setGroupHeader(function(value, count, data, group){
            if (settings.student) {
                //reduce the "credits" in each row of data
                console.log(data)
                let course_credits = data.reduce(function(a, b) {
                    return a + b["credits"]
                }, 0)
                return `<span class='info-text'>${count}</span> courses in ${value}, for a total of <span class='${(course_credits < 120) ? "error-color":"success-color"}'>${course_credits} credits<span>`; //return the header contents
            } else {
                return `<span class='info-text'>${count}</span> courses offered in ${value}`; //return the header contents
            }
        });
    })
    
    

    if (settings.student) {
        table.addChartLink([document.getElementById("student_level_chart"), function(table_inner) {
        let student_data = settings.student
        let table_data = table_inner.getData()
        let chart_data = {};
        let year_datas = []

        for (let x = student_data.start_year; x < student_data.end_year; x++) {
            year_datas.push({
                'year': x + 1,
                'level': (student_data.is_faster_router) ? x+1-student_data.start_year : x+1-student_data.start_year + 1,
            })
            // `${student_data.start_year} - level {(student_data.is_faster_router) ? x : x + 1}`
        }

        let grouped_data = table_inner.getCalcResults()
        for (let year in grouped_data) {
            let year_data = grouped_data[year]
            percent_to_integer_band
            chart_data[year] = percent_to_integer_band(year_data.bottom.final_grade, false)
        }

        //make abc grades pleasant green color, d grade yellow, and e f g h red
        return {
            data: {
                labels: Object.keys(chart_data),
                datasets: [
                    {
                        label: "GPA",
                        data: Object.values(chart_data),
                        barPercentage: 0.90,
                    }
                ]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Academic year",
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Final GPA",
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: "Final GPA across all Academic years",
                    }
                }
            }
        }
    }])
    }
    

    table.setReloadFunction(load_courses_table, [extra_constructor_params, extra_cols, settings])

    table.on("dataLoaded", function(data){
        // page_count += 1
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

function render_course_moderation_section(course_id, parent_table=null) {
    //course_data.assessments
    let final_extra_constructor_params = {
        ajaxParams: {
            "fetch_table_data": true,
            "assessments": true,
            "course_id": course_id,
        },
        pagination: false,
        placeholder: "Assessment data loading...",
    }
    
    let wrapper = string_to_html_element(`
        <div class="moderation-popup">
            <p>Please select one or multiple assignments, to moderate</p>
            <div id="assessments_table"></div>
            <div id="moderation-input-area" class="disabled moderation-input-area">
                <button id="moderation-increase">Increase bands</button>
                <button id="moderation-decrease">Decrease bands</button>
                <button id="moderation-remove">Remove moderation</button>

                <p>by</p>
                <select id="moderation-value">
                    <option value="0" default>--Select number of bands--</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                    <option value="5">5</option>
                    <option value="6">6</option>
                </select>
            </div>
        </div>
    `)
    
    document.body.appendChild(wrapper)
    
    let columns = [
        {formatter:"rowSelection", titleFormatter:"rowSelection", headerSort:false},
        {title: "Assessment type", field: "type"},
        {title: "Assessment name", field: "name"},
        {title: "Weighting", field: "weighting", bottomCalc: "sum", formatter: "money", formatterParams: {precision: 0, symbol: "%", symbolAfter: true}},
        {title: "Current moderation", field: "moderation", headerHozAlign: "center"},
        {title: "Moderation User", field: "moderation_user", headerHozAlign: "center"},
        {title: "Moderation Date", field: "moderation_date", headerHozAlign: "center"},
    ]
    let table = init_table(document.getElementById("assessments_table"), columns, null, final_extra_constructor_params)
    let popup = Popup.init(wrapper)

    const handle_moderation = (mode) => {
        let moderation_value_elt = document.getElementById("moderation-value")
        let moderation_value = moderation_value_elt.options[moderation_value_elt.selectedIndex].value
        if (moderation_value == 0) {
            alert("Please select a number of bands to moderate by")
            return
        }
        api_post("moderation", {"mode": mode, "value": moderation_value, "assessment_ids": table.getSelectedData().map(x => x.id), "course_id": course_id}).then(data => {
            if (data.data) {
                popup.close()
                if (parent_table)
                    parent_table.reloadTable()
            }
             else {
                alert("Error: " + data.status)
            }
        })
    }

    document.getElementById("moderation-increase").addEventListener("click", function() {handle_moderation("increase")})
    document.getElementById("moderation-decrease").addEventListener("click", function() {handle_moderation("decrease")})
    document.getElementById("moderation-remove").addEventListener("click", function() {handle_moderation("remove")})

    table.on("rowSelectionChanged", function(data, rows){
        let input_area = document.getElementById("moderation-input-area")
        if (rows.length > 0) {
            input_area.classList.remove("disabled")
        } else {
            input_area.classList.add("disabled")
        }
    })
    // let table = init_table(table_placeholder, xd, null, final_extra_constructor_params)
    //Please select the assessments that you would like to moderate. You can select one, or  multiple.
    //selected.getRows()...
    //Step 1: select the assessments from the table that you would like to moderate. click next.
    //Step 2: select the moderation rules you would like to apply. click next.
    //Step 3: review page: shows the moderated grades. Are you sure you want to apply these grades? click next.
}


function load_grading_rules_table(data_json){
    // let tooltip_function = function(e, cell, onRendered){
    //     var el = document.createElement("div");
    //     el.innerText = "Left click cell to edit."; //return cells "field - value";
    //     return el; 
    // }

    let columns = [
        // {formatter:"rowSelection", titleFormatter:"rowSelection", align:"center", headerSort:false},
        {title: "Name", field: "name", editor: false, clickPopup: "Hello"},
        {title: "Standard lower GPA", field: "std_low_gpa", editor: "number", editorParams: {min: 0, max: 22, step: 0.1}, cssClass: "edit-mode"},
        {title: "Discretionary lower GPA", field: "disc_low_gpa", editor: "number", editorParams: {min: 0, max: 22, step: 0.1}, cssClass: "edit-mode"},
        {title: "Character Band", field: "char_band", visible: false, editor: "list", cssClass: "edit-mode",
            editorParams: {
                values: ["A", "B", "C", "D", "F"]
            }
        },
        {title: "Percentage above", field: "percentage_above", formatter: "money", visible: false, editor:"number", cssClass: "edit-mode", formatterParams: {precision: 0, symbol: "%", symbolAfter: true},
            editorParams: {
                min: 0,
                max: 100,
                step: 1,
            }
        },
    ]

    let final_extra_constructor_params = {
        "selectable": false, 
        "placeholder": "Grading rules loading...",
        "pagination": false,
        footerElement: "<div></div>",
    }
    
    let table = init_table("grading_rules_table", columns.map(
        col => {
            return {...col, editor: false, cssClass: ""}
        }
    ), data_json, final_extra_constructor_params)

    table.on("dataLoaded", function(data){
        let wrapper = table.getWrapper()
        let footer = wrapper.querySelector('.tabulator-footer-contents')
        let edit_button = document.createElement('button')
        let table_element = table.getElement()
        edit_button.innerHTML = "Edit Classification rules"
        edit_button.stored_width = table_element.style.width
        edit_button.addEventListener('click', function(){
            if (table_element.dataset.edit_mode == 1) {
                table.removeNotification()
                this.innerHTML = "Edit Classification rules"
                table_element.dataset.edit_mode = 0

                //increase the width of the table
                console.log(edit_button.stored_width)
                table_element.style.width = edit_button.stored_width

                table.setColumns(columns.map(col => {
                    return {...col, editor: false, cssClass: ""}
                }))
                let table_data = table.getData()
                if (JSON.stringify(table_data) === JSON.stringify(data_json)) {
                    console.log("no changes")
                } else {
                    console.log("changes")
                }
                //api call here to save the data.
                let posted_data = {}
                for (i = 1; i < table_data.length + 1; i++) {
                    posted_data[i] = table_data[i - 1]
                }
                api_post("save_grading_rules", posted_data).then(response => {
                    alert(response.status)
                })
            } else {
                table.addNotification()
                this.innerHTML = "Save changes"
                table_element.dataset.edit_mode = 1

                //decrease the width of the table
                console.log(edit_button.stored_width)
                // table_element.style.width = edit_button.stored_width
                table_element.style.width = "100%"

                table.setColumns(columns.map(col => {
                    return {...col, visible: true}
                }))
                table.getColumns().forEach(col => {
                    console.log(col.getElement())
                })
            }
        })
        footer.prepend(edit_button)
    })
}

function load_student_comments_table(data_json){

    let columns = [
        {title: "Comment", field: "comment", tooltip:true},
        {title: "Lecturer", field: "added_by", vertAlign:"middle"},
        {title: "Date added", field: "timestamp", vertAlign:"middle"},
        {title: "Comment ID", field: "id", visible: false, vertAlign:"middle"}
    ]

    let footer_element = 
        `<div style='display: flex; align-items: center; gap: 5px;'>
            <textarea type="text" id="comment_input" placeholder="Write your comment here.."></textarea>
            <button id="add_comment_button">Add comment</button>
        </div>`
    let final_extra_constructor_params = {
        "selectable": true,
        selectableCheck:function(row){
            //row - row component
            return row.getData().added_by == user_full_name; //allow selection of rows where the age is greater than 18
        },
        "pagination": false,
        "layout": "fitColumns",
        "footerElement": footer_element,
        "rowHeight": 30,
        "index": "id",
        rowContextMenu:[
            {
                label:"Delete comment",
                    action:function(e, row){
                        if(row.getData().added_by == user_full_name) {
                            if (confirm("Are you sure you want to delete this comment?")) {
                                api_post("delete_student_comment", row.getData().id).then(response => {
                                    if (response.data) {
                                        table.setData(response.data).then(function () {
                                            setTimeout(() => {alert(response.status)}, 10)
                                        })
                                    } else {
                                        alert(response.status)
                                    }
                                })
                            }
                        } else {
                            alert("You can only delete your own comments")
                        }
                    }
            },
        ],
    }
    
    let table = init_table("student_comments_table", columns, data_json, final_extra_constructor_params)
    table.on("tableBuilt", function(){
        let footer = table.getWrapper().querySelector('.tabulator-footer-contents')
        let add_comment_button = footer.querySelector('#add_comment_button')
        let comment_input = footer.querySelector('#comment_input')
        add_comment_button.addEventListener('click', function(){
            let comment = comment_input.value
            if (comment.length > 0) {
                api_post("add_student_comment", comment).then(response => {
                    if (response.data) {
                        table.setData(response.data).then(function () {
                            comment_input.value = ""
                            setTimeout(() => {alert(response.status)}, 10)
                        })
                    } else {
                        alert(response.status)
                    }
                })
            } else {
                alert("Please enter a non empty comment.")
            }
        })
    })
}