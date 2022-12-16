//Description: Javascript Frontend for the Order Scan Screen
//             for index.html
//             User scans in orders and creates all the labels for the products in the system.
//             Uses Socket messaging to communicate to the Flask backend (views.py)
//             


//global variables
var SocketIpList = ["127.0.0.1:5000"];

//get the IP list of all the HMI screens to allow Socket Messaging to be enabled
async function getSocketIpList() {

    result = await fetch("/getSocketIpList", { method: "GET", mode: "no-cors", });

    //iterrate through SocketIPList and add IP to list
    for (let i = 0; i < result.length; i++) {
        console.log(SocketIpList[i]);
        SocketIpList.add(result[i]);
    }
}

//list of IP addresses that can access the SocketIO messages, main and all HMI's
var socket = io.connect(SocketIpList);
var entry = {};
var label_number = 0;
var ordernumber = '';
var lightTimeout;

//When the page elements are done loading, do the following
document.addEventListener("DOMContentLoaded", function () {

    
    //run the Socket IP list generator function
    //getSocketIpList();
    //showProgressBar(true,"update")
    //Always Autofocus the Order Number input box if a keystroke is pressed!
    document.addEventListener("keypress", function (e) {
        if (e.target.tagName !== "INPUT") {
            var input = document.getElementById("scan_label");
            //autofocus input, recover the first keypress, and the rest of the keypresses will fill in
            input.focus();
            input.value = e.key;
            e.preventDefault();
        }

    });

    
    scanInput = document.getElementById("submit_label")
    scanInput.onsubmit = function() {
        showProgressBar(true, "")
    
        rawScanData = document.getElementById("scan_label").value;

        socket.emit("scanLabel", rawScanData)
        return false

    }

    socket.on("fromScanLabel", function (successBool, postJSON) {
        document.getElementById("scan_label").value = '';

        if (successBool == true) {
            showProgressBar(false, "success")

        }
        else if (successBool == false) {
            
            if (postJSON == "invalid") {
                showProgressBar(false, "invalid")
            }
            
            if (postJSON == "no_parts_found") {
                showProgressBar(false, "no_parts_found")
            }
        }
        else {
            showProgressBar(false, "invalid")
        }
        
    })
    
    
    
});




/////////////////////
// Async Functions //
/////////////////////


//Logic for controlling the loading bar
async function showProgressBar(action, alertMessage) {
    var loadingBar = document.getElementById('loading_bar')

    function success_sound() {
        var snd = new Audio("/static/wav/success.wav")
        snd.play();
    }

    function error_sound() {
        var snd = new Audio("/static/wav/error.wav")
        snd.play();
    }

    if (action == true) {

        loadingBar.classList.remove("bg-danger");
        loadingBar.classList.remove("bg-warning");
        loadingBar.classList.remove("bg-success");
        loadingBar.classList.remove("bg-info");
        loadingBar.classList.add("bg-primary");
        loadingBar.classList.remove('fade')
        loadingBar.innerHTML = "<h2 id=\"loading_bar_text\" class=\"m-3\">Searching Database...</h2>"

        if (alertMessage == 'update') {
            loadingBar.classList.remove("bg-danger");
            loadingBar.classList.remove("bg-warning");
            loadingBar.classList.remove("bg-success");
            loadingBar.classList.remove("bg-info");
            loadingBar.classList.add("bg-primary");
            loadingBar.innerHTML = "<h2 id=\"loading_bar_text\" class=\"m-3\">Loading...<h2/>"

        }
    }

    //Prepare to Hide the Loading bar
    if (action == false) {
        console.log(alertMessage)

        //Display success message
        if (alertMessage == 'success') {
            
            loadingBar.classList.remove("bg-primary");
            loadingBar.classList.remove("bg-warning");
            loadingBar.classList.remove("bg-danger");
            loadingBar.classList.remove("bg-info");
            loadingBar.classList.add("bg-success");
            loadingBar.innerHTML = "<h2 id=\"loading_bar_text\">Unpacked Parts Found</h2><h4>Creating Label...</h4></h2>"

            setTimeout(function success() {
                loadingBar.classList.add('fade')
                loadingBar.classList.remove("bg-success");
                loadingBar.classList.add("bg-primary");
            }, 1500);
        }

        //If order number entered is an invalid order number
        else if (alertMessage == 'invalid') {
            

            loadingBar.classList.remove("bg-warning")
            loadingBar.classList.remove("bg-primary");
            loadingBar.classList.remove("bg-success");
            loadingBar.classList.remove("bg-info");
            loadingBar.classList.add("bg-danger");
            loadingBar.innerHTML = "<h2 id=\"loading_bar_text\" class=\"m-3\">Invalid Scan</h2>"

            setTimeout(function invalid() {
                loadingBar.classList.add('fade')
                loadingBar.classList.remove("bg-success");
                loadingBar.classList.add("bg-primary");
            }, 5000);
        }

        else if (alertMessage == 'no_parts_found') {
            

            loadingBar.classList.remove("bg-warning")
            loadingBar.classList.remove("bg-primary");
            loadingBar.classList.remove("bg-success");
            loadingBar.classList.remove("bg-info");
            loadingBar.classList.add("bg-danger");
            loadingBar.innerHTML = "<h2 id=\"loading_bar_text\" class=\"m-3\">No Unpacked Parts Found</h2>"
            
            setTimeout(function invalid() {
                loadingBar.classList.add('fade')
                loadingBar.classList.remove("bg-success");
                loadingBar.classList.add("bg-primary");
            }, 5000);
        }
    }
}



