function string_to_html_element(html_string) {
    var doc = new DOMParser().parseFromString(html_string, "text/html");
    return doc.body.firstChild
}

function wrap(el, wrapper) {
    el.parentNode.insertBefore(wrapper, el);
    wrapper.appendChild(el);
    return wrapper;
}

function render_student_data(student_data){
    
}

pagination_size = 1000

window.onload = function() {
    
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

function api_post(action, data) {
    return new Promise((resolve, reject) => {
        var form_data = new FormData();
        form_data.append("action", action)
        document.querySelectorAll(".api_prefill").forEach(element => {
            console.log(element.name, element.value)
            form_data.append(element.name, element.value)
        })

        form_data.append("data", JSON.stringify(data))
        if (form_data.get("csrfmiddlewaretoken") == null) {
            form_data.append("csrfmiddlewaretoken", get_cookie("csrftoken"))
        }
        fetch("/api/", {
            method: "POST",
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
    })
}

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

