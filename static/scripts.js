let vehicle_data;
fetch("/api/vehicles").then(
    resp => {
        resp.json().then(
            json => 
            {
                vehicle_data = json;
                update_selector("start-year-select", get_start_years(), 'Start Year');
            }
        )
    }
)

function get_start_years() {
    return Object.keys(vehicle_data);
}

function get_end_years() {
    let start_year = document.getElementById("start-year-select").value;
    let all_years = Object.keys(vehicle_data);
    return all_years.filter(year => year >= start_year);
}

function range(start, end) {
    return [...Array(end - start + 1).keys()].map(val => start + val)
}

function get_makes_for_year() {
    let start_year = parseInt(document.getElementById("start-year-select").value);
    let end_year = parseInt(document.getElementById("end-year-select").value);
    let all_years = new Set(Object.keys(vehicle_data));

    let available_makes = new Set();
    for(year of range(start_year, end_year)) {
        if(all_years.has(year.toString())) {
            for(make of Object.keys(vehicle_data[year])) {
                available_makes.add(make);
            }
        }
    }
    return Array.from(available_makes).sort();
}

function get_models_for_year_make() {
    let start_year = parseInt(document.getElementById("start-year-select").value);
    let end_year = parseInt(document.getElementById("end-year-select").value);
    let make = document.getElementById("make-select").value;

    let all_years = new Set(Object.keys(vehicle_data));
    let available_models = new Set();
    for(year of range(start_year, end_year)) {
        if(all_years.has(year.toString())) {
            for(model of vehicle_data[year][make] || []) {
                available_models.add(model);
            }
        }
    }
    return Array.from(available_models).sort();
}

function update_selector(selector_id, collection, select_name) {
    let selector = document.getElementById(selector_id);
    let current_value = selector.value;
    selector.innerHTML = "";
    selector.removeAttribute("disabled");
    let has_selected_value = false;

    let default_option = document.createElement("option");
    default_option.textContent = `Select ${select_name}`;
    default_option.value = 'default';
    selector.appendChild(default_option);

    for(value of collection) {
        if(value === current_value) {
            console.log("Has value")
            has_selected_value = true;
        }
        let element = document.createElement("option");
        element.textContent = value;
        element.value = value;
        selector.appendChild(element);
    }

    if(has_selected_value) {
        selector.value = current_value;
    }
}