
function update_fields() {
    var productTypeSelect = document.getElementById("id_product_type");
    var colorField = document.getElementById("id_color");
    var quantityField = document.getElementById("id_quantity");

    if (productTypeSelect.value === "shrinkwrapper") {
        colorField.value = "";
        quantityField.value = "";
        colorField.setAttribute("disabled", true);
        quantityField.setAttribute("disabled", true);
    } else {
        colorField.removeAttribute("disabled");
        quantityField.removeAttribute("disabled");
    }
}

