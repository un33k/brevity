var tracker_on = false;

$(document).ready(function(){

    jQuery.fn.hasAttr = function(name) {
       return this.attr(name) !== undefined;
    };

    String.prototype.contains = function(sub_str) {
        return this.indexOf(sub_str) != -1;
    };

    // checkbox simulation
    ///////////////////////////////////////
    $(document).on('hover', '.checkbox.toggle',function(e){
        if($(this).hasClass('disabled')){
            return
        }
        if($(this).children('i').hasClass('icon-check')){
            $(this).children('i').removeClass('icon-check').addClass('icon-check-empty');
        }
        else if($(this).children('i').hasClass('icon-check-empty')){
            $(this).children('i').removeClass('icon-check-empty').addClass('icon-check');
        }
    });

    // background flasher
    ///////////////////////////////////////
    jQuery.fn.backgroundFlashFade = function(timeout, flash_color, orig_color) {
        if (!is_valid(orig_color)) {
            var orig_color = this.css('backgroundColor');
        }
        if (!is_valid(flash_color)) {
            var flash_color = 'yellow';
        }
        if (!is_valid(timeout)) {
            var timeout = 500;
        }
        return this.css({
            'backgroundColor': flash_color
        }).animate({
            'backgroundColor': orig_color
        }, timeout);
    };

    // text flasher
    //////////////////////////////////////
    jQuery.fn.textFlashFade = function(timeout, flash_color, orig_color) {
        if (!is_valid(orig_color)) {
            var orig_color = this.css('color');
        }
        if (!is_valid(flash_color)) {
            var flash_color = 'yellow';
        }
        if (!is_valid(timeout)) {
            var timeout = 700;
        }
        return this.css({
            'color': flash_color
        }).animate({
            'color': orig_color
        }, timeout);
    };

    String.prototype.isEmpty = function() {
        return (this.length === 0 || !this.trim());
    };
});

// Re-Enabling stuff after full/partial reloads (FrontEnd)
////////////////////////////////////
$(document).ready(function(){
    trigger_full_page_load_event_frontend();
});

function trigger_full_page_load_event_frontend(){
    $( document ).trigger( "FullPageLoadFrontend", [] );
}

function trigger_partial_page_load_event_frontend(){
    $( document ).trigger( "PartialPageLoadFrontend", [] );
}

function full_page_load_frontend() {
    enable_confirmation();
    enable_tooltip();
    tracker_on_cleanup();
    enable_page_refresh();
    maps_load();
    $("[rel='popover']").popover();
    $(".top-nav .navbar-fixed-top").autoHidingNavbar();
}
function partial_page_load_frontend() {
    enable_confirmation();
    enable_tooltip();
    tracker_on_cleanup();
}
// Public house keeping
$( document ).on( "FullPageLoadFrontend", function(event) {
    console.log('FullPageLoadFrontend')
    full_page_load_frontend();
});
// Public house keeping
$( document ).on( "PartialPageLoadFrontend", function(event) {
    console.log('PartialPageLoadFrontend')
    partial_page_load_frontend();
});


// Hide popover when clicked outside
////////////////////////////////////
$('body').on('click', function (e) {
    $('[data-toggle=popover]').each(function () {
        // hide any open popovers when the anywhere else in the body is clicked
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

// Enable page refresh for superuser
////////////////////////////////////
function get_page_refresh_timeout(){
    var params = get_query_params();
    var min_refresh_time = 4;
    var refresh_time = null;
    $.each(params, function( index, value ) {
        if (value[0] === 'refresh') {
            refresh_time = parseInt(value[1]);
            if (refresh_time < min_refresh_time){
                refresh_time = min_refresh_time;
            }
            return refresh_time
        }
    });
    return refresh_time
}
function enable_page_refresh(){
    var refresh_time = get_page_refresh_timeout();
    if (refresh_time && $('meta[http-equiv="refresh"]').length){
        setTimeout(function() {location.reload();}, refresh_time * 1000);
        var last_hash = $('[name^=#snippet-block-]').last().attr('name');
        if (last_hash) {
            jump_to_smoothly(last_hash, 1500);
        }
    }
}
function is_refresh_on() {
    if (get_page_refresh_timeout()){
        return true;
    }
    return false;
}

// Collapse menu bar on click outside of it
////////////////////////////////////
$(document).click(function (event) {
    if ($('.top-nav .navbar-collapse').hasClass('in')){
        $(".top-nav .navbar-collapse").removeClass('in');
    }
});
var nav_bar_collapse_on_scroll = debounce(function() {
    if ($('.top-nav .navbar-collapse').hasClass('in')){
        $(".top-nav .navbar-collapse").removeClass('in');
    }
}, 100);
window.addEventListener('scroll', nav_bar_collapse_on_scroll);

// Change the address bar programmatically
////////////////////////////////////
function push_state_sync(next_url){
    window.history.pushState('', '', next_url);
}

// Hide menu bar for a fullscreen modal
////////////////////////////////////
var lastScrollTop = 0;
var lastDirection = '';
var directionCount = 0;
var dirUp = 'UP';
var dirDown = 'DOWN';
var upDirctionCount = 6;
var downDirctionCount = 16;
var fadeInComplete = false;
var fadeOutComplete = false;
var navBarElement = $('#full-screen-modal .modal-navbar');
var nav_bar_auto_hide = debounce(function() {
    // perform the following action on de-bounced event
    distance_from_top = 40;
    var distance = $(".modal-scrollable").scrollTop();
    if (distance > lastScrollTop){
        if (lastDirection == dirDown){
            directionCount += 1;
        } else {
            directionCount = 0;
            lastDirection = dirDown;
        }
        if (distance > distance_from_top && directionCount > downDirctionCount && !fadeOutComplete) {
            navBarElement.removeClass('nav-down').addClass('nav-up');
            fadeOutComplete = true;
            fadeInComplete = false;
        }
        console.log('down')
    } else {
        if (lastDirection == dirUp){
            directionCount += 1;
        } else {
            directionCount = 0;
            lastDirection = dirUp;
        }
        if (directionCount > upDirctionCount && !fadeInComplete) {
            navBarElement.removeClass('nav-up').addClass('nav-down');
            fadeInComplete = true;
            fadeOutComplete = false;
        }
        console.log('up')
    }
    lastScrollTop = distance;
}, 5);

$(document).on('show.bs.modal', '#full-screen-modal', function (e) {
    $(".modal-scrollable").unbind("scroll");
    $(".modal-scrollable").scroll(function(){
        nav_bar_auto_hide();
    });
});

// Returns a function, that, as long as it continues to be invoked, will not
// be triggered. The function will be called after it stops being called for
// N milliseconds. If `immediate` is passed, trigger the function on the
// leading edge, instead of the trailing.
// var myEfficientFn = debounce(function() {
//    action item goes here
//}, 250);
// window.addEventListener('resize', myEfficientFn);
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};


function setup_confirmation() {
    $( ".confirm" ).each(function( index ) {
        var me = $(this);
        var placement = me.attr('placement') || 'left';
        me.confirmation({
            btnOkLabel: 'Yes',
            btnOkClass: 'btn btn-sm btn-primary confirmation-ok-btn',
            btnOkIcon: 'fa fa-check',
            btnCancelLabel: 'No',
            btnCancelClass: 'btn btn-sm btn-default',
            btnCancelCIcon: 'fa fa-times',
            placement: placement,
            onConfirm: function(event, element){
                event.preventDefault();
                var type = $(element).attr('confirm-type');
                if (type){
                    $(element).addClass(type+"-deletion-submitter");
                    $(element).trigger( "click" );
                } else {
                    window.location.href = me.attr('href');
                }
            }
        });
    });
}

function enable_confirmation(timeout) {
    timeout = timeout || 0
    setTimeout(function() {
        setup_confirmation();
    }, timeout);
}

// Smooth Scrolling To name=#hash on demand - Stop on any user interaction
///////////////////////////////////////
$('body,html').bind('scroll mousedown wheel DOMMouseScroll mousewheel keyup touchmove', function(e){
    if ( e.which > 0 || e.type == "mousedown" || e.type == "mousewheel"){
        $("html,body").stop();
    }
});
function jump_to_smoothly(hash, timeout){
    timeout = timeout || 300;
    setTimeout(function() {
        if (hash.indexOf('#') != 0) {
            hash = '#' + hash;
        }
        var target = $('[name=' + hash +']');
        if (target && target.length) {
            $('html,body').animate({
                scrollTop: target.offset().top
            }, 1000);
            return false;
        }
    }, timeout);
}

// Ajax Wheel Show/Hide
///////////////////////////////////////
function toggle_ajax_wheel(element, action){
    var parent = element;
    var max_try = 4;
    var idx = 0;
    do {
        var spinner = parent.find('.ajax_wheel').first();
        if (spinner.hasClass('spin-it')) {
            if (action == 'off'){
                spinner.hide()
            } else if (action == 'on'){
                spinner.show()
            } else {
                spinner.toggle();
            }
            break;
        }
        parent = parent.parent();
        idx++;
    } while (idx <= max_try);
    if (idx > max_try){
        if (element.hasClass('spin-it')) {
            if (action == 'off'){
                element.removeClass('fa-spin')
            } else if (action == 'on'){
                element.addClass('fa-spin')
            }
        }
    }
}

// Tooltip stuff
///////////////////////////////////////
var isTouch = (('ontouchstart' in window) || (navigator.msMaxTouchPoints > 0));

function enable_tooltip(timeout){
    timeout = timeout || 0;
    setTimeout(function() {
        if (!isTouch){
            $('[rel=tooltip]').tooltip();
        }
    }, timeout
    );
}

$(document).on('click','[rel=tooltip]',function(e){
    $(this).tooltip('hide');
});


// Toaster stuff
///////////////////////////////////////
function toaster(level, msg, duration){
  toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": true,
    "positionClass": "toast-bottom-full-width",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": duration || 300,
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
  }
  toastr[level](msg);
}

// if variable is set
/////////////////////////////////////////
function is_valid(value){
    return (value && (typeof value !== 'undefined') &&
            value != '' && value != 'None'&&
            value.toString() != '0.0' && value.toString() != '0');
}

// One video playing per page.
/////////////////////////////////////////
function stop_other_videos() {
    $( ".video-wrapper" ).each(function(index) {
        var me = $(this);
        var image = me.find('.image');
        var video = me.find('.video');
        image.fadeIn();
        video.html('');
    });
}

// Load video only on click
/////////////////////////////////////////
$(document).on('click','.video-play-container',function(e){
    stop_other_videos();
    var me = $(this);
    var image = me.find('.image');
    var video = me.find('.video');
    var width = me.width();
    var height = me.height();
    var link = video.attr('data-link') + '?rel=0&autoplay=1';
    var directive = 'frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen';
    var iframe = '<iframe  src="' + link + '" width="' + width + '" height="' + height + '" ' + directive + '></iframe>'
    video.html(iframe).fadeIn('slow');
});

// Rotate on hover
/////////////////////////////////////////
$(document).on('mouseover','.rotate-wrapper',function(e){
    var pin = $(this).find('i:first-of-type');
    if (pin.hasClass('fa-rotate-45')){
        pin.removeClass('fa-rotate-45').addClass('text-danger').removeClass('text-success')
    } else {
        pin.addClass('fa-rotate-45').addClass('text-success').removeClass('text-danger')
    }
})
$(document).on('mouseout','.rotate-wrapper',function(e){
    var pin = $(this).find('i:first-of-type');
    if (pin.hasClass('fa-rotate-45')){
        pin.removeClass('fa-rotate-45').addClass('text-danger').removeClass('text-success')
    } else {
        pin.addClass('fa-rotate-45').addClass('text-success').removeClass('text-danger')
    }
})

// Share Modal
/////////////////////////////////////////
$("#social-sharing-modal-article").on("show.bs.modal", function(e) {
    var link = $(e.relatedTarget);
    $(this).find(".modal-body").load(link.attr("data-url"));
});

// Advanced search
/////////////////////////////////////////
$(document).on('click','.text-search',function(e){
    var modal = $('#text-search-modal');
    modal.modal('show');
    modal.on('shown.bs.modal', function () {
        $('#text-search-input').focus();
        $('#text-search-input').select();
    })
});

$(document).on('click','.text-search-submit-button',function(e){
        advanced_search_submit();
});

$(document).on('keypress','#text-search-form',function(e){
    if (e.which == 13) {
        e.preventDefault();
        advanced_search_submit();
    }
});

$(document).on('click','#text-search-clear',function(e){
    $('#text-search-input').val('');
    advanced_search_submit();
});

function get_query_params() {
    var params = [];
    var uri = decodeURIComponent(location.search.substr(1));
    if (uri){
        uri.split("&").some(function(item) {
            params.push(item.split("="));
        })
    }
    return params
}

function update_query_string(params, query_string) {
    updated_params = [];
    $.each(params, function( index, value ) {
        if (value[0] !== 'query') {
            updated_params.push(value);
        }
    });
    query_string = query_string || '';
    if (query_string) {
        updated_params.push(['query', query_string]);
    }
    return updated_params
}

function build_query_uri(params) {
    var string = '';
    $.each(params, function( index, value ) {
        if (index == 0){
            string += value[0] + '=' + value[1];
        } else {
            string += '&' + value[0] + '=' + value[1];
        }
    });
    return string
}

function advanced_search_submit(element) {
    var input = $('#text-search-input');
    var query_string = input.val();
    var referrer = input.attr('data-referrer') || 'search';
    var cur_params = get_query_params();
    var new_params = update_query_string(cur_params, query_string);
    var query_uri = build_query_uri(new_params);
    var search_url = '/' + referrer + '?' + query_uri;
    $('#text-search-input').addClass('input-ajax-wheel');
    window.location.href = search_url;
}


// Ajaxable
$(document).on('click', '.has-ajax', function () {
    var me = $(this);
    toggle_ajax_wheel(me, 'on');
});


// Paginate
/////////////////////////////////////////
function lazy_paginate(element, html) {
    element.fadeOut('slow', function() {
        element.replaceWith(html).fadeOut('slow', function() {;
            $(this).fadeIn('slow', function() {
                trigger_partial_page_load_event_frontend();
            });
        });
    });
}
$(document).on('click','.show-more-button',function(e){
    var me = $(this);
    var display_msg = me.find('.pagination-message');
    display_msg.html('loading ...')
    var url = me.attr('data-url');
    var pagination_container = $('#pagination-data-container');

    toggle_ajax_wheel(me, 'on');
    $.ajax({
        url: url,
        type: 'GET',
        timeout: 8000,
        data: {},
        dataType: 'json',
        success: function(result) {
            lazy_paginate(pagination_container, result.html)
            push_state_sync(result.curr_url);
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});

function is_a_bot() {
    var agent = navigator.userAgent || '';
    if (/bot|robot|spider|crawl|google|bing|yahoo|baidu/i.test(agent.toLowerCase())) {
        return true;
    }
}

// Full view
/////////////////////////////////////////
function build_article_view_url(next_url, history) {
    var history = history || false;
    var params = get_query_params();
    var string = '';
    $.each(params, function( index, value ) {
        if (value[0] !== 'history') {
            if (index == 0){
                string += value[0] + '=' + value[1];
            } else {
                string += '&' + value[0] + '=' + value[1];
            }
        }
    });
    if (history) {
        if (string.isEmpty()){
            uri = next_url + '?history=on';
        } else {
            uri = next_url.split('?')[0] + '?' + string + '&history=on';
        }
    } else {
        if (string.isEmpty()){
            uri = next_url.split('?')[0];
        } else {
            uri = next_url
        }
    }
    return uri
}
$(document).on('click','.read-full-article', function(e){
    if (is_a_bot()) {
        return
    }
    e.preventDefault();
    var me = $(this);
    var next_url = me.attr('href');
    var parent = me.closest('.article-view-action');
    var category = me.attr('data-category');
    if (category && category.length) {
         var url = next_url + '?category=' + category + '&history=on';
    } else {
        var url = build_article_view_url(next_url, true);
    }
    window.location.href = url;
});
$( document ).ready(function() {
    var params = get_query_params();
    $.each(params, function( index, value ) {
        if (value[0] === 'history' && value[1] === 'on') {
            $('.article-history').removeClass('hidden');
            var url = window.location.href.split('?')[0]
            push_state_sync(url);
            return
        }
    });
});
$(document).on('click','.article-history', function(e){
    e.preventDefault();
    history.go(-2);
});

// Featured Article
///////////////////////////////////////
function toggle_featured_icon(element, featured) {
    featured = featured || 'NO';
    if (featured === 'YES'){
        element.removeClass('black').addClass('green');
    } else {
        element.removeClass('green').addClass('black');
    }
}
$(document).on('click', '.article-featured', function () {
    var me = $(this);
    var url = me.attr('data-url');
    var icon = me.find('i');
    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            toggle_featured_icon(icon, result.featured)
        },
        error: function(result) {
            // toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});

// Trac toggle
///////////////////////////////////////
$(document).ready(function(){
    var me = $('.trac_initial_load');
    if (me.attr('trac-state') == 'TICK_INIT'){
        me.trigger('click');
    }
});

$(document).on('click', 'a', function () {
    var me = $(this);
    if (!me.hasAttr('trac-type')){ return; }
    trac_elment_toggler(me);
    return false;
});
function trac_update_like(element, result){
    element.attr('trac-state', result['state']);
    var target = element.find('.trac-togglable-value');
    value = result['counters']['likes'];
    var icon = element.find('i');
    var color = 'brown';
    if (result['state'] == 'TICK_OFF'){
        icon.removeClass('fa-heart').removeClass(color).addClass('fa-heart-o');
    }else if (result['state'] == 'TICK_ON'){
        icon.removeClass('fa-heart-o').addClass('fa-heart').addClass(color);
    }
    if (value > 0) {
        target.html(value)
    } else {
        target.html('0');
    }
}
function trac_update_star(element, result){
    element.attr('trac-state', result['state']);
    var target = element.find('.trac-togglable-value');
    value = result['counters']['stars'];
    var icon = element.find('i');
    var color = 'gold';
    if (result['state'] == 'TICK_OFF'){
        icon.removeClass('fa-star').removeClass(color).addClass('fa-star-o');
    }else if (result['state'] == 'TICK_ON'){
        icon.removeClass('fa-star-o').addClass('fa-star').addClass(color);
    }
    if (value > 0) {
        target.html(value)
    } else {
        target.html('Star');
    }
}
function trac_update(element, type, result){
    if (type == 'Like') {
        trac_update_like(element, result)
    } else if (type == 'Star') {
        trac_update_star(element, result)
    }
}
function trac_elment_toggler(element){
    if (!element.hasAttr('trac-type')){ return; }
    var url = element.attr('href');
    var postdata = {
        'trac-oid': element.attr('trac-oid'),
        'trac-app': element.attr('trac-app'),
        'trac-type': element.attr('trac-type'),
        'trac-class': element.attr('trac-class'),
        'trac-state': element.attr('trac-state'),
        'csrfmiddlewaretoken': $('form#csrf_post_form input').val()
    }
    $.ajax({
        url: url,
        type: 'POST',
        timeout: 15000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            trac_update(element, postdata['trac-type'], result);
        },
        error: function(result) {
            // toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
}

function set_tracker_on(){
     window.tracker_on = true;
}

function tracker_on_cleanup(timeout) {
    if (window.tracker_on) {
        timeout = timeout || 0;
        setTimeout(function() {
            var trackable_items = ['.site-ad-box', '.site-comment-box-facebook'];
            trackable_items.forEach(function(item, index){
                $(item).remove();
            });
        }, timeout);
    }
}
