window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const gas = L.icon({
                iconUrl: `https://img.icons8.com/ios-filled/344/gas.png`,
                iconSize: [64, 48]
            });
            return L.marker(latlng, {
                icon: gas
            });
        }
    }
});