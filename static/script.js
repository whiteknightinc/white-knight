$(document).ready( function() {
    function empty() {
        var x;
        x = document.getElementById("scrape_button").value;
        if (x == "") {
            alert("Enter a Valid Subreddit");
            return false;
        };
    }
})
