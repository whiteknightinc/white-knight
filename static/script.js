$(document).ready( function() {
    function empty() {
        var x;
        x = document.getElementById("scrape_button").value;
        if (x == "") {
            alert("Enter a Valid Subreddit");
            return false;
        };
    }

    function hide_post() {
        $('.twitter').addClass( 'remove_feed' );
        $('.shame-post').hide();
    }

    $('.edit_button').click(function(event){
    hide_post();
  });


    $('.twitter-share-button').click(function(event){
    hide_post();
  });

})
