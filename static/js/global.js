function string_to_html_element(html_string) {
    var doc = new DOMParser().parseFromString(html_string, "text/html");
    return doc.body.firstChild
}

function render_student_data(student_data){
    
}

window.onload = function() {
    var page_data = document.getElementById('page_data');
    var page_data = (page_data.dataset.all);
    
    for (var student in page_data) {
        render_student_data(page_data[student]);
    }

    string_to_html_element(
        `
        <div>

        </div>
        `
    )
}