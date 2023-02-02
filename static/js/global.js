function string_to_html_element(html_string) {
    var doc = new DOMParser().parseFromString(html_string, "text/html");
    return doc.body.firstChild
}

function isElement(element) {
    return element instanceof Element || element instanceof HTMLDocument;  
}

function wrap(el, wrapper) {
    el.parentNode.insertBefore(wrapper, el);
    wrapper.appendChild(el);
    return wrapper;
}

pagination_size = 1000

function toggle_based_on_sidebar_state(sidebar, hardset_state=null) {
    let sidebar_is_collapsed = null
    if (hardset_state != null) {
        sidebar_is_collapsed = hardset_state
        sessionStorage.setItem("sidebar-collapsed", sidebar_is_collapsed)
        console.log("session storage is", sessionStorage.getItem("sidebar-collapsed"))
    } else {

        sidebar_is_collapsed = sidebar.classList.contains("sidebar-collapsed")
        let session_sidebar_collapsed = sessionStorage.getItem("sidebar-collapsed")
        
        if (session_sidebar_collapsed == "true") {
            sidebar_is_collapsed = true
        } else if (session_sidebar_collapsed == "false") {
            sidebar_is_collapsed = false
        } else { //if session is not set
            sessionStorage.setItem("sidebar-collapsed", sidebar_is_collapsed)
        }
    }

    console.log("sidebar is collapsed", sidebar_is_collapsed)

    let main_area = document.querySelector(".main-area")
    if (!sidebar_is_collapsed) {
        main_area.classList.add("main-area-collapsed")
        sidebar.classList.remove("sidebar-collapsed")
    } else {
        main_area.classList.remove("main-area-collapsed")
        sidebar.classList.add("sidebar-collapsed")
    }
}

window.onload = function() {
    let sidebar = document.querySelector(".sidebar")
    toggle_based_on_sidebar_state(sidebar)

    let sidebar_toggle_button = document.querySelector(".toggle-sidebar-container")
    if (sidebar && sidebar_toggle_button) {
        sidebar_toggle_button.addEventListener("click", function() {
            let siderbar_collapsed = sidebar.classList.toggle("sidebar-collapsed")
            toggle_based_on_sidebar_state(sidebar, siderbar_collapsed)
        })
    }
}

function get_cookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function api_factory(method) {
    function api(action, data) {
        return new Promise((resolve, reject) => {
            var form_data = new FormData();
            form_data.append("action", action)
            document.querySelectorAll(".api_prefill").forEach(element => {
                console.log(element.name, element.value)
                form_data.append(element.name, element.value)
            })
            
            if (data)
                form_data.append("data", JSON.stringify(data))
            if (form_data.get("csrfmiddlewaretoken") == null) {
                form_data.append("csrfmiddlewaretoken", get_cookie("csrftoken"))
            }
            
            if (method == "GET") {
                const queryString = new URLSearchParams(form_data).toString()
                fetch("/api/?" + queryString, {
                    method: method,
                }).then(response => {
                    if (response.status == 200) {
                        response.json().then(data => {
                            resolve(data)
                        });
                    } else {
                        reject(response)
                    }
                })
                return
            } else if (method == "POST") {
                fetch("/api/", {
                    method: method,
                    body: form_data,
                }).then(response => {
                    if (response.status == 200) {
                        response.json().then(data => {
                            resolve(data)
                        });
                    } else {
                        reject(response)
                    }
                })
                return
            }
        })
    }
    return api
}

const api_post = api_factory("POST")
const api_get = api_factory("GET")

// function api_post(action, data) {
//     return new Promise((resolve, reject) => {
//         var form_data = new FormData();
//         form_data.append("action", action)
//         document.querySelectorAll(".api_prefill").forEach(element => {
//             console.log(element.name, element.value)
//             form_data.append(element.name, element.value)
//         })

//         form_data.append("data", JSON.stringify(data))
//         if (form_data.get("csrfmiddlewaretoken") == null) {
//             form_data.append("csrfmiddlewaretoken", get_cookie("csrftoken"))
//         }
//         fetch("/api/", {
//             method: "POST",
//             body: form_data,
//         }).then(response => {
//             if (response.status == 200) {
//                 response.json().then(data => {
//                     resolve(data)
//                 });
//             } else {
//                 reject(response)
//             }
//         })
//     })
// }

function api(page_count, pagination_size) {
    return new Promise((resolve, reject) => {
        fetch(window.location.href + `?api_get=true&page=${page_count}&size=${pagination_size}`).then(response => {
            if (response.status == 200) {
                response.json().then(data => {
                    resolve(data)
                });
            } else {
                reject(response)
            }
        })
    })
    // return fetch(window.location.href, {
    //     method: "POST",
    //     headers: {
    //         "Content-Type": "application/json",
    //         "X-CSRFToken": csrf_token,
    //     },
    //     body: JSON.stringify({
    //         "action": action,
    //         "block_id": block_id,
    //         "csrfmiddlewaretoken": csrf_token,
    //     })
    // })  
}

const Popup = {
    content: null,
    init: function(content) {
        let z_index = 1000
        document.querySelectorAll(".popup-wrapper").forEach(element => {
            z_index += 1
        })

        let popup_wrapper = document.createElement("div")
        popup_wrapper.style.position = "fixed"
        popup_wrapper.style.top = 0
        popup_wrapper.style.left = 0
        popup_wrapper.style.width = "100%"
        popup_wrapper.style.height = "100%"
        popup_wrapper.style.backgroundColor = "transparent"
        popup_wrapper.style.zIndex = z_index
        popup_wrapper.style.display = "flex"
        popup_wrapper.style.justifyContent = "center"
        popup_wrapper.style.alignItems = "center"
        popup_wrapper.style.overflow = "auto"
        popup_wrapper.classList.add("popup-wrapper")
        popup_wrapper.style.backdropFilter =  "blur(5px)"

        let popup_inner = document.createElement("div")
        popup_inner.style.backgroundColor = "white"
        popup_inner.style.border = "1px solid black"
        popup_inner.style.borderRadius = "5px"
        popup_inner.style.position = "relative"
        popup_inner.style.padding = "10px"
        popup_inner.style.maxHeight = "80%"
        popup_inner.style.maxWidth = "80%"
        popup_inner.style.overflow = "auto"
        popup_inner.style.boxShadow = "0 0 10px 0 rgba(0,0,0,0.5)"
        popup_inner.style.zIndex = z_index + 200
        popup_inner.style.display = "flex"
        popup_inner.style.justifyContent = "center"
        popup_inner.style.alignItems = "center"
        popup_inner.style.overflow = "auto"

        popup_wrapper.appendChild(popup_inner)

        //make everythihing except the popup wrapper be blurred
        let main_body = document.querySelector(".body-inner-wrapper")
        main_body.classList.add("disabled-body")
        
        let close_button = document.createElement("button")
        close_button.classList.add("popup-close-button")
        close_button.innerHTML = "Close"
        close_button.onclick = () => {this.close()} //use arrow function to bind this to the popup object
        popup_inner.appendChild(close_button)
        
        window.onclick = (e) => {
            let found_wrapper = document.querySelector(".popup-wrapper")
            if (!found_wrapper) return
            if (e.target == found_wrapper || e.target == found_wrapper.querySelector(".popup-close-button")) {
                this.close()
            }
        }

        popup_inner.appendChild(content)
        document.body.prepend(popup_wrapper)
        this.content = content
        return this
    },
    close: function() {
        let wrapper = document.querySelector(".popup-wrapper")
        if (wrapper) wrapper.remove()
        
        if (!document.querySelector(".popup-wrapper"))
            document.querySelector(".body-inner-wrapper").classList.remove("disabled-body")
        
        delete this
    },
}

//chart to chart handler map. say table is reloaded - chart needs to be reloaded.
//as soon as table has data - chart needs to be initialized.

//a function that takes a tables data, and returns chart data object.

const Charts = {
    init: function(chart_or_chart_id=null, type=null, data={}, options={}) {
        let chart = chart_or_chart_id
        if (chart == null) {
            chart = document.createElement("canvas")
        } else {
            chart = (isElement(chart)) ? chart : document.getElementById(chart)
        }
        
        console.log("initializing chart")
        this.chart = new Chart(chart, {
            type: (type) ? type : 'bar',
            data: (data) ? data : {
                labels: [],
                datasets: [
                    {
                        label: 'Number of courses offered in a given year',
                        data: [],
                    }
                ]
            },
            options: {
              scales: {
                y: {
                  beginAtZero: true
                }
              }
            }
          });
        
        console.log("chart initialized")
        return this
    },
    chart: null,
    load_with_table_data: function(table, population_function) {
        console.log("loading chart with table data")
        console.log(table)
        let data = population_function(table)
        console.log(data)
        console.log(this.chart)
        //population_function is a function that takes a table data object, and returns chart data object.
        this.chart.data = population_function(table)
        this.chart.update('active')
        console.log("done!")
    },
    destroy: function() {
        this.chart.destroy()
    }
}


//MOSCOW CHARTS PLAN.

//today: Create chart system. Add simple charts to every page.
//my own
//degree classification: 
// degree qualification distribution

// course page:
// final grade distribution
// average grade per assignment distribution

// student page:
// 

// dashboard (given year):
// all courses offered in that year
// all students in that year
// 

//moscow
//1. grades below band d3 -> in course page, we have final grade. we can use that to show the grade distribution.

// 

//note that dashboard should be year by year. for sure.
// percentage of students in a grade band, in a particular YEAR.