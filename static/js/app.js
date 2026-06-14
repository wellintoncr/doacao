// preenche os campos escondidos de nome com o que tá salvo no perfil
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

fillNames(document);

// mostra quem tá logado (bom, "logado") no link do perfil
var profileLink = document.getElementById('profile-link');
var profileName = localStorage.getItem('person_name');
if (profileLink && profileName) {
    profileLink.textContent = 'Perfil · ' + profileName;
}
