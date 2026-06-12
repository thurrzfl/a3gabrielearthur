// 1. Nova função de cadastro SEM JSON (Usa FormData agora)
async function cadastrarUsuario() {
    const userInp = document.getElementById('reg-user').value;
    const passInp = document.getElementById('reg-pass').value;

    // Criamos um FormData em vez de um objeto/JSON
    const formData = new FormData();
    formData.append("username", userInp);
    formData.append("password", passInp);

    try {
        const resposta = await fetch(`${URL_API}/signup`, {
            method: "POST",
            body: formData // Enviado como dados de formulário puro!
        });

        const resultado = await resposta.json();
        
        if (resposta.ok) {
            alert(resultado.message);
        } else {
            alert("Erro: " + resultado.detail);
        }
    } catch (erro) {
        alert("Não foi possível conectar ao servidor back-end.");
    }
}