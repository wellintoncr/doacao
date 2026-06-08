// guarda o nome do voluntário pra ele digitar só uma vez em cada aparelho
function fillNames(root) {
    var name = localStorage.getItem('person_name');
    if (!name) return;
    root.querySelectorAll('input[data-remember-name]').forEach(function (input) {
        if (!input.value) input.value = name;
    });
}

document.body.addEventListener('htmx:afterSwap', function (event) {
    fillNames(event.target);
});

document.body.addEventListener('submit', function (event) {
    var input = event.target.querySelector('input[data-remember-name]');
    if (input && input.value) localStorage.setItem('person_name', input.value);
});

fillNames(document);
