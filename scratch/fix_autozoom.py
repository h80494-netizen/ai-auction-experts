path = 'public/map.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """            const unexecutedOnly = document.getElementById('toggle-unexecuted-auctions') ? document.getElementById('toggle-unexecuted-auctions').checked : false;
            if (data.length === 1 && unexecutedOnly) {
                map.setView([data[0].lat, data[0].lng], 16);
                setTimeout(() => {
                    layers.auction.eachLayer(layer => {
                        if (layer.auctionData && layer.auctionData.id === data[0].id) {
                            layer.openPopup();
                        }
                    });
                }, 500);
            }"""

new_logic = """            const unexecutedOnly = document.getElementById('toggle-unexecuted-auctions') ? document.getElementById('toggle-unexecuted-auctions').checked : false;
            if (data.length === 1 && unexecutedOnly) {
                if (window._lastAutoZoomId !== data[0].id) {
                    window._lastAutoZoomId = data[0].id;
                    map.setView([data[0].lat, data[0].lng], 16);
                    setTimeout(() => {
                        layers.auction.eachLayer(layer => {
                            if (layer.auctionData && layer.auctionData.id === data[0].id) {
                                layer.openPopup();
                            }
                        });
                    }, 500);
                }
            } else {
                window._lastAutoZoomId = null;
            }"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Auto-zoom loop fixed")
else:
    print("Old logic not found")
