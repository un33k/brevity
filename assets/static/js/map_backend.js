var map_list = {};
var marker_always_center = true;

function get_map_info(instance) {
    // get map info from snippet's `content` input field

    var content = $(instance.snippet_element).find(instance.content_element);
    var params = content.val();
    var info = {};
    if (params){
        info = JSON.parse(params);
    } else {
        info = {};
    }
    info.mapZoom = info.mapZoom || 3;
    info.mapTilt = info.mapTilt || 0;
    info.mapHeading = info.mapHeading || 0;
    info.searchText = info.searchText || '';
    info.mapTypeId = info.mapTypeId || google.maps.MapTypeId.ROADMAP;
    info.mapCenter = info.mapCenter || {lat: 0.0, lng: 0.0};
    info.markerPosition = info.markerPosition || {lat: 0.0, lng: 0.0};

    instance.mapZoom = info.mapZoom;
    instance.mapTilt = info.mapTilt;
    instance.mapHeading = info.mapHeading;
    instance.searchText = info.searchText;
    instance.mapTypeId = info.mapTypeId;
    instance.mapCenter = new google.maps.LatLng(info.mapCenter.lat, info.mapCenter.lng);
    instance.markerPosition = new google.maps.LatLng(info.markerPosition.lat, info.markerPosition.lng);

    content.val(JSON.stringify(info));
    return info
}

function set_map_info(instance) {
    // initialize and/or set map into snippet's `content` input field

    instance.searchText = document.getElementById(instance.input).value;

    if (!('mapZoom' in instance)) {
        instance.mapZoom = 3;
    }
    if ('mapObj' in instance) {
        instance.mapCenter = instance.mapObj.getCenter();

        if (!('markerPosition' in instance)) {
            instance.markerPosition = instance.mapObj.getCenter();
        }
        instance.mapTilt = instance.mapObj.getTilt() || 0;
        instance.mapHeading = instance.mapObj.getHeading() || 0;
    }

    info = {}
    info.searchText = instance.searchText;
    info.markerPosition = instance.markerPosition;
    info.mapCenter = instance.mapCenter;
    info.mapZoom = instance.mapZoom;
    info.mapTypeId = instance.mapTypeId;
    info.mapTilt = instance.mapTilt;
    info.mapHeading = instance.mapHeading;

    var content = $(instance.snippet_element).find(instance.content_element);
    content.val(JSON.stringify(info));
}

function marker_event_handlers_init(instance) {
    // add desired event handlers for this marker instance

    if ('markerObj' in instance) {
        google.maps.event.addListener(instance.markerObj , 'dragend', function(event) {
            instance.markerPosition = event.latLng;
            if (marker_always_center){
                instance.mapObj.setCenter(instance.markerPosition);
            }
            set_map_info(instance);
        });
    }
}

function position_marker(instance, move_center) {
    // set marker to new position or mapCenter of the map

    move_center = move_center || false;
    if ('markerObj' in instance) {
        if (move_center || !('markerPosition' in instance)) {
            instance.markerPosition = instance.mapObj.getCenter();
        }
        instance.markerObj.setPosition(instance.markerPosition);
        set_map_info(instance);
    }
}

function create_marker(instance){
    // create a marker for map and initialize it

    if ('markerObj' in instance) {
        google.maps.event.clearListeners(instance.markerObj);
        instance.markerObj = null;
    }

    var marker_options = {
        map: instance.mapObj,
        draggable: true,
    }
    instance.markerObj = new google.maps.Marker(marker_options);

    marker_event_handlers_init(instance);
    position_marker(instance);
}


function map_event_handlers_init(instance) {
    // add desired event handlers for this map instance

    if ('mapObj' in instance) {

        instance.mapObj.setTilt(instance.mapTilt);
        google.maps.event.addListener(instance.mapObj , 'tilt_changed', function(event) {
            instance.mapTilt = instance.mapObj.getTilt();
            set_map_info(instance);
        });

        instance.mapObj.setHeading(instance.mapHeading);
        google.maps.event.addListener(instance.mapObj , 'heading_changed', function(event) {
            instance.mapHeading = instance.mapObj.getHeading();
            set_map_info(instance);
        });

        google.maps.event.addListener(instance.mapObj , 'zoom_changed', function(event) {
            instance.mapZoom = instance.mapObj.getZoom();
            set_map_info(instance);
        });

        google.maps.event.addListener(instance.mapObj, 'dragend', function(event) {
            instance.mapCenter = instance.mapObj.getCenter();
            if (marker_always_center){
                position_marker(instance, true)
            }
            set_map_info(instance);
        });

        google.maps.event.addDomListener(window, "resize", function(event) {
            var center = instance.mapCenter;
            google.maps.event.trigger(instance.mapObj, "resize");
            instance.mapObj.setCenter(center);
        });

        google.maps.event.addListener(instance.mapObj, 'maptypeid_changed', function(event) {
            instance.mapTypeId = instance.mapObj.getMapTypeId();
            set_map_info(instance);
        });
    }
}

function create_map(instance) {
    // create a map instance, initialize or set to save values

    var info = get_map_info(instance);
    var map_options = {
        minzoom: 3,
        maxzoom: 18,
        zoom: info.mapZoom,
        center: new google.maps.LatLng(info.mapCenter.lat, info.mapCenter.lng),
        disableDefaultUI: false,
        mapTypeControlOptions: {
            mapTypeIds: [
            google.maps.MapTypeId.SATELLITE,
            google.maps.MapTypeId.ROADMAP,
            google.maps.MapTypeId.HYBRID,
            google.maps.MapTypeId.TERRAIN]
        },
        mapTypeId: info.mapTypeId,
        streetViewControl: false,
        zoomControl: true,
        scrollwheel: false
    };

    var canvas_div = document.getElementById(instance.canvas);
    if ('mapObj' in instance) {
        google.maps.event.clearListeners(instance.mapObj);
        instance.mapObj = null;
    }
    instance.mapObj = new google.maps.Map(canvas_div, map_options);
    map_event_handlers_init(instance);
    create_marker(instance);
    set_map_info(instance);
}

function autocomplete_event_handler_init(instance) {
    // initialize autocomplete event listener

    if ('autocomplete' in instance) {
        google.maps.event.clearListeners(instance.autocomplete);
        instance.autocomplete = null;
    }

    var input = document.getElementById(instance.input);
    var autocomplete = new google.maps.places.Autocomplete(input);
    autocomplete.bindTo('bounds', instance.mapObj);

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            toaster('warning', 'Location was not found.');
        } else {
            if (place.geometry.viewport) {
                instance.mapObj.fitBounds(place.geometry.viewport);
            } else {
                instance.mapObj.setCenter(place.geometry.location);
                instance.mapObj.setZoom(12);
            }
            position_marker(instance, true);
        }
        set_map_info(instance);
    });
}

function maps_reload(timeout){
    timeout = timeout || 200;
    setTimeout(function () {
        $( ".map-canvas" ).each(function(index) {
            var me = $(this);
            var id = me.attr('data-snippet-id');
            map_init(id)
        });
    }, timeout);
}

function get_defaults(id){
    var defaults = {
        id: id,
        input: 'map-input-' + id,
        canvas: 'map-canvas-' + id,
        snippet_element: '#target-snippet-' + id,
        content_element: '#id_content'
    };
    if (!(id in map_list)) {
        map_list[id] = defaults;
    }
    return map_list[id];
}

function map_init(id){
    var instance = get_defaults(id);
    create_map(instance);
    autocomplete_event_handler_init(instance);
}
