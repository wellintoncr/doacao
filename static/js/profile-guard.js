// sem nome salvo não tem doação: manda pro perfil antes da página nem pintar
if (!localStorage.getItem('person_name')) {
    window.location.replace('/profile/');
}
