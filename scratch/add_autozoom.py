path = 'public/map.html'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(3545, 3550):
    if 'triggerHighlighter();' in lines[i]:
        idx = i
        lines.insert(idx, """            const unexecutedOnly = document.getElementById('toggle-unexecuted-auctions') ? document.getElementById('toggle-unexecuted-auctions').checked : false;
            if (data.length === 1 && unexecutedOnly) {
                map.setView([data[0].lat, data[0].lng], 16);
                setTimeout(() => {
                    layers.auction.eachLayer(layer => {
                        if (layer.auctionData && layer.auctionData.id === data[0].id) {
                            layer.openPopup();
                        }
                    });
                }, 500);
            }\n""")
        break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Auto-zoom logic added")
