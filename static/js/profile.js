// o quadro de doações ainda lê o nome do localStorage; aqui a gente mantém
// os dois em sincronia com o que tá salvo na conta
var nameInput = document.getElementById('id_name');
if (nameInput && nameInput.value) {
    localStorage.setItem('person_name', nameInput.value);
}
