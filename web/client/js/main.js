(function() {
    let infoBox;
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

    function reportSuccess(success) {
        infoBox.classList.remove('hidden');
        infoBox.classList.remove('error');
        infoBox.classList.add('success');
        infoBox.innerHTML = success;
    }

    function markErrorField(field) {
        form.elements[field].classList.add('error');
    }

    function reportError(error) {
        infoBox.innerHTML = error.message;
        infoBox.classList.remove('hidden');
        infoBox.classList.remove('success');
        infoBox.classList.add('error');
        flashForm('error-flash');
        if (error.code === 0) {
            markErrorField(error.data.field)
        }
    }

    function clearInfo() {
        infoBox.classList.add('hidden');
        for (let field of form.elements) {
            field.classList.remove('error');
        }
    }

    function flashForm(className) {
        form.classList.add(className);
        setTimeout(() => {
            form.classList.remove(className);
        }, 200);
    }

    window.onload = () => {
        infoBox = document.getElementById('info-box');
        form = document.getElementById('set-location-form');

        form.addEventListener('submit', async ev => {
            ev.preventDefault();
            const formData = new FormData(ev.currentTarget);
            const region = formData.get('region');
            const municipality = formData.get('kommune');
            const location = formData.get('lokasjon');

            const result = await setLocation(region, municipality, location);
            if (result.ok) {
                reportSuccess('Fant sted - oppdaterer skjerm');
            } else {
                const body = await result.text();
                let error;
                try {
                    error = JSON.parse(body);
                } catch (SyntaxError) {
                    error = {
                        message: body,
                        code: -1
                    };
                }
                reportError(error);
            }
        });
        form.addEventListener('input', ev => {
            clearInfo();
        });
    }
})();
