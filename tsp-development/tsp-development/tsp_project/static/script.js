var map = new MapmyIndia.Map('map', {
    center: [28.09, 78.3],
    zoom: 5,
    search: false
});

/*Search plugin initialization*/
var optional_config = {
    location: [28.61, 77.23],
    /* pod:'City',
     bridge:true,
     tokenizeAddress:true,*
     filter:'cop:9QGXAM',
     distance:true,
     width:300,
     height:300*/
};
new MapmyIndia.search(document.getElementById("auto"), optional_config, callback);

/*CALL for fix text - LIKE THIS
 * 
 new MapmyIndia.search("agra",optional_config,callback);
 * 
 * */
let loc = "";
map.addEventListener("click", function (e) {
    var pt = e.latlng; //event returns lat lng of clicked point
    console.log(pt);
    L.marker([pt.lat, pt.lng]).addTo(map);
    loc += pt.lng + "," + pt.lat + ";";
    //Do your related operation here
});
var marker;

function callback(data) {
    if (data) {
        if (data.error) {
            if (data.error.indexOf('responsecode:401') !== -1) {
                /*TOKEN EXPIRED, set new Token ie. 
                 * MapmyIndia.setToken(newToken);
                 */
            }
            console.warn(data.error);

        } else {
            var dt = data[0];
            if (!dt) return false;
            var eloc = dt.eLoc;
            var lat = dt.latitude,
                lng = dt.longitude;

            var place = dt.placeName + (dt.placeAddress ? ", " + dt.placeAddress : "");
            /*Use elocMarker Plugin to add marker*/
            if (marker) marker.remove();
            if (eloc) marker = new MapmyIndia.elocMarker({
                map: map,
                eloc: lat ? lat + "," + lng : eloc,
                popupHtml: place,
                popupOptions: {
                    openPopup: true
                }
            }).fitbounds();
            new MapmyIndia.elocMarker({
                map: map,
                eloc: "28.408389744145275" ? "28.408389744145275" + "," + "79.18769359588624" : eloc
            });
            // lat: 28.408389744145275


        }
    }
}
const submitBtn = document.getElementsByClassName('submit-btn')[0]

submitBtn.addEventListener('click', async function () {
    console.log('clicked')
    const res = await fetch(`http://127.0.0.1:5000/api?loc=${loc}`)
    const data = await res.json()
    console.log(data)
    setTimeout(() => {
        window.location.href = `http://127.0.0.1:5000/result?data=${data.cord}`
    }, 1000)
})