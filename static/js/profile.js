// página de perfil: guarda o nome no localStorage e volta pro quadro de doações
var profileForm = document.getElementById('profile-form');
var profileNameInput = document.getElementById('profile-name');

profileNameInput.value = localStorage.getItem('person_name') || '';

profileForm.addEventListener('submit', function (event) {
    event.preventDefault();
    var name = profileNameInput.value.trim();
    if (!name) return;
    localStorage.setItem('person_name', name);
    window.location.href = profileForm.dataset.next;
});
