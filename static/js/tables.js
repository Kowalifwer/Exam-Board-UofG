//helper functions
const chart_colors = ["#115f9a", "#1984c5", "#22a7f0", "#48b5c4", "#76c68f", "#a6d75b", "#c9e52f", "#d0ee11", "#d0f400"]
const good_to_bad = ["#99FF99", "#CCFF99", "#FFFF99", "#FFFFCC", "#FFCC99", "#FF9999", "#FF6666", "#CC0000"]
const c_good = chart_colors[5]
const c_mid = good_to_bad[4]
const c_poor = good_to_bad[7]

const loading_spinner = `<div class="loading-animation"><div></div><div></div><div></div><div></div></div>`

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

const columnHeaderGroupBy = [
    {
        label:"Group rows by this column",
        action:function(e, column){
            let table = column.getTable()
            table.setGroupBy(column.getField());
            table.setGroupHeader(function(value, count, data, group) {
                return `<div class="tabulator-group-toggle">Grouped by '<span class="info-text">${column.getDefinition().title}</span>' column. Showing rows with value: '<span class="info-text">${value}</span>'   (<span class="success-text">${count} items</span>)</div>`
            }
        );
        },
    }
]


const moderation_formatter = function (cell) {
    let value = cell.getValue()
    //if value is 0 - return 'Not moderated'
    //if value is positive - return +value bands
    //if value is negative - return -value bands
    if (value == 0) {
        return "Not moderated"
    } else if (value > 0) {
        return "+" + value + " bands"
    } else {
        return value + " bands"
    }
}

const preponderance_formatter = function (cell) {
    let value = cell.getValue()
    let element = cell.getElement()
    if (element) {
        if (value == "N/A"){
            element.style.backgroundColor = good_to_bad[5]
            element.classList.add("preponderance")
            element.title = "Not applicable"
        } else if (value == "NA") {
            element.style.backgroundColor = good_to_bad[0]
            element.classList.add("preponderance")
            element.title = "No preponderance"
        } else if (value == "MV"){
            element.style.backgroundColor = chart_colors[1]
            element.classList.add("preponderance")
            element.title = "Medical void"
        } else if (value == "CW"){
            element.style.backgroundColor = good_to_bad[3]
            element.classList.add("preponderance")
            element.title = "Credit witheld"
        } else if (value == "CR"){
            element.style.backgroundColor = good_to_bad[6]
            element.classList.add("preponderance")
            element.title = "Credit refused"
        }
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

const bound_check = (value, lower_bound, upper_bound) => {
    if (value >= lower_bound && value < upper_bound)
        return true
    return false
}

//FORMATTERS
const formatter_to_band_letter = function(cell, formatterParams, onRendered){
    if (is_preponderance(cell)) {
        return preponderance_formatter(cell)
    }

    return boundary_map[Math.round(cell.getValue())]
}

const formatter_to_band_integer = function(cell, formatterParams, onRendered){
    if (is_preponderance(cell)) {
        return preponderance_formatter(cell)
    } 
    return parseFloat(cell.getValue()).toFixed(2)
}

const custom_average_calculator = function(values, data, calcParams){
    let total = 0;
    let count = 0;
    let credit_mode = false;
    let credit_accessor = "credits"
    let total_credits = 0;
    let credit_values = [];
    if (data[0]) {
        if (data[0].credits) {
            credit_mode = true;
        } else if (data[0].weighting) {
            credit_mode = true;
            credit_accessor = "weighting"
        }
    }
    
    let check_list = [...preponderance_list, "N/A", ""]
    if (credit_mode) {
        for (let i = 0; i < data.length; i++) {
            let row = data[i];
            if (row[credit_accessor]) {
                total_credits += row[credit_accessor];
                credit_values.push(row[credit_accessor]);
            }
        }
    }

    for (let i = 0; i < values.length; i++) {
        if (!check_list.includes(values[i])) {
            total += (credit_mode && credit_values[i]) ? parseInt(values[i]) * credit_values[i]: parseInt(values[i]);
            count++;
        } else { // if the value is N/A or MV, then we need to subtract the credit value from the total
            total_credits -= credit_values[i];
            credit_values[i] = 0;
        }
    }

    if (count) {
        return (credit_mode) ? (total/total_credits).toFixed(2) : (total / count).toFixed(2);
    } else {
        return "N/A";
    }
}

const default_formatter = formatter_to_band_integer

//this function can be used to create instantiate a Tabulator table, with various settings and parameters
// table_id - can be an ID of a table element, or a DOM element directly
// columns - an array of column definitions, for the table. See https://tabulator.info/docs/5.4/columns
// prefil_data - OPTIONAL PARAMETER: you can provide the data to be loaded into the table. 
// Alternatively, leaving this blank will cause the table to fetch data from the server.
// note that by default, perfil_data fetches data from the url of page current page that you are on.
// extra_constructor_params - OPTIONAL PARAMETER: you can provide extra parameters to pass to the Tabulator constructor. These parameters will be merged with the default parameters.
// settings - OPTIONAL PARAMETER: these settings are used to configure the table, and are not passed to the Tabulator constructor. Generally used to store things like the title of the table, some metadata, as well as header configurations.
function init_table(table_id, columns, prefil_data = null, extra_constructor_params = {}, settings={}) {
    let title = ""
    if (settings.title)
        title = settings.title

    let table_constructor = {
        columns: columns,
        pagination: true,
        paginationMode: "local", //all data will be loaded at once, and then paginated locally
        columnHeaderVertAlign:"middle", //center column headers vertically

        selectable:true, //make table ROWS selectable
        rowHeight: 30,
        groupToggleElement: "header", //toggle ROW groups by clicking header

        autoResize: false, 

        placeholder: "Table is empty", //placeholder when no data in the table

        paginationSize: 100, //number of rows to display per page by default
        paginationSizeSelector:[50, 100, 250, 500, 1000], //allow user to select number of rows to be shown per page

        layout: "fitDataFill", //"fitColumns", //fitDataStretch //fitDataFill

        movableColumns: true, //allow user to move columns around

        dataLoaderLoading:`<span>Loading ${title} table data</span>`, //message that is displayed when data loading into table (usually from ajax request)

        //config for table download
        downloadConfig:{
            columnHeaders:true, //do not include column headers in downloaded table
            columnGroups:true, //do not include column groups in column headers for downloaded table
            rowGroups:false, //do not include row groups in downloaded table
            columnCalcs:false, //do not include column calcs in downloaded table
        },
        rowContextMenu: [], //intialize right-click row actions to be empty
    }

    if (settings.fitColumns) {
        table_constructor.layout = "fitColumns"
    }

    if (prefil_data){ //if we are pre-filling the table with data, then we don't need to fetch data from the server
        table_constructor.data = prefil_data
    } else { //otherwise, we need to fetch data from the server
        table_constructor.ajaxURL = window.location.href
        if (settings.api_table_fetch) { //if api_table_fetch is passed in settings, then we fetch data from the api_table endpoint (not current url)
            table_constructor.ajaxURL = `http://localhost:8000/api/table/${settings.api_table_fetch}/`  
        }
        console.log("fetching data from " + table_constructor.ajaxURL)

        table_constructor.ajaxParams = {
            "fetch_table_data": true, //this is a flag that the server uses to determine if it should return table data
        }
        table_constructor.ajaxConfig = "GET"
        table_constructor.ajaxResponse = function(url, params, response) {
            if (typeof response.extra_cols !== 'undefined') { //if the server returns extra columns (not defined locally in the columns parameter), then we add them to the table
                table.extra_cols = response.extra_cols
                table.dispatchEvent("dataFetchedFromServer")
                return response.data
            } else { //otherwise, we just return the data
                table.dispatchEvent("dataFetchedFromServer")
                return response
            }
        }
    }

    table_constructor = {...table_constructor, ...extra_constructor_params} //merge the settings with the table constructor

    if (!settings.no_multirow) { //determine if we add multi-row actions to the table (such as hiding or deleting rows)
        table_constructor.rowContextMenu.push({
            separator: true //add a separator before we add the multi-row actions
        })
        table_constructor.rowContextMenu.push({
            label:"<div class='inline-icon' title='The following actions will affect all the selected rows. Note that all the actions in this category are reversible - so do not worry if you accidentally click something.'><img class='color-icon-theme' src='/static/icons/info.svg'></i><span>Multi-row actions</span></div>",
            menu:[
                { //hide rows action
                    label:"<div class='inline-icon' title='Note that this is simply hiding the rows, meaning no table data gets manipulated.'><img class='color-icon-theme' src='/static/icons/info.svg'></i><span>Hide row(s)</span></div>",
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
                { //delete rows action
                    label:"<div class='inline-icon' title='Note that this action properly removes data from the table (locally, and not from the database), - this can be useful for preparing the table for data extraction, such as generating an excel file, for example.'><img class='color-icon-theme' src='/static/icons/info.svg'></i><span>Delete row(s)</span></div>",
                    action:function(e, row){
                        let selected_rows = table.getSelectedRows()
                        selected_rows.forEach(function(inner_row){
                            table.deleted_rows.push(inner_row.getData()) //keep track of the deleted rows
                            inner_row.delete()
                        })
                        if (table.deleted_rows) {
                            document.getElementById('undelete-rows').classList.remove('hidden')
                        }
                    }
                },
            ]
        })    
    }

    let table_element = (isElement(table_id)) ? table_id : document.getElementById(table_id)
    table_element.dataset.edit_mode = 0
    let table = new Tabulator(table_element, table_constructor)
    if (prefil_data) {
        setTimeout(function(){ //we need to wait a bit before we dispatch the event, otherwise the event listener might not be attached yet
            table.dispatchEvent("dataFetchedFromServer")
        }, 10)
    }
    
    //attaching some extra properties and methods to the table object
    table.settings = settings
    table.extra_cols = []
    table.hidden_rows = []
    table.deleted_rows = []

    //this creates a table notification, which is more noticeable than a table heading. It is displayed at the top of the table
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

    //this creates a table heading, which is a message that is displayed at the top of the table
    table.heading = null
    table.setHeading = function(message) {
        let heading = document.createElement('div')
        heading.classList.add('tabulator-heading')
        heading.innerHTML = message
        table.heading = heading
    }

    table.dataFullyLoaded = false

    table.getElement = () => table_element //returns table DOM element

    //reformats the table, and applies a formatter to all the cells in the table that have a provided cssClass.
    table.reformatTable = function(formatter=null, cssClass=null, new_bottom_calc_function=null) {
        let existing_cols = new Set()
        for (let col of table.getColumns()) {
            let parent_col = col.getParentColumn()
            if (parent_col) {
                existing_cols.add(parent_col.getDefinition())
            } else {
                existing_cols.add(col.getDefinition())
            }
        }
        const downloadFormatter = function(value, data, type, params, column){ //this function ensures that the downloaded table data is also formatted the same way as the table.
            //formatters take cells with various expected methods and attributes. We have to convert our value into a cell object, so that the formatter can work with it.
            return formatter({
                getValue: () => value,
                getElement: () => null,
            })
        }

        const handle_column_formatting = (col) => {
            if (col.cssClass && col.cssClass.includes(cssClass)) {
                if (formatter) { //if we have a formatter, we add it to the column
                    col.formatter = formatter
                    col.accessorDownload = downloadFormatter
                    if (new_bottom_calc_function) { //if we have a bottom calc function, we add it and apply the formatter to it as well
                        col.bottomCalc = new_bottom_calc_function
                        col.bottomCalcFormatter = formatter
                    }
                }
                else
                    delete col.formatter
            }
        }

        for (let col of existing_cols) { //handles all columns - including nested columns
            if (col.columns) {
                for (let j = 0; j < col.columns.length; j++) {
                    let col_inner = col.columns[j]
                    handle_column_formatting(col_inner)
                }
            } else {
                handle_column_formatting(col)
            }
        }
        table.setColumns(existing_cols)
        table.dataFullyLoaded = true
    }

    let wrapper = wrap(table_element, document.createElement('div'))
    wrapper.classList.add('tabulator-wrapper')
    table.getWrapper = () => wrapper

    table.on("dataFetchedFromServer", function(){
        for (let i = 0; i < table.extra_cols.length; i++){ //add extra columns, if any were added from the server.
            table.addColumn(table.extra_cols[i])
        }
        let table_wrapper = table.getWrapper()
        if (!table.settings.no_components) {
            let table_components = document.createElement('div')
            table_components.classList.add('tabulator-components')
            wrapper.prepend(table_components)

            if (table.heading)
                wrapper.prepend(table.heading)

            table.reformatTable(default_formatter, "format_grade", custom_average_calculator) //format the table gradesr

            let select_element = string_to_html_element(
                `
                    <select>
                        <option selected="selected" disabled="disabled">grade format</option>
                        <option value="I">band integer</option>
                        <option value="B">band letter</option>
                    </select>
                `
            )
            select_element.classList.add('tabulator-format-select')

            let select_download = string_to_html_element(
                `
                    <select>
                        <option value=0 selected="selected" disabled="disabled">export table</option>
                        <option value="xlsx">Excel</option>
                        <option value="pdf">PDF</option>
                        <option value="csv">CSV</option>
                        <option value="json">JSON</option>
                    </select>
                `
            )

            select_element.addEventListener("change", function(e){
                if (this.value == "B") {
                    table.reformatTable(formatter_to_band_letter, "format_grade", custom_average_calculator)
                } else if (this.value == "I") {
                    table.reformatTable(formatter_to_band_integer, "format_grade", custom_average_calculator)
                }
            })

            select_download.addEventListener("change", function(e){
                if (this.value == "xlsx") {
                    table.download("xlsx", "data.xlsx", {});
                    this.value = 0
                } else if (this.value == "pdf") {
                    table.downloadToTab("pdf", "data.pdf", {
                        orientation:"landscape", //set page orientation to landscape
                    });
                    this.value = 0
                } else if (this.value == "csv") {
                    table.download("csv", "data.csv", {});
                    this.value = 0
                } else if (this.value == "json") {
                    table.download("json", "data.json", {});
                    this.value = 0
                }   
            })

            let unhide_rows = string_to_html_element(`<button id="unhide-rows" class="hidden">Unhide rows</button>`)
            let undelete_rows = string_to_html_element(`<button id="undelete-rows" class="hidden">Add back deleted rows</button>`)
            let column_manager = string_to_html_element(`<button class="column-manager">column manager</button>`)
            let help_button = string_to_html_element(`<button class="help-button">help</button>`)
            let remove_row_groups = string_to_html_element(`<button class="remove-row-groups">remove row groups</button>`)

            remove_row_groups.addEventListener("click", function(){
                table.setGroupBy([])
            })

            help_button.addEventListener("click", function(){
                let help_points = [
                    "<b>Sort columns:</b> Click on a column header to sort the table by that column. (Ascending or descending order is determined by the arrow next to the column header). Click again to change the order.",
                    "<b>Rearrange column order:</b> Click on a column header and drag it to the left or right to move it. This way you can reorder the columns to your liking.",
                    "<b>Resize columns:</b> Resize a column by dragging the left/right edge of the column",
                    "<b>Row actions:</b> Right-click on a row, to get a menu with options relevant to that object. Non-multirow actions will be executed only on the clicked row. Multirow actions will be executed on all selected rows.",
                    "<b>Show/hide columns:</b> Click on the 'Column manager' button to manage what columns will be shown/hidden",
                    "<b>Download table data:</b> Tables can be exported to Excel, PDF, CSV, and JSON. Click on the 'export table' button to export the table to one of these formats. Note that the export will be formatted according to the state of the table (accounting for hidden columns, grade format and deleted rows). 'pdf' exports are not advisable for tables with many columns.",
                    "<b>Format grades:</b> Tables can be reformatted to show grades as band letters or band integers. Click on the 'grade format' button to change the formatting of the table.",
                    "<b>Search for rows:</b> Some column headers have a text input box. Type in the box to search for rows that contain the text you typed.",
                    "<b>Group rows by column:</b> Some column headers have 3 vertical dots. Clicking the dots will open a menu that allows you to group the table rows by that column. Note that most tables load pre-grouped, but you are free to regroup however you wish.",
                    "<b>Remove all row groups:</b> Click on the 'Remove all row groups' button to remove all row groups.",
                ]
                create_notification("Table help", bullet_list_to_html_string(help_points), "info", 20000)
            })

            column_manager.addEventListener("click", function(){
                var columns = table.getColumns();
                var menu_container = document.createElement("div");
                menu_container.classList = "tabulator-columns-menu";

                //add title to menu
                var title = document.createElement("h3");
                title.textContent = "Column manager";
                menu_container.appendChild(title);

                let current_parent = null
                for (let column of columns){
                    if (!column.getDefinition().title || column.getDefinition().title == "hidden" || column.getDefinition().formatter == "rowSelection")
                        continue

                    let parent_column = column.getParentColumn()
                    let parent_title = document.createElement("p")
                    parent_title.textContent = ""
                    if (parent_column && parent_column != current_parent) {
                        parent_title.textContent = parent_column.getDefinition().title
                        menu_container.appendChild(parent_title)
                        current_parent = parent_column
                    } else if (!parent_column && current_parent) {
                        menu_container.appendChild(parent_title)
                        current_parent = null
                    }

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


            table_wrapper.querySelector(".tabulator-components").prepend(select_element)
            table_wrapper.querySelector(".tabulator-components").prepend(select_download)
            table_wrapper.querySelector(".tabulator-components").appendChild(column_manager)
            if (table_constructor.groupBy && table_constructor.groupBy.length > 0)
                table_wrapper.querySelector(".tabulator-components").appendChild(remove_row_groups)

            table_wrapper.querySelector(".tabulator-components").appendChild(help_button)

            table_wrapper.querySelector(".tabulator-components").appendChild(unhide_rows)
            table_wrapper.querySelector(".tabulator-components").appendChild(undelete_rows)
        }

        if (settings.course) {
            let moderate_course_button = string_to_html_element(`<button class="tabulator-moderate">moderate course</button>`)
            moderate_course_button.addEventListener("click", function(e){
                render_course_moderation_section(settings.course, table)
            })
            table_wrapper.querySelector(".tabulator-components").appendChild(moderate_course_button)
        }
    })

    table.on("dataProcessed", function(){
        if (table.dataFullyLoaded) {
            table.reloadCharts()
            table.reloadContent()
            document.querySelectorAll(".loading-animation").forEach(function(select){
                select.classList.add("hidden")
            })
        }
    })

    table.setReloadFunction = (reload_function, reload_function_parameter_list) => {
        table.reload_function = reload_function
        table.reload_function_parameter_list = reload_function_parameter_list
    }

    table.charts = []
    table.chart_links = []
    table.content_links = []

    table.addChartLink = function(chart_link){
        table.chart_links.push(chart_link)
    }

    table.addContentLink = function(content_link){
        table.content_links.push(content_link)
    }

    table.destroyCharts = function(){
        for (var chart of table.charts) {
            chart.destroy()
        }
    }

    table.destroyContent = function(){
        for (var content of table.content_links) {
            content[0].innerHTML = ""
            content[0].appendChild(string_to_html_element(loading_spinner))
        }
    }

    table.reloadTable = (message=null) => {
        console.log("Reloading table")
        table.destroyCharts()
        table.destroyContent()

        document.querySelectorAll(".loading-animation").forEach(function(select){
            select.classList.remove("hidden")
        })
        
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

    table.reloadCharts = function(){
        for (var link_data of table.chart_links) {
            //link_data[1] is a function that returns the chart setup. We pass it through defaultChartSetup to add some default settings.
            let chart = new Chart(link_data[0], defaultChartSetup(link_data[1](table), table))
            
            table.charts.push(chart)
        }
    }

    table.reloadContent = function(){
        for (var link_data of table.content_links) {
            let linked_element = link_data[0]
            linked_element.innerHTML = link_data[1](table)
        }
    }

    return table
}

//define various table setups below

function load_students_table(extra_constructor_params = {}, extra_cols=true, settings={'title': 'Students'}){
    let columns = [
        {title:"Row selector", formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false, frozen:true, download:false, maxWidth: 25, hozAlign: "center"},
        {title: "GUID", field: "GUID", headerFilter: "input", frozen:true},
        {title: "Full name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            columns: [
                {title: "Title", field: "degree_title", headerMenu: columnHeaderGroupBy},
                {title: "Name", field: "degree_name"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
                {title: "Faster route?", field: "is_faster_route", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
            ],
            "headerHozAlign": "center",
        },
        {
            title: "Study year data",
            columns: [
                {title: "Currently active?", field: "is_active", headerMenu: columnHeaderGroupBy, formatter: "tickCross"},
                {title: "Current level", field: "current_level", headerMenu: columnHeaderGroupBy},
                {title: "Start year", field: "start_year", headerMenu: columnHeaderGroupBy},
                {title: "End year", field: "end_year", headerMenu: columnHeaderGroupBy},
            ],
            "headerHozAlign": "center",
        },
        {title: "hidden", field: "count", bottomCalc: "count", visible: false},
    ]

    let ajaxParams = {
        "fetch_table_data": true,
        "students": true,
    }

    let rowContextMenu = [
        {
            label:"View Student page",
                action:function(e, row){
                    if (typeof row.getData().page_url !== 'undefined') {
                        window.location.href = row.getData().page_url
                    }
                }
        },
    ]
    if (settings.course) {
        rowContextMenu.push({
            label:"<div class='inline-icon' title='This action will create a popup where you can see the student grades for all the assessed content for this course. Additionally, you may view and edit the preponderances here.'><img class='color-icon-theme' src='/static/icons/info.svg'></i><span>Student grades and preponderance(popup)</span></div>",
            action: function(e, row){
                create_student_course_detailed_table_popup(row.getData(), settings.course.course_id, row.getTable())
            }
        }) 
    }

    let final_extra_constructor_params = { ...extra_constructor_params,
        ajaxParams: ajaxParams,
        rowContextMenu:rowContextMenu,
        initialSort: [{column: 'current_level', dir: 'dsc'}],
        placeholder: "Student data loading...",
    }

    if (!settings.noGroupBy) {
        final_extra_constructor_params.groupBy = "current_level"
    }

    let table = init_table("students_table", columns, settings.prefillData, final_extra_constructor_params, settings={...settings, ...{title: "Students"}})

    table.setReloadFunction(load_students_table, [extra_constructor_params, extra_cols, settings])

    if (!settings.noGroupBy) {
        table.on("tableBuilt", function() {
            table.setGroupHeader(function(value, count, data, group){
                return `Number of <span class='info-text'>${value}</span> students: <span class='success-text'>${count}</span>`; //return the header contents
            });
        })
    }

    if (settings.course) {
        table.addContentLink([
            document.querySelector(".course-page-extra-info"),
            function(table) {
                let table_data = table.getData()
                let passed_students = 0
                let failed_students = 0
                let average_final_grade = 0
                let average_coursework_grade = 0
                let average_group_grade = 0
                let average_ind_grade = 0
                let average_exam_grade = 0
                let n_rows = table_data.length
                for (let i = 0; i < n_rows; i++) {
                    let student = table_data[i]
                    if (student.final_grade && student.final_grade >= 11.5) {
                        passed_students += 1
                    } else {
                        failed_students += 1
                    }
                }
                let group_results = table.getCalcResults()
                
                for (group in group_results) {
                    let group_data = group_results[group]
                    average_final_grade += group_data.bottom.final_grade * group_data.bottom.count
                    average_coursework_grade += group_data.bottom.C_grade * group_data.bottom.count
                    average_group_grade += group_data.bottom.G_grade * group_data.bottom.count
                    average_ind_grade += group_data.bottom.I_grade * group_data.bottom.count
                    average_exam_grade += group_data.bottom.E_grade * group_data.bottom.count
                }
                //final, coursework, group, ind, exam
                let averages = [(average_final_grade / n_rows).toFixed(1), (average_coursework_grade / n_rows).toFixed(1), (average_group_grade / n_rows).toFixed(1), (average_ind_grade / n_rows).toFixed(1), (average_exam_grade / n_rows).toFixed(1)]
                let averages_text = ["Final", "Coursework", "Group Project", "Individual Project", "Exam"]
                let grades_breakdown_string = ""
                for (let i = 0; i < averages.length; i++) {
                    if (averages[i] != "NaN")
                        grades_breakdown_string += `<p><b>Average ${averages_text[i]} GPA:</b> ${averages[i]} - ${boundary_map[Math.round(averages[i])]}</p>`
                }

                return `
                    ${grades_breakdown_string}
                    <p><b>Number of students above pass grade (above E1):</b> ${passed_students} (${(passed_students/ n_rows * 100).toFixed(2)}%)</p>
                    <p><b>Number of students below pass grade (below D3):</b> ${failed_students} (${(failed_students/ n_rows * 100).toFixed(2)}%)</p>
                `
            }
        ])
    }

    if (document.getElementById("students_final_grade")) {
        table.addChartLink([
            document.getElementById("students_final_grade"), function(table_inner) {
                let table_data = table_inner.getData()
                let chart_data = {};
                let boundaries = ["A","B","C","D","E","F","G","H", "MV"]
                for (let x in boundaries) {
                    chart_data[boundaries[x]] = 0
                }
                table_data.forEach(function(row){
                    let band_grade = (row.final_grade == "MV") ? "MV" : boundary_map[Math.round(row.final_grade)][0]
                    chart_data[band_grade] = (chart_data[band_grade] || 0) + 1;
                })

                //make abc grades pleasant green color, d grade yellow, and e f g h red
                let colors = [c_good,c_good,c_good,c_mid,c_poor,c_poor,c_poor,c_poor, chart_colors[1]]

                return {
                    data: {
                        labels: Object.values(boundaries),
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
                        y_title: "Number of students",
                        x_title: "Final grade for course",
                        tooltip_extra: "Percentage of students: ",
                        tooltip_extra_data_size: table_data.length,
                        legend_display: false,
                        title: "Final grade distribution for course",
                    }
                }
            }
        ])
    }
}

function load_level_progression_table(level){
    level = parseInt(level)
    if(![1,2,3,4,5].includes(level)) {
        console.error("Invalid level passed to load_level_progression_table function")
        return
    }

    let columns = [
        {title: "Row selector", formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false, frozen:true, download:false, maxWidth: 25, hozAlign: "center"},
        {title: "GUID", field: "GUID", headerFilter: "input", frozen: true},
        {title: "Full name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            columns: [
                {title: "Title", field: "degree_title"},
                {title: "Name", field: "degree_name"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
                {title: "Faster route?", field: "is_faster_route", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
            ],
            headerHozAlign: "center",
        },
        {
            title: "Study year data",
            columns: [
                {title: "Currently active?", field: "is_active", headerMenu: columnHeaderGroupBy, formatter: "tickCross"},
                {title: "Current level", field: "current_level", headerMenu: columnHeaderGroupBy},
                {title: "Start year", field: "start_year", headerMenu: columnHeaderGroupBy},
                {title: "End year", field: "end_year", headerMenu: columnHeaderGroupBy},
            ],
            headerHozAlign: "center",
        },
        {
            title: `Level ${level} final results`,
            columns: [
                {title: `L${level} GPA`, field: "final_gpa"},
                {title: `L${level} band`, field: "final_band"},
            ],
            headerHozAlign: "center",
        },
        {
            title: `Cumulative number of level ${level} credits graded at band`,
            columns: [
                {title: "Total", field: "n_credits", headerMenu: columnHeaderGroupBy},
                {title: "> A", field: "greater_than_a"},
                {title: "> B", field: "greater_than_b"},
                {title: "> C", field: "greater_than_c"},
                {title: "> D", field: "greater_than_d"},
                {title: "> E", field: "greater_than_e"},
                {title: "> F", field: "greater_than_f"},
                {title: "> G", field: "greater_than_g"},
                {title: "> H", field: "greater_than_h"},
            ],
            "headerHozAlign": "center",
        },
    ]

    let table = init_table("level_progression_table", columns, null, {
        rowContextMenu: [{
            label:"View Student page",
                action:function(e, row){
                    if (typeof row.getData().page_url !== 'undefined') {
                        window.location.href = row.getData().page_url
                    }
                } 
        }],
        "ajaxParams": {
            "fetch_table_data": true,
        },
        groupBy: "progress_to_next_level",

        groupHeader: function(value, count, data, group){
            let message = ""
            if (value == "Discretionary") {
                message = `Students who <span class="warning-text">might progress</span> at schools discretion (${count})`
            } else if (value == "No") {
                message = `Students who <span class="error-text">will not</span> progress (${count})`
            } else if (value == "Guaranteed") {
                message = `Students who are <span class="success-text">guaranteed</span> to progress (${count})`
            }
            return message
        },
    }, {'title': 'Degree classification data for level '+level+' students'})

    //on data loeaded, sort by final_gpa
    table.on("dataProcessed", function(){
        if (table.dataFullyLoaded)
            table.setSort('final_gpa', 'dsc')
    })

    table.addChartLink([document.getElementById("level_progression_chart_success"), function(table_inner) {
        let table_data = table_inner.getData()
        let classes = ["Guaranteed", "Discretionary", "No"]
        let colors = [c_good,c_mid,c_poor]
        let chart_data = []
        for (let x in classes) {
            chart_data[classes[x]] = 0
        }
        table_data.forEach(function(row){
            chart_data[row.progress_to_next_level] = (chart_data[row.progress_to_next_level] || 0) + 1;
        })
        return {
            data: {
                labels: classes,
                datasets: [
                    {
                        label: "Progression?",
                        data: Object.values(chart_data),
                        backgroundColor: colors,
                    }
                ]
            },
            extra_settings: {
                x_title: "Progression to level "+ (level + 1),
                y_title: "Number of students",
                tooltip_extra: "Percentage of cohort: ",
                tooltip_extra_data_size: table_data.length,
                legend_display: false,
            }
        }
    }])

    table.addChartLink([document.getElementById("level_progression_chart_all"), function(table_inner) {
        let table_data = table_inner.getData()
        let bands = ["A", "B", "C", "D", "E", "F", "G"]
        let colors = [c_good,c_good,c_good,c_mid,c_poor,c_poor,c_poor]
        let chart_data = {}

        for (let x in bands) {
            chart_data[bands[x]] = {
                "final_band": 0,
            }
        }

        for (let i = 0; i < table_data.length; i++) {
            let row = table_data[i]
            let band_letter = row.final_band[0]
            chart_data[band_letter].final_band = (chart_data[band_letter].final_band || 0) + 1;
        }

        return {
            data: {
                labels: bands,
                datasets: [
                    {
                        label: "GPA band",
                        data: Object.values(chart_data).map(x => x.final_band),
                        backgroundColor: colors,
                    }
                ]
            },
            extra_settings: {
                x_title: "Level "+ level +" GPA",
                y_title: "Number of students",
                tooltip_extra: "Percentage of cohort: ",
                tooltip_extra_data_size: table_data.length,
                legend_display: false,
            }
        }
    }])

    table.addContentLink([document.querySelector(".tabulator-linked-section"), function(table_inner) {
        let table_data = table_inner.getData()
        let passed_students = 0
        let discretionary = 0
        let failed_students = 0
        let n_rows = table_data.length
        let final_gpa_avg = 0
        let final_gpa_count = 0

        for (let i = 0; i < n_rows; i++) {
            let student = table_data[i]
            if (student.progress_to_next_level == "Guaranteed") {
                passed_students++
            } else if (student.progress_to_next_level == "Discretionary") {
                discretionary++
            } else if (student.progress_to_next_level == "No") {
                failed_students++
            }
            if (student.final_gpa != null) {
                final_gpa_avg += student.final_gpa
                final_gpa_count++
            }
        }

        return `
            <p><b>Total number of students:</b> ${n_rows}</p>
            <p><b>Average level ${level} GPA:</b> ${(final_gpa_avg/final_gpa_count).toFixed(1)} - (${boundary_map[(final_gpa_avg/final_gpa_count).toFixed(0)]})</p>
            <p><b>Number of students guaranteed to progress:</b> ${passed_students} (${(passed_students/ n_rows * 100).toFixed(2)}%)</p>
            <p><b>Number of students who might progress at schools discretion:</b> ${discretionary} (${(discretionary/ n_rows * 100).toFixed(2)}%)</p>
            <p><b>Number of students who will not progress:</b> ${failed_students} (${(failed_students/ n_rows * 100).toFixed(2)}%)</p>
        `
    }])

}
    

function load_degree_classification_table(level) {
    level = parseInt(level)
    if(![4,5].includes(level)) {
        console.error("Invalid level passed to load_degree_classification_table function")
        return
    }

    let columns = [
        {title: "Row selector", formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false, frozen:true, download:false, maxWidth: 25, hozAlign: "center"},
        {title: "GUID", field: "GUID", headerFilter: "input", "frozen": true},
        {title: "Full name", field: "name", headerFilter: "input"},
        {
            title: "Degree info",
            columns: [
                {title: "Title", field: "degree_title", headerMenu: columnHeaderGroupBy},
                {title: "Name", field: "degree_name"},
                {title: "Masters?", field: "is_masters", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
                {title: "Faster route?", field: "is_faster_route", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
            ],
            "headerHozAlign": "center",
        },
        {
            title: "Year data",
            columns: [
                {title: "Current level", field: "current_level", headerMenu: columnHeaderGroupBy},
                {title: "Start year", field: "start_year", headerMenu: columnHeaderGroupBy},
                {title: "End year", field: "end_year", headerMenu: columnHeaderGroupBy},
            ],
            "headerHozAlign": "center",
        },
        {title: "Degree classification", field: "class", headerMenu: columnHeaderGroupBy},
        {title: "Final band", field: "final_band"},
        {title: "Final GPA", field: "final_gpa", bottomCalc: custom_average_calculator},
        {title: "L5 band", field: "l5_band"},
        {title: "L5 GPA", field: "l5_gpa", bottomCalc: custom_average_calculator},
        {title: "L4 band", field: "l4_band"},
        {title: "L4 GPA", field: "l4_gpa", bottomCalc: custom_average_calculator},
        {title: "L3 band", field: "l3_band"},
        {title: "L3 GPA", field: "l3_gpa", bottomCalc: custom_average_calculator},
        {
            title: `Cumulative number of level ${level} credits graded at band`,
            columns: [
                {title: "Total", field: "n_credits"},
                {title: "> A", field: "greater_than_a"},
                {title: "> B", field: "greater_than_b"},
                {title: "> C", field: "greater_than_c"},
                {title: "> D", field: "greater_than_d"},
                {title: "> E", field: "greater_than_e"},
                {title: "> F", field: "greater_than_f"},
                {title: "> G", field: "greater_than_g"},
                {title: "> H", field: "greater_than_h"},
            ],
            "headerHozAlign": "center",
        },
        {title: "Team (lvl 3)", field: "team", bottomCalc: custom_average_calculator},
        {title: "Individual (lvl 4)", field: "project", bottomCalc: custom_average_calculator},
        {title: "Individual (lvl 5)", field: "project_masters", bottomCalc: custom_average_calculator},
    ]

    if (level != 5) {
        //remove the l5 columns from the table
        for (let i = 0; i < columns.length; i++) {
            if (["l5_band", "l5_gpa", "project_masters"].includes(columns[i].field)) {
                columns.splice(i, 1);
                i--;
            }
        }
    }

    let table = init_table("degree_classification_table", columns, null, {
        rowContextMenu: [{
            label:"View Student page",
                action:function(e, row){
                    if (typeof row.getData().page_url !== 'undefined') {
                        window.location.href = row.getData().page_url
                    }
                } 
        }],
        "ajaxParams": {
            "fetch_table_data": true,
        },
    }, {'title': 'Degree classification data for level '+level+' students'})

    //on data loeaded, sort by final_gpa
    table.on("dataProcessed", function(){
        if (table.dataFullyLoaded)
            table.setSort([
                {column: "final_gpa", dir: "dsc"},
                {column: "class", dir: "asc"},
            ])
    })

    table.addChartLink([document.getElementById("degree_classification_chart_class"), function(table_inner) {
        let table_data = table_inner.getData()
        let classes = ["1st", "2:1", "2:2", "3rd", "Fail"]
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
                        label: "Degree classification",
                        data: Object.values(chart_data),
                        backgroundColor: [c_good, c_good, c_good, c_mid, c_poor],
                    }
                ]
            },
            extra_settings: {
                y_title: "Number of students",
                x_title: "Degree classification",
                tooltip_extra: "Percentage of cohort: ",
                tooltip_extra_data_size: table_data.length,
                legend_display: false,
            }
        }
    }])

    table.addChartLink([document.getElementById("degree_classification_chart_all"), function(table_inner) {
        let table_data = table_inner.getData()
        let bands = ["A", "B", "C", "D", "E", "F", "G"]
        let chart_data = {}

        let inits = (level == 5) ? [
            ["final_band", "Final band"],
            ["l5_band", "L5 band"],
            ["l4_band", "L4 band"],
            ["l3_band", "L3 band"],
            ["team", "Team (lvl 3)"],
            ["project", "Individual (lvl 4)"],
            ["project_masters", "Individual (lvl 5)"],
        ] : [
            ["final_band", "Final band"],
            ["l4_band", "L4 band"],
            ["l3_band", "L3 band"],
            ["team", "Team (lvl 3)"],
            ["project", "Individual (lvl 4)"],
        ]
        for (let x in bands) {
            chart_data[bands[x]] = {};
        }

        for (let i = 0; i < table_data.length; i++) {
            let row = table_data[i]
            for (let j = 0; j < inits.length; j++) {
                let key = inits[j][0]
                let band_letter = row[key]
                if (typeof band_letter != "string") {
                    //band letter is actually a number, must be converted to a string band
                    band_letter = boundary_map[band_letter.toFixed(0)][0]
                } else {
                    band_letter = row[key][0]
                }
                chart_data[band_letter][key] = (chart_data[band_letter][key] || 0) + 1;
            }
        }

        return {
            data: {
                labels: bands,
                datasets: inits.map((tuple, i) => {
                    return {
                        label: tuple[1],
                        data: Object.values(chart_data).map(x => x[tuple[0]]),
                        backgroundColor: chart_colors[i],
                        hidden: (i > 0),
                    }
                })
            },
            extra_settings: {
                y_title: "Number of students",
                x_title: "Band",
                tooltip_extra: "Percentage of cohort: ",
                tooltip_extra_data_size: table_data.length,
                legend_display: true,
            }
        }
    }])

    table.addContentLink([
        document.querySelector(".tabulator-linked-section"), 
        function(table) {
            let table_data = table.getData()

            let inits = (level == 5) ? [
                ["final_gpa", "Average final GPA"],
                ["l5_gpa", "Average L5 GPA"],
                ["project_masters", "Average L5 individual project(M) GPA"],
                ["l4_gpa", "Average L4 GPA"],
                ["project", "Average L4 individual project GPA"],
                ["l3_gpa", "Average L3 GPA"],
                ["team", "Average L3 team project GPA"],
            ] : [
                ["final_gpa", "Average final GPA"],
                ["l4_gpa", "Average L4 GPA"],
                ["project", "Average L4 individual project GPA"],
                ["l3_gpa", "Average L3 GPA"],
                ["team", "Average L3 team project GPA"],
            ]

            let passed_students = 0
            let failed_students = 0
            let n_rows = table_data.length

            for (let i = 0; i < n_rows; i++) {
                let student = table_data[i]
                if (student.class != "Fail") {
                    passed_students += 1
                } else {
                    failed_students += 1
                }
            }

            let group_results = table.getCalcResults().bottom
            for (let i = 0; i < inits.length; i++) {
                let field_name = inits[i][0]
                inits[i].push(parseFloat(group_results[field_name]))
            }

            //final, coursework, group, ind, exam
            let grades_breakdown_string = ""
            for (let i = 0; i < inits.length; i++) {
                //inits[i][1] is the label
                //inits[i][2] is the value (average)
                grades_breakdown_string += `<p><b>${inits[i][1]}:</b> ${inits[i][2].toFixed(1)} - ${boundary_map[inits[i][2].toFixed(0)]}</p>`
            }

            return `
                <p><b>Total number of students:</b> ${n_rows}</p>
                ${grades_breakdown_string}
                <p><b>Number of students graduated succesfully:</b> ${passed_students} (${(passed_students/ n_rows * 100).toFixed(2)}%)</p>
                <p><b>Number of students failed to graduate:</b> ${failed_students} (${(failed_students/ n_rows * 100).toFixed(2)}%)</p>
            `
        }
    ])
}

function create_student_course_detailed_table_popup(student_data=null, course_id=null, parent_table_to_reload=null){
    if (student_data?.GUID && course_id) {
        let columns = [
            {title: "Assessment type", field: "type"},
            {title: "Assessment name", field: "name"},
            {title: "Weighting", field: "weighting", bottomCalc: "sum", formatter: "money", formatterParams: {precision: 0, symbol: "%", symbolAfter: true}},
            {title: "Grade", field: "grade", cssClass: "format_grade"},
            {title: "Moderation", field: "moderation", formatter: moderation_formatter},
            {title: "Preponderance", field: "preponderance", cssClass: "edit-mode", formatter: preponderance_formatter, editor: "list", editorParams: {
                values: preponderance_list
            }},
            {title: "AssessmentResult ID", field: "result_id", visible: false},
        ]
    
        let ajaxParams = {
            "fetch_table_data": true,
            "students": true,
            "student_GUID": student_data.GUID,
            "course_id": course_id,
        }
    
        let final_extra_constructor_params = {
            "ajaxParams": ajaxParams,
            "selectable": false,
            "placeholder": "Popup loading...",
            "pagination": false,
            "layout": "fitColumns",
        }
        
        let elt = document.createElement("div")
        document.body.appendChild(elt)
        let table = init_table(elt, columns.map((col) => {
            return {...col, editor: false, cssClass: (col.cssClass=="format_grade" ? "format_grade" : "")}
        }), null, final_extra_constructor_params, settings = {'title': "Student course data", 'api_table_fetch': 'course_assessments'})

        table.setHeading(`Viewing assessment breakdown for <b>${student_data.name}</b>`)
        
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
                        return {...col, editor: false, cssClass: (col.cssClass=="format_grade" ? "format_grade" : "")}
                    }))
                    let table_data = table.getData()
                    //api call here to save the data.
                    api_post("update_preponderance", table_data).then(response => {
                        if (response.data) {
                            parent_table_to_reload.reloadTable()
                            popup.close()
                            create_notification("Preponderance update", `Preponderance updated successfully for ${student_data.name}. Tables and charts are reloading.`, "success")
                        } else {
                            create_notification("Error", response.status, "error")
                        }
                    })
                }
            } else {
                table.addNotification()
                this.innerHTML = "Save changes!"
                table.setColumns(columns)
                table_element.dataset.edit_mode = 1
            }
        })
        popup.content.classList.add("preponderance-popup")
        popup.content.appendChild(edit_button)
    
    } else {
        create_notification("Error", "No student data or course ID provided.")
    }
    
}

function load_courses_table(extra_constructor_params = {}, extra_cols=true, settings={}){
    let columns = [
        {title: "Row selector", formatter:"rowSelection", titleFormatter:"rowSelection", headerHozAlign:"center", headerSort:false, frozen:true, download:false, maxWidth: 25, hozAlign: "center"},
        {title: "Code", field: "code", headerFilter: "input", frozen:true},
        {title: "Name", field: "name", headerFilter: "input"},
        {title: "Academic year", field: "academic_year", headerMenu: columnHeaderGroupBy},
        {title: "Credits", field: "credits", bottomCalc: "sum", headerMenu: columnHeaderGroupBy},
        {title: "Taught now?", field: "is_taught_now", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
        {title: "Moderated?", field: "is_moderated", formatter: "tickCross", headerMenu: columnHeaderGroupBy},
    ]

    let groupBy = ['academic_year']
    let initialSort = [{column: 'academic_year', dir: 'dsc'}, {column: 'credits', dir: 'dsc'}]

    if (settings.student) {
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
        if (extra_cols) {
            columns.push({title:"Enrolled students", field: "n_students"})
            columns.push({
                title: "Cohort average performance",
                headerHozAlign: "center",
                columns: [
                    {title: "Coursework grade", field: "coursework_avg", cssClass: "format_grade"},
                    {title: "Exam grade", field: "exam_avg", cssClass: "format_grade"},
                    {title: "Final weighted grade", field: "final_grade", cssClass: "format_grade"},
                ]
            })
            groupBy = []
            initialSort = [{column: 'credits', dir: 'dsc'}]
        }
    }

    if (settings.noGroupBy)
        groupBy = []

    let ajaxParams = {
        "fetch_table_data": true,
        "courses": true,
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
                render_course_moderation_section(row.getData(), row.getTable())
            }
        }
    ]

    if (settings.student) {
        rowContextMenu.pop(1)
        rowContextMenu.push({
            label:"<div class='inline-icon' title='This action will create a popup where you can see the student grades for all the assessed content for this course. Additionally, you may view and edit the preponderances here.'><img class='color-icon-theme'src='/static/icons/info.svg'></i><span>Student grades and preponderance(popup)</span></div>",
            action: function(e, row){
                create_student_course_detailed_table_popup(settings.student, row.getData().course_id, row.getTable())
            }
        })
    }


    let final_extra_constructor_params = { ...extra_constructor_params,
        ajaxParams: ajaxParams,
        rowContextMenu:rowContextMenu,
        groupBy: groupBy,
        initialSort: initialSort,
        placeholder: "Course data loading...",
    }
    let table = init_table("courses_table", columns, settings.prefillData, final_extra_constructor_params, settings)

    table.on("tableBuilt", function() {
        table.setGroupHeader(function(value, count, data, group){
            if (settings.student) {
                //reduce the "credits" in each row of data
                let course_credits = data.reduce(function(a, b) {
                    return a + b["credits"]
                }, 0)
                return `<span class='info-text'>${count}</span> courses in ${value}, for a total of <span class='${(course_credits < 120) ? "error-color":"success-color"}'>${course_credits} credits<span>`; //return the header contents
            } else {
                return `<span class='info-text'>${count}</span> courses in ${value}`; //return the header contents
            }
        });
    })

    if (settings.student) {
        table.addChartLink([document.getElementById("student_level_chart"), function(table_inner) {
        let student_data = settings.student
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
            chart_data[year] = {
                'coursework': year_data.bottom.coursework_avg,
                'exam': year_data.bottom.exam_avg,
                'final': parseFloat(year_data.bottom.final_grade).toFixed(1),
            }
        }

        //make abc grades pleasant green color, d grade yellow, and e f g h red
        return {
            data: {
                labels: Object.keys(chart_data),
                datasets: [
                    {
                        label: "Final GPA",
                        data: Object.values(chart_data).map(x => x.final),
                        barPercentage: 0.90,
                        backgroundColor: chart_colors[1],
                    },
                    {
                        label: "Average Coursework GPA",
                        data: Object.values(chart_data).map(x => x.coursework),
                        backgroundColor: chart_colors[4],
                    },
                    {
                        label: "Average Exam GPA",
                        data: Object.values(chart_data).map(x => x.exam),
                        backgroundColor: chart_colors[5],
                    },
                ]
            },
            extra_settings: {
                y_title: "GPA",
                x_title: "Academic year",
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

function render_course_moderation_section(course_data, parent_table=null) {
    let course_id = course_data.course_id
    if (!course_id) {
        console.error("Course ID not found")
        return
    }
    let final_extra_constructor_params = {
        ajaxParams: {
            "fetch_table_data": true,
            "assessments": true,
            "course_id": course_id,
        },
        pagination: false,
        placeholder: "Assessment data loading...",
        height: "auto",
    }
    
    let wrapper = string_to_html_element(`
        <div class="moderation-popup">
            <h4>Moderation section for <b>${course_data.name} - ${course_data.academic_year}</b></h4>
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
        {title: "Row selector", formatter:"rowSelection", titleFormatter:"rowSelection", headerSort:false, frozen:true, download:false, maxWidth: 25, hozAlign: "center"},
        {title: "Assessment type", field: "type"},
        {title: "Assessment name", field: "name"},
        {title: "Weighting", field: "weighting", bottomCalc: "sum", formatter: "money", formatterParams: {precision: 0, symbol: "%", symbolAfter: true}},
        {title: "Current moderation", field: "moderation", headerHozAlign: "center", formatter: moderation_formatter},
        {title: "Moderation User", field: "moderation_user", headerHozAlign: "center"},
        {title: "Moderation Date", field: "moderation_date", headerHozAlign: "center"},
    ]
    let table = init_table("assessments_table", columns, null, final_extra_constructor_params, {'api_table_fetch': 'assessment_moderation'})

    let popup = Popup.init(wrapper)

    const handle_moderation = (mode) => {
        let moderation_value_elt = document.getElementById("moderation-value")
        let moderation_value = moderation_value_elt.options[moderation_value_elt.selectedIndex].value
        if (moderation_value == 0) {
            create_notification("Moderation warning", "Please select a number of bands to moderate by", "warning")
            return
        }
        api_post("moderation", {"mode": mode, "value": moderation_value, "assessment_ids": table.getSelectedData().map(x => x.id), "course_id": course_id}).then(data => {
            if (data.data) {
                popup.close()
                if (parent_table) {
                    parent_table.reloadTable()
                    create_notification("Moderation update", "Moderation updated succesfully. Tables and charts are reloading.", "success")
                }
                else {
                    create_notification("Moderation update", "Moderation updated succesfully.", "success")
                }
            }
             else {
                create_notification("Moderation update", data.status, "error")
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
}

function load_grading_rules_table(data_json, level=null){
    let columns = [
        {title: "Name", field: "name", editor: false},
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

    if (level) {
        columns = [
            {title: "Progression type", field: "name", editor: false},
            {title: "Minimum GPA required to secure given progression type", field: "above", editor: "number", editorParams: {min: 0, max: 22, step: 0.1}, cssClass: "edit-mode"},
        ]
    }

    let final_extra_constructor_params = {
        "selectable": false, 
        "placeholder": "Grading rules loading...",
        "pagination": false,
        footerElement: "<div></div>",
        autoResize: true,
        layout: "fitColumns",
    }
    
    let table = init_table("grading_rules_table", columns.map(
        col => {
            return {...col, editor: false, cssClass: ""}
        }
    ), data_json, final_extra_constructor_params, {no_components:true})

    table.on("dataLoaded", function(data){
        let wrapper = table.getWrapper()
        let footer = wrapper.querySelector('.tabulator-footer-contents')
        let edit_button = document.createElement('button')
        let msg = (level) ? "Level progression" : "Degree classification" + " rules"
        let table_element = table.getElement()
        edit_button.innerHTML = "Edit " + msg
        edit_button.addEventListener('click', function(){
            if (table_element.dataset.edit_mode == 1) {
                table.removeNotification()
                edit_button.innerHTML = "Edit " + msg
                table_element.dataset.edit_mode = 0

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
                api_post("save_grading_rules", table_data).then(response => {
                    create_notification(msg, response.status, "info")
                }) 
            } else {
                table.addNotification()
                edit_button.innerHTML = "Save changes"
                table_element.dataset.edit_mode = 1

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

function load_comments_table(data_json){
    let columns = [
        {title: "Comment", field: "comment", vertAlign:"middle", widthGrow: 1, resizable:false},
        {title: "Lecturer", field: "added_by", vertAlign:"middle", minWidth: 200, maxWidth: 300, resizable:false},
        {title: "Date added", field: "timestamp", vertAlign:"middle", width:150, resizable:false},
    ]

    let footer_element = 
        `<div class='comment-table-footer'>
            <textarea type="text" id="comment_input" placeholder="Write your comment here.."></textarea>
            <button id="add_comment_button">Add comment</button>
            <button class="button_warning hidden" id="delete_comments_button">Delete selected comment(s)</button>
        </div>`
    let final_extra_constructor_params = {
        "selectable": true,
        selectableCheck:function(row){
            return user_full_name == "SUPER-ADMIN" || row.getData().added_by == user_full_name; //allow selection of rows where the age is greater than 18
        },
        "pagination": false,
        "layout": "fitColumns",
        "footerElement": footer_element,
        "rowHeight": 60,
        "autoResize": true,
        "height": "100%",
        "index": "id",
        "renderVertical": "basic", //render 20 rows in buffer
        "placeholder":"There are no comments right now. Feel free to add the first comment!",
    }
    let table = init_table("comments_table", columns, data_json, final_extra_constructor_params, {no_multirow: true, no_components:true})
    table.on("rowSelectionChanged", function(data, rows){
        if (rows.length >= 1) {
            document.getElementById('delete_comments_button').classList.remove("hidden")
        } else {
            document.getElementById('delete_comments_button').classList.add("hidden")
        }
    })

    table.on("tableBuilt", function(){
        let footer = table.getWrapper().querySelector('.tabulator-footer-contents')
        let add_comment_button = footer.querySelector('#add_comment_button')
        let delete_comments_button = footer.querySelector('#delete_comments_button')
        let comment_input = footer.querySelector('#comment_input')
        add_comment_button.addEventListener('click', function(){
            let comment = comment_input.value
            if (comment.length > 0) {
                api_post("add_comment", comment).then(response => {
                    if (response.data) {
                        table.setData(response.data).then(function () {
                            comment_input.value = ""
                            setTimeout(() => {create_notification("Comment addition", response.status, "success")}, 10)
                        })
                    } else {
                        create_notification("Comment addition", response.status, "warning")
                    }
                })
            } else {
                create_notification("Comment addition", "Please enter a non-empty comment.", "warning")
            }
        })

        delete_comments_button.addEventListener('click', function(){
            let selected_rows = table.getSelectedRows()
            let confirm_message = "Are you sure you want to delete this comment?"
            if (selected_rows.length > 1) {
                confirm_message = `Are you sure you want to delete these ${selected_rows.length} comments?`
            }
            if (confirm(confirm_message)) {
                api_post("delete_comments", selected_rows.map(
                    row => row.getData().id
                )).then(response => {
                    if (response.data) {
                        table.setData(response.data).then(function () {
                            setTimeout(() => {create_notification("Comment deletion", response.status, "info")}, 10)
                        })
                    } else {
                        create_notification("Comment deletion", response.status, "warning")
                    }
                })
            }
        })
    })
}