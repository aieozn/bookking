var acctPage = 0;

function getNextPage(){
    if(acctPage == -1){
        return;
    }

    $('#loadingBar').show();

    acctPage += 1
    var link = acctPage

    $.get(link, function(data){
        $('#bookList').append(data);
        if(data == ''){
            acctPage = -1;
        }
        $('#loadingBar').hide();
    })
}

$(document).ready(function(){
    getNextPage();
})

$(window).on("scroll", function() {
	var scrollHeight = $(document).height();
	var scrollPosition = $(window).height() + $(window).scrollTop();
	if ((scrollHeight - scrollPosition) / scrollHeight === 0) {
        // when scroll to bottom of the page
        getNextPage();
	}
});