$(document).ready(function () {
    updateCreditAndShipping();
});

$(document).on("change", "#partName", function () {
    updateReviewPage();
});

$(document).on("change", "#partURL", function () {
    updateReviewPage();
});

$(document).on("change", "#partQuantity", function () {
    updateReviewPage();
});

$(document).on("change", "#partUnitPrice", function () {
    updateReviewPage();
});

$(document).on("change", "#credit", function () {
    updateCreditAndShipping();
});

$(document).on("change", "#shipping", function () {
    updateCreditAndShipping();
});

function updateCreditAndShipping() {
    var credit = $('#credit').val();
    var shipping = $('#shipping').val();
    if (typeof credit != "undefined" && typeof shipping != "undefined") {
        $('#reviewCredit').html("$" + credit);
        $('#reviewShipping').html("$" + shipping);
        console.log("not undefined")
    }
    updateReviewPage();
}

function updateReviewPage() {
    var partName = $('#partName').val();
    var partURL = $('#partURL').val();
    var quantity = $('#partQuantity').val();
    var unitPrice = $('#partUnitPrice').val();

    var subtotal, total;
    if (quantity == "" || unitPrice == "") {
        subtotal = "Not enough information given";
    } else {
        subtotal = "$" + (quantity * unitPrice).toFixed(2);
    }

    var credit = $('#reviewCredit').html();
    var shipping = $('#reviewShipping').html();

    if (!(credit == "TBD" && shipping == "TBD") && !(quantity == "" && unitPrice == "")) {
        console.log(parseFloat(subtotal.replace("$", "")));
        console.log(parseFloat(shipping.replace("$", "")));
        console.log(parseFloat(credit.replace("$", "")));
        total = "$" + ((parseFloat(subtotal.replace("$", "")) + parseFloat(shipping.replace("$", ""))) - parseFloat(credit.replace("$", ""))).toFixed(2);
        console.log(total);
        console.log("includes cred and ship");
    } else if (quantity == "" || unitPrice == "") {
        total = "Not enough information given";
        console.log("not computable");
    } else {
        total = subtotal;
        console.log("is subtotal");
    }

    $('#reviewPartName').html(partName == "" ? "Not Specified" : partName);
    $('#reviewPartUrl').html(partURL == "" ? "Not Specified" : partURL);
    $('#reviewPartQuantity').html(quantity == "" ? "Not Specified" : quantity);
    $('#reviewPartUnitPrice').html(unitPrice == "" ? "Not Specified" : "$" + unitPrice);
    $('#subtotal').html(subtotal);
    $('#total').html(total);
}