function fancyCountdown(time)
{   // From https://stackoverflow.com/a/11486026
    // days, hours, minutes and seconds
    var days = ~~(time / 86400);
    var hrs = ~~((time % 86400) / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;
    console.log(days, hrs, mins, secs);

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (days > 0) {
        ret += "" + days + " day" + (days != 1 ? "s " : " ");
    }

    ret += (hrs < 10 ? "0" : "")
    ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

function fancyTimeFormat(time)
{   // From https://stackoverflow.com/a/11486026
    // Hours, minutes and seconds
    var hrs = ~~(time / 3600);
    var mins = ~~((time % 3600) / 60);
    var secs = ~~time % 60;

    // Output like "1:01" or "4:03:59" or "123:03:59"
    var ret = "";

    if (hrs > 0) {
        ret += "" + hrs + ":" + (mins < 10 ? "0" : "");
    }

    ret += "" + mins + ":" + (secs < 10 ? "0" : "");
    ret += "" + secs;
    return ret;
}

const nav = (url) =>{
     window.history.pushState(null, document.title, url);
};

// const nav = (r,s,x,url) =>{
//     console.log(r);
//     console.log(s);
//     console.log(x);
//     console.log(url);
//     window.history.pushState(r, document.title, url);
// };

// parse cookie
const getCookie = (s)=>{
    let parse=RegExp(""+s+"[^;]+").exec(document.cookie);
    return decodeURIComponent(!!parse ? parse.toString().replace(/^[^=]+./,"") : "");
};


// header navigation
$(document).on('click', 'a[class^="yata-link"]', function(e){
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(spinner+'&nbsp;&nbsp;Loading '+$(this).attr("title"))
    $(this).html(spinner);
});

// pagination nav
$(document).on('click', 'a.page-link', function(e){
    e.preventDefault();
    var reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load( $(e.currentTarget).attr("href"), function() {});
    $(e.currentTarget).closest("table").find("tr").html('<td>'+spinner+'</td>');
});

// show/hide module
$(document).on('click', 'h2.toggle-display', function(e){
    e.preventDefault();
    var h = $(this);
    // console.log(!($(e.target).hasClass("update-type") && !h.hasClass("rounded")));
    if (!($(e.target).hasClass("update-type") && !h.hasClass("rounded"))) {
        var i = h.find("i.fa-caret-right");
        var div = h.closest(".catch-me").children("div");
        if(div.css("display") == "none") {
            h.removeClass("rounded");
            i.addClass("fa-rotate-90");
        }
        div.slideToggle("fast", function(){
            if(div.css("display") == "none") {
                h.addClass("rounded");
                i.removeClass("fa-rotate-90");
            }
        });
    }
});

// refresh loot timer
window.setInterval(function(){
    $("span#loot-countdown").each(function() {
        var timeRefresh = $.trim($(this).text());
        var splitRefresh = timeRefresh.split(" ");
        var sRefresh = 0;
        if (splitRefresh.length == 2) {
            sRefresh = parseInt(splitRefresh[0]);
        } else if (splitRefresh.length == 4) {
            sRefresh = parseInt(splitRefresh[2]) + 60 * parseInt(splitRefresh[0]);
        } else if (splitRefresh.length == 6) {
            sRefresh = parseInt(splitRefresh[4]) + 60 * parseInt(splitRefresh[2]) + 3600 * parseInt(splitRefresh[0]);
        }

        sRefresh --;
        sRefresh = Math.max(sRefresh, 0)
        if (sRefresh == 0) {
            $(this).parent("span").addClass("error");
            $(this).parent("span").html("NOW");
        }
        hRefresh = Math.floor(sRefresh / 3600);
        sRefresh = sRefresh % 3600;
        mRefresh = Math.floor(sRefresh / 60);
        sRefresh = sRefresh % 60;
        if (hRefresh) {
            spad = ("0"+sRefresh.toString()).slice(-2);
            $(this).html(hRefresh.toString()+" hrs "+mRefresh.toString()+" mins "+spad+" s");
        }
        else if (mRefresh) {
            spad = ("0"+sRefresh.toString()).slice(-2);
            $(this).html(mRefresh.toString()+" mins "+spad+" s");
        } else {
            $(this).html(sRefresh.toString()+" s");
        }
    });
}, 1000);
