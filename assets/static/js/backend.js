$(document).ready(function(){
    trigger_full_page_load_event_backend();
    trigger_partial_page_load_event_backend();
});

function trigger_full_page_load_event_backend(){
    $( document ).trigger( "FullPageLoadBackend", [] );
}

function trigger_partial_page_load_event_backend(){
    $( document ).trigger( "PartialPageLoadBackend", [] );
}

// Re-Enabling stuff after full/partial reloads Backend
////////////////////////////////////
function full_page_load_backend() {
    dropzone_attach_to_snippets();
    enable_confirmation();
    enable_tooltip()
    enable_confirmation();
    wysiwyg_attach_to_all_elements('textarea.wysiwyg');
    enable_snippet_insert_popover();
}

function partial_page_load_backend() {
    dropzone_attach_to_snippets();
    enable_confirmation();
    enable_tooltip()
    enable_confirmation();
    wysiwyg_attach_to_all_elements('textarea.wysiwyg');
    append_common_to_autocomplete();
    enable_snippet_insert_popover();
    maps_reload();
}

// Public house keeping
$( document ).on( "FullPageLoadBackend", function(event) {
    console.log('FullPageLoadBackend')
    full_page_load_backend();
});
// Public house keeping
$( document ).on( "PartialPageLoadBackend", function(event) {
    console.log('PartialPageLoadBackend')
    partial_page_load_backend();
});


// WysIsWyg stuff
///////////////////////////////////////
wysiwyg_option = {
    height: 180,
    disableLinkTarget: true,
    disableDragAndDrop: true,
    insertTableMaxSize: {
        // col: 2,
        row: 10
    },
    toolbar: [
        ['font', ['bold', 'italic', 'underline', 'strikethrough']],
        ['table', ['table']],
        ['insert', ['link']],
        ['view', ['fullscreen', 'codeview']]
    ],
    callbacks: {
        onPaste: function (e) {
            var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('Text');

            e.preventDefault();

            // Firefox fix
            setTimeout(function () {
                document.execCommand('insertText', false, bufferText);
            }, 10);
        }
    }
}
///////////////////////////////////////
function wysiwyg_attach_to_element(element, delay) {
    delay = delay || 0;
    setTimeout(function() {
      $(element).summernote(wysiwyg_option);
    }, delay);
}
function wysiwyg_attach_to_all_elements(elements, delay){
    $(elements).each(function (idx){
        wysiwyg_attach_to_element(this, delay);
    });
}

// Popover - Snippet Add/Insert
///////////////////////////////////////
function enable_snippet_insert_popover(timeout){
    timeout = timeout || 0;
    setTimeout(function() {
        $( ".snippet-insert-popover" ).each(function(index) {
            $(this).popover({
                html : true,
                trigger: 'click',
                content: function() {
                    var content_id = $(this).attr('data-action-content');
                    return $(content_id).html();
                }
            }).data('bs.popover').tip().addClass('snippet-insert-popover-element');
        });
    }, timeout);
}

// Dropzone stuff
///////////////////////////////////////
function dropzone_attach_to_snippets(timeout) {
    timeout = timeout || 0;
    setTimeout(function() {
        $( ".dropzone" ).each(function(index) {
            ImageDropzone.attach(this);
        });
    }, timeout);
}

var ImageDropzone = function () {

    return {
        attach: function (form_id, options) {

            options = options || {
                autoProcessQueue : true,
                paramName: "file",
                maxFilesize: 15,
                maxFiles: 15,
                parallelUploads: 1,
                acceptedFiles: ".jpeg,.jpg,.png,.gif,.JPEG,.JPG,.PNG,.GIF,.webp",
                dictDefaultMessage: "<strong>OR</strong><br/>Add Image - [ Click / Drag & Drop ]",
            }
            try {
                var imgDropzone = new Dropzone(form_id, options);
                imgDropzone.on("success", function(file, resp) {
                    if (resp.status == 201){
                        add_article_image(resp);
                        toaster('success', resp.message);
                    } else {
                        toaster('warning', resp.message);
                    }
                });

                imgDropzone.on("complete", function(file) {
                  imgDropzone.removeFile(file);
                });
            } catch (error){
                // console.log("Already attached.");
            }
        }
    }
}();

// SWAP / Animation et.c
///////////////////////////////////////
function swap_tr_inplace(tr_element, direction){
    if (direction == 'UP'){
        tr_element.insertBefore( tr_element.prev() );
    } else if (direction == 'DOWN') {
        tr_element.insertAfter( tr_element.next() );
    }
}
function swap_li_inplace(li_element, direction){
    if (direction == 'UP'){
        li_element.insertBefore( li_element.prev() );
    } else if (direction == 'DOWN') {
        li_element.insertAfter( li_element.next() );
    }
}
function replace_html_with_animation(element, html) {
    element.fadeOut('slow', function() {
        element.html(html).fadeOut('slow', function() {;
            $(this).fadeIn('slow', function(){
                toggle_ajax_wheel(element, 'off');
                trigger_partial_page_load_event_backend();
            });
        });
    });
}
function remove_li_from_olist(li_element){
    var count = li_element.siblings('li').length;
    var ol = li_element.closest('ol');

    li_element.hide('slow', function () {
        $(this).remove();
    });
}
function add_article_image(resp){
    var tbody = $('#li-snippet-' + resp.snippet_id + ' .image-table tbody');
    if (resp.status == 201){
        replace_html_with_animation(tbody, resp.html);
    } else {
        toaster('warning', resp.message);
    }
}
function remove_tr_from_table(tr_element){
    var count = tr_element.siblings('tr').length;
    var tbody = tr_element.closest('tbody');

    tr_element.hide('slow', function () {
        $(this).remove();
    });
}

// Form Submitter
///////////////////////////////////////
$(document).on('click', '.form-submitter', function () {
    var me = $(this);
    var target = me.attr('data-target');
    var container = $('#'+target);
    var form = container.find('form:first-of-type');
    var url = form.attr('action') || '';
    var data = form.serialize();

    toggle_ajax_wheel(me, 'on');
    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: data,
        dataType: 'json',
        success: function(result) {
            replace_html_with_animation(container, result.html)
            if (result.status == 200){
                if (result.warning == 1){
                    toaster('warning', result.message);
                } else {
                    toaster('success', result.message);
                }
            } else {
                toaster('warning', result.message);
            }
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});

// Article Update Submitter
///////////////////////////////////////
function append_common_to_autocomplete() {
    $.each([ '#id_categories', '#id_targets', '#id_tags' ], function( idx, val ) {
        var item = $(val);
        var value = item.val();
        if( value && value.length !== 0 && value[value.length - 1] !== ',') {
            item.val( value + ',');
        }
    });
}
function auto_save_snippets_on_action(func, element) {
    var xhr = [];

    $( ".auto-save-snippets-on-action" ).each(function(index) {
        var form = $(this);
        var url = form.attr('action');
        if (url){
            url = url + '/quiet'
            var data = form.serialize();
            var request = $.ajax({
                url: url,
                type: 'POST',
                data: data,
                dataType: 'json',
                cache: false,
            });
            xhr.push(request);
        }
    });

    $.when.apply($, xhr).done(function() {
        func(element)
    });
}
function auto_save_snippets_on_interval(){
    var xhr = [];
    $( ".auto-save-snippets-on-action" ).each(function(index) {
        var form = $(this);
        var url = form.attr('action');
        if (url){
            url = url + '/quiet'
            var data = form.serialize();
            var request = $.ajax({
                url: url,
                type: 'POST',
                data: data,
                dataType: 'json',
            });
        }
    });
}
var auto_save_interval = null;
function start_auto_save() {
    if (!auto_save_interval){
        auto_save_interval = setInterval(function() {
            auto_save_snippets_on_interval();
        }, 8000);
    }
}
function stop_auto_save() {
    auto_save_snippets_on_interval();
    clearInterval(auto_save_interval);
    auto_save_interval = null;
}
$(function() {
    start_auto_save();
    $( document ).idleTimer( { timeout: 47000 } );
    $( document ).on( "active.idleTimer", function(event, elem, obj, triggerevent){
        // the user becomes active again
        console.log('user active')
        start_auto_save();
    });
    $( document ).on( "idle.idleTimer", function(event, elem, obj){
        // the user goes idle
        console.log('user idle');
        stop_auto_save();
    });
});

// Article Add
///////////////////////////////////////
$(document).on('click', '.article-update', function () {
    auto_save_snippets_on_action(article_update, $(this));
});
function article_update(element) {
    append_common_to_autocomplete();

    var me = element
    var target = me.attr('data-target');
    var container = $('#'+target);
    var form = container.find('form:first-of-type');
    var url = form.attr('action') || '';

    toggle_ajax_wheel(me, 'on');

    var data = form.serialize();

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: data,
        dataType: 'json',
        success: function(result) {
            replace_html_with_animation(container, result.html)
            if (result.status == 200){
                if (result.warning){
                    toaster('warning', result.message);
                } else {
                    toaster('success', result.message);
                }
            }
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
};


// Snippet Add
///////////////////////////////////////
var snippet_add_in_progress = false;
$(document).on('click', '.snippet-add, .snippet-insert', function () {
    if (!snippet_add_in_progress){
        snippet_add_in_progress = true;
        auto_save_snippets_on_action(snippet_add, $(this));
    }
});
function snippet_add(element) {
    var me = element
    var url = me.attr('data-url');
    var list = $('#snippet-list');
    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            if (result.status == 201){
                replace_html_with_animation(list, result.html)
                toaster('success', result.message);
            } else {
                toaster('warning', result.message);
            }
            jump_to_smoothly('#li-snippet-'+result.snippet_id, 1000);
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
            setTimeout(function () {
                snippet_add_in_progress = false;
            }, 1000);
        }
    });
}

// Snippet Delete
///////////////////////////////////////
$(document).on('click', '.snippet-deletion-submitter', function () {
    auto_save_snippets_on_action(snippet_delete, $(this));
});
function snippet_delete(element) {
    var me = element
    me.removeClass('.snippet-deletion-submitter');

    var url = me.attr('data-url');
    var li_element = $('#'+me.attr('data-li'));
    toggle_ajax_wheel(me, 'on');

    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    var target = me.attr('data-target');
    var list = $('#snippet-list');

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            toggle_ajax_wheel(me, 'off');
            remove_li_from_olist(li_element);
            replace_html_with_animation(list, result.html)
            toaster('success', result.message);
            jump_to_smoothly('#li-snippet-'+result.snippet_id, 800);
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
};

// Snippet Move UP/DOWN
///////////////////////////////////////
var snippet_sort_in_progress = false;
$(document).on('click', '.snippet-sort-submitter', function () {
    if (!snippet_sort_in_progress){
        snippet_sort_in_progress = true;
        auto_save_snippets_on_action(snippet_sort, $(this));
    }
});
function snippet_sort(element) {
    var me = element
    var url = me.attr('data-url');
    var direction = me.attr('data-direction');
    var li_element = $('#'+me.attr('data-li'));

    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    var list = $('#snippet-list');

    toggle_ajax_wheel(me, 'on');

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            swap_li_inplace(li_element, direction);
            replace_html_with_animation(list, result.html)
            toaster('success', result.message);
            jump_to_smoothly('#li-snippet-'+result.snippet_id);
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
            setTimeout(function () {
                snippet_sort_in_progress = false;
            }, 1000);
        }
    });
}

$(document).on('click', '.image-add-submitter', function () {
    var me = $(this);
    var image_link = $(me.attr('data-link'));
    if (!image_link || image_link.val() === '') {
        return false
    }
    var form = me.closest('form');
    var url = form.attr('action') || '';
    var data = form.serialize();

    var spinner = form.find('.fa-picture-o').first();
    toggle_ajax_wheel(spinner, 'on');

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000000,
        data: data,
        dataType: 'json',
        success: function(result) {
            if (result.status == 201){
                image_link.val('');
                add_article_image(result)
                toaster('success', result.message);
            } else {
                toaster('warning', result.message);
            }
        },
        error: function(result) {
            resp = JSON.parse(result.responseText);
            var msg = resp.message || 'Operation Failed.';
            toaster('error', msg);
        },
        complete: function(result) {
            toggle_ajax_wheel(spinner, 'off');
        }
    });
});

// Image Delete
///////////////////////////////////////
function remove_from_table(tr_element, tbody, html){
    tr_element.hide('slow', function () {
        $(this).remove();
        replace_html_with_animation(tbody, html)
    });
}
$(document).on('click', '.image-deletion-submitter', function () {
    var me = $(this);
    me.removeClass('.image-deletion-submitter');

    var url = me.attr('data-url');
    var tr_element = $('#'+me.attr('data-tr'));
    toggle_ajax_wheel(me, 'on');

    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    var tbody = tr_element.closest('tbody');

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            toggle_ajax_wheel(me, 'off');
            tr_element.backgroundFlashFade(100, '#F9F9DE');
            remove_from_table(tr_element, tbody, result.html);
            toaster('success', 'Image removed.');
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});

// Image Move UP/DOWN
///////////////////////////////////////
$(document).on('click', '.image-sort-submitter', function () {
    var me = $(this);

    var url = me.attr('data-url');
    var direction = me.attr('data-direction');
    var tr_element = $('#'+me.attr('data-tr'));
    toggle_ajax_wheel(me, 'on');

    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    var tbody = tr_element.closest('tbody');

    toggle_ajax_wheel(me, 'on');
    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            swap_tr_inplace(tr_element, direction);
            replace_html_with_animation(tbody, result.html)
            tr_element.backgroundFlashFade(8000, '#F9F9DE');
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});


// Image Preview Modal
///////////////////////////////////////
$(document).on('click', '.image-preview-modal-trigger', function () {
    var me = $(this);
    var isrc = me.attr('data-isrc');
    var anchor = $('#image-preview-modal a');
    var image = $('#image-preview-modal img');
    anchor.attr('href', isrc);
    image.attr('src', isrc);
});
$(document).on('hidden.bs.modal', '#image-preview-modal', function () {
    var me = $(this);
    var image = $('#image-preview-modal img');
    image.attr('src', '');
});


// Video Add
///////////////////////////////////////
// $(document).on('keypress', function (e) {
//     if (e.keyCode == 13) { // enter
//         $( ".video-modal" ).each(function( idx ) {
//             if ($(this).is(':visible')) {
//                 return false
//             }
//         });
//     }
// });
$(document).on('click', '.video-add-submitter', function () {
    var me = $(this);
    var url = me.attr('data-url');
    var snippet = me.attr('data-snippet');
    var box = me.closest('.video-add-box');
    var csrf = $('form#csrf_post_form input').val();
    var link = $(me.attr('data-link'));
    if (!link || link.val() === '') {
        return false
    }
    var postdata = {
        csrfmiddlewaretoken: csrf,
        snippet: snippet,
        link: link.val()
    };

    var tbody = box.find('.video-table tbody');
    var spinner = box.find('.fa-video-camera').first();
    toggle_ajax_wheel(spinner, 'on');

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            if (result.status == 201){
                link.val('');
                replace_html_with_animation(tbody, result.html)
            } else {
                toaster('warning', result.message);
            }
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
            toggle_ajax_wheel(spinner, 'off');
        }
    });
});

// Video Delete
///////////////////////////////////////
function remove_video_from_table(tr_element, tbody, html){
    tr_element.hide('slow', function () {
        $(this).remove();
        replace_html_with_animation(tbody, html)
    });
}
$(document).on('click', '.video-deletion-submitter', function () {
    var me = $(this);
    me.removeClass('.video-deletion-submitter');

    var url = me.attr('data-url');
    var tr_element = $('#'+me.attr('data-tr'));
    toggle_ajax_wheel(me, 'on');

    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    var tbody = tr_element.closest('tbody');

    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            toggle_ajax_wheel(me, 'off');
            tr_element.backgroundFlashFade(100, '#F9F9DE');
            remove_from_table(tr_element, tbody, result.html);
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});

// Video Move UP/DOWN
///////////////////////////////////////
$(document).on('click', '.video-sort-submitter', function () {
    var me = $(this);

    var url = me.attr('data-url');
    var direction = me.attr('data-direction');
    var tr_element = $('#'+me.attr('data-tr'));
    toggle_ajax_wheel(me, 'on');

    csrf = $('form#csrf_post_form input').val();
    var postdata = {csrfmiddlewaretoken: csrf };

    var tbody = tr_element.closest('tbody');

    toggle_ajax_wheel(me, 'on');
    $.ajax({
        url: url,
        type: 'POST',
        timeout: 8000,
        data: postdata,
        dataType: 'json',
        success: function(result) {
            swap_tr_inplace(tr_element, direction);
            replace_html_with_animation(tbody, result.html);
            tr_element.backgroundFlashFade(9000, '#F9F9DE');
        },
        error: function(result) {
            toaster('error', 'Operation Failed.');
        },
        complete: function(result) {
        }
    });
});

// Video Preview Modal
///////////////////////////////////////
$(document).on('click', '.video-preview-modal-trigger', function () {
    var me = $(this);
    var vsrc = me.attr('data-vsrc');
    var provider = me.attr('data-provider');
    var modal_body = $('#video-preview-modal .modal-body');

    var directives = 'frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen'
    switch(provider.toLowerCase()) {
        case 'youtube':
            vsrc += '?rel=0';
            break;
        case 'vimeo':
            break;
        default:
    }

    var iframe = '<iframe class="embed-responsive-item" src="'+vsrc+'" ' +directives+'></iframe>'
    modal_body.html(iframe);
});

$(document).on('hidden.bs.modal', '#video-preview-modal', function () {
    var me = $(this);
    var modal_body = $('#video-preview-modal .modal-body');
    modal_body.html('');
});
