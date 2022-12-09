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

