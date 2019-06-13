function getCookie(name) {
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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function clearStatus(){
    $('#keywords').css("border-color", "#333333");
    $('#keywords').attr("placeholder", "Keywords")
    $("#results").hide();
    $('#processingStatus').css('visibility', 'hidden')
}

var refreshTime = 500; //ms

function finishLoading(total, pk, error){
    if(error){
        $("#results h2").text(total + " books found, but something went wrong :/");
    }else{
        $("#results h2").text(total + " books found");
    }
    
    $("#comaback").text("Check");
    $("#results a").attr('href', '/query/' + pk);
    $("#results").show();

    var progressbar = document.getElementById('progress').ldBar;
    progressbar.set(100);
    $('#processingStatus').hide();
}

function nightWatch(pk){
    $.get('/querystatus/' + pk, function(data){
        console.log(data);
        var found = data.found;
        var status = data.status;
        var total = data.total;
        var error = data.error
        
        if(total == 0){
            total = 1;
        }

        if(status){
            finishLoading(total, pk, error)
        }else{
            var progressbar = document.getElementById('progress').ldBar;
            progressbar.set(found / total * 100);

            setTimeout(function(){
                nightWatch(pk);
            }, refreshTime);
        }
    })
}

function startSearch(){
    $("#results").hide();
    $('#processingStatus').css('visibility', 'hidden')

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var keywords = $('#keywords').html();
    $('.option input').each(function(){
        if(this.checked){
            var name = $(this).attr('class')
            if(name != 'text'){
                keywords = name + ':' + keywords;
            }
        }
    })

    if(keywords.length < 3){
        $('#keywords').css("border-color", "red");
        $('#keywords').attr("placeholder", "Keywords must be longer then 3 characters")
        return;
    }
    
    $.post('/query/', {keywords:keywords}, function(data){
        var pk = data.id;
        var total = data.total;

        if(total == 0){
            if(data.error){
                $("#results h2").text("No book found. Something went wrong :/ ");
            }else{
                $("#results h2").text("No book found");
            }
            
            $("#comaback").text("Return");
            $("#results").show();
            $("#results a").attr('href', '/');
        }else{
            $('#processingStatus h2').text( total + ' books found. Loading.')
            $('#processingStatus').css('visibility', 'visible')
            console.log(data);
            nightWatch(pk)
        }
    })
}
