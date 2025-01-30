document.addEventListener('DOMContentLoaded', function () {
    console.log('Script cargado'); // Para verificar que el script se carga

    const form = document.getElementById('deleteForm');
    console.log('Formulario encontrado:', form); // Para verificar que encuentra el form

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault(); // Detiene el envío del formulario hasta que el usuario confirme

            if (confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
                form.submit(); // Solo envía si el usuario confirma
            }
        });
    }
});