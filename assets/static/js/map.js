var map_view_list = {};

function set_map_params(id, data) {
    // get map info from snippet's `content` field

    instance = get_defaults(id);
    info = JSON.parse(data);

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
    instance.mapTypeId = info.mapTypeId;
    instance.mapCenter = new google.maps.LatLng(info.mapCenter.lat, info.mapCenter.lng);
    instance.markerPosition = new google.maps.LatLng(info.markerPosition.lat, info.markerPosition.lng);
}

function get_defaults(id){
    var defaults = {
        id: id,
        canvas: 'map-canvas-' + id,
    };
    if (!(id in map_view_list)) {
        map_view_list[id] = defaults;
    }
    return map_view_list[id];
}

function add_marker(instance){
    // create a marker for map and initialize it

    var marker_options = {
        map: instance.mapObj,
        draggable: false,
        position: instance.mapObj.getCenter()
    }
    instance.markerObj = new google.maps.Marker(marker_options);
}

function set_map_control(instance){
    var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    if (isTouch) {
        var isDraggable = w > 480 ? true : false;
        var clickZoom = !isDraggable
        var streetView = isDraggable
        instance.mapObj.setOptions({
            draggable: isDraggable,
            disableDoubleClickZoom: clickZoom,
            streetViewControl: streetView
        });
    }
}

function add_map(instance) {
    // create a map instance, initialize or set to save values

    var map_options = {
        minzoom: 3,
        maxzoom: 18,
        zoom: instance.mapZoom,
        center: instance.mapCenter,
        disableDefaultUI: false,
        mapTypeControlOptions: {
            mapTypeIds: [
            google.maps.MapTypeId.SATELLITE,
            google.maps.MapTypeId.ROADMAP,
            google.maps.MapTypeId.HYBRID,
            google.maps.MapTypeId.TERRAIN]
        },
        mapTypeId: instance.mapTypeId,
        streetViewControl: true,
        zoomControl: true,
        scrollwheel: false,
        linksControl: false,
    };
    instance.mapObj = new google.maps.Map(document.getElementById(instance.canvas), map_options);
    instance.mapObj.setTilt(instance.mapTilt);
    instance.mapObj.setHeading(instance.mapHeading);
    set_map_control(instance);

    google.maps.event.addDomListener(window, "resize", function() {
        var center = instance.mapCenter;
        google.maps.event.trigger(instance.mapObj, "resize");
        instance.mapObj.setCenter(center);
        set_map_control(instance);
    });

    add_marker(instance);
}

function maps_load(timeout){
    timeout = timeout || 0;
    setTimeout(function () {
        for (var key in map_view_list) {
            var instance = map_view_list[key];
            add_map(instance);
        }
    }, timeout);
}
