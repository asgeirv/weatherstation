(function() {
    let errorBox;
    let form;

    function setLocation(region, municipality, location) {
        const queryString = [
            ['region', region],
            ['kommune', municipality],
            ['lokasjon', location]
        ].map(param => param.map(encodeURIComponent).join('=')).join('&')
        return fetch('/sted?' + queryString, {
            method: 'POST'
        });
    }

    function reportError(error) {
        errorBox.innerHTML = error;
        errorBox.classList.remove('hidden');
        flashForm();
    }

    function clearError() {
        errorBox.classList.add('hidden');
    }

    function flashForm() {
        form.classList.add('error-flash');
        setTimeout(() => {
            form.classList.remove('error-flash');
        }, 200);
    }

    window.onload = () => {
        errorBox = document.getElementById('error-box');
        form = document.getElementById('set-location-form');

        form.addEventListener('submit', async ev => {
            ev.preventDefault();
            const formData = new FormData(ev.currentTarget);
            const region = formData.get('region');
            const municipality = formData.get('municipality');
            const location = formData.get('location');

            try {
                const result = await setLocation(region, municipality, location);
                if (!result.ok) {
                    reportError(await result.text());
                }
            } catch {
                console.log("Error");
            }
        });
        form.addEventListener('input', ev => {
            clearError();
        });
    }
})();
