async function setLocation(region, municipality, location) {
    const queryString = [
        ['region', region],
        ['kommune', municipality],
        ['lokasjon', location]
    ].map(param => param.join('=')).join('&')
    return await fetch('/sted?' + queryString, {
        method: 'POST'
    });
}

window.onload = () => {
    document.getElementById('set-location-form').addEventListener('submit', async ev => {
        ev.preventDefault();
        const formData = new FormData(ev.currentTarget);
        const region = formData.get('region');
        const municipality = formData.get('municipality');
        const location = formData.get('location');

        try {
            const result = await setLocation(region, municipality, location);
        } catch {
            console.log("Error");
        }
    });
}
