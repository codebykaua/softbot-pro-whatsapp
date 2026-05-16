const TOKEN_KEY = "softbot_token";
const PERFIL_KEY = "softbot_perfil";

let mensagensCache = [];
let usuariosCache = [];

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function salvarToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function removerToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function salvarPerfil(perfil) {
  localStorage.setItem(PERFIL_KEY, perfil);
}

function getPerfil() {
  return localStorage.getItem(PERFIL_KEY);
}

function removerPerfil() {
  localStorage.removeItem(PERFIL_KEY);
}

function authHeaders() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${getToken()}`
  };
}

function protegerPagina() {
  const paginaAtual = window.location.pathname.split("/").pop();
  const token = getToken();

  if (paginaAtual === "login.html") {
    if (token) {
      window.location.href = "index.html";
    }
    return;
  }

  if (!token) {
    window.location.href = "login.html";
  }
}

function sair() {
  removerToken();
  removerPerfil();
  window.location.href = "login.html";
}

function aplicarPermissoesFrontEnd() {
  const perfil = getPerfil();

  const linksUsuarios = document.querySelectorAll('a[href="usuarios.html"]');
  const elementosAdmin = document.querySelectorAll(".admin-only");

  if (perfil !== "admin") {
    linksUsuarios.forEach((link) => {
      link.style.display = "none";
    });

    elementosAdmin.forEach((elemento) => {
      elemento.style.display = "none";
    });
  } else {
    linksUsuarios.forEach((link) => {
      link.style.display = "";
    });

    elementosAdmin.forEach((elemento) => {
      elemento.style.display = "";
    });
  }
}

async function fazerLogin() {
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const erroLogin = document.getElementById("erroLogin");

  if (!usernameInput || !passwordInput || !erroLogin) return;

  const username = usernameInput.value.trim();
  const password = passwordInput.value.trim();

  if (!username || !password) {
    erroLogin.classList.remove("hidden");
    erroLogin.innerText = "Preencha usuário e senha.";
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        username: username,
        password: password
      })
    });

    if (!resposta.ok) {
      throw new Error("Login inválido.");
    }

    const dados = await resposta.json();

    salvarToken(dados.access_token);
    salvarPerfil(dados.perfil);

    window.location.href = "index.html";
  } catch (erro) {
    erroLogin.classList.remove("hidden");
    erroLogin.innerText = "Usuário ou senha inválidos.";
  }
}

function verificarErroAuth(resposta) {
  if (resposta.status === 401 || resposta.status === 403) {
    removerToken();
    removerPerfil();
    window.location.href = "login.html";
    return true;
  }

  return false;
}

async function enviarMensagem() {
  const telefoneInput = document.getElementById("telefone");
  const mensagemInput = document.getElementById("mensagem");
  const respostaBot = document.getElementById("respostaBot");

  if (!telefoneInput || !mensagemInput || !respostaBot) return;

  const telefone = telefoneInput.value.trim();
  const mensagem = mensagemInput.value.trim();

  if (!telefone || !mensagem) {
    respostaBot.classList.remove("hidden");
    respostaBot.innerText = "Preencha o telefone e a mensagem antes de enviar.";
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/webhook`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        telefone: telefone,
        mensagem: mensagem
      })
    });

    if (!resposta.ok) {
      throw new Error("Erro ao enviar mensagem.");
    }

    const dados = await resposta.json();

    respostaBot.classList.remove("hidden");
    respostaBot.innerText = `${dados.resposta}\n\nStatus: ${dados.status}`;

    mensagemInput.value = "";

    carregarResumoDashboard();
    carregarMensagens();
  } catch (erro) {
    respostaBot.classList.remove("hidden");
    respostaBot.innerText = "Erro ao conectar com a API. Verifique se o servidor está rodando.";
  }
}

async function cadastrarFaq() {
  const palavraChaveInput = document.getElementById("palavraChave");
  const perguntaInput = document.getElementById("pergunta");
  const respostaFaqInput = document.getElementById("respostaFaq");
  const alertaFaq = document.getElementById("alertaFaq");

  if (!palavraChaveInput || !perguntaInput || !respostaFaqInput || !alertaFaq) return;

  const palavraChave = palavraChaveInput.value.trim();
  const pergunta = perguntaInput.value.trim();
  const respostaFaq = respostaFaqInput.value.trim();

  if (!palavraChave || !pergunta || !respostaFaq) {
    alertaFaq.classList.remove("hidden");
    alertaFaq.innerText = "Preencha todos os campos da FAQ.";
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/faqs`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        palavra_chave: palavraChave,
        pergunta: pergunta,
        resposta: respostaFaq
      })
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alertaFaq.classList.remove("hidden");
      alertaFaq.innerText = dados.detail || "Erro ao cadastrar FAQ.";
      return;
    }

    alertaFaq.classList.remove("hidden");
    alertaFaq.innerText = "FAQ cadastrada com sucesso!";

    palavraChaveInput.value = "";
    perguntaInput.value = "";
    respostaFaqInput.value = "";

    carregarFaqs();
    carregarResumoDashboard();
  } catch (erro) {
    alertaFaq.classList.remove("hidden");
    alertaFaq.innerText = "Erro ao cadastrar FAQ. Verifique se a API está rodando.";
  }
}

async function carregarResumoDashboard() {
  const listaMensagensResumo = document.getElementById("listaMensagensResumo");
  const totalMensagens = document.getElementById("totalMensagens");
  const totalRespondidas = document.getElementById("totalRespondidas");
  const totalPendentes = document.getElementById("totalPendentes");
  const totalEncaminhadas = document.getElementById("totalEncaminhadas");
  const totalFinalizadas = document.getElementById("totalFinalizadas");

  try {
    const resposta = await fetch(`${API_URL}/mensagens`, {
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    if (!resposta.ok) {
      throw new Error("Erro ao carregar resumo.");
    }

    const mensagens = await resposta.json();

    const respondidas = mensagens.filter((item) => item.status === "respondido").length;
    const pendentes = mensagens.filter((item) => item.status === "pendente").length;
    const encaminhadas = mensagens.filter((item) => item.status === "encaminhado").length;
    const finalizadas = mensagens.filter((item) => item.status === "finalizado").length;

    if (totalMensagens) {
      totalMensagens.innerText = mensagens.length;
    }

    if (totalRespondidas) {
      totalRespondidas.innerText = respondidas;
    }

    if (totalPendentes) {
      totalPendentes.innerText = pendentes;
    }

    if (totalEncaminhadas) {
      totalEncaminhadas.innerText = encaminhadas;
    }

    if (totalFinalizadas) {
      totalFinalizadas.innerText = finalizadas;
    }

    if (!listaMensagensResumo) return;

    if (mensagens.length === 0) {
      listaMensagensResumo.innerHTML = `
        <tr>
          <td colspan="4" class="empty-text">Nenhuma mensagem cadastrada.</td>
        </tr>
      `;
      return;
    }

    const ultimas = mensagens.slice(0, 5);

    listaMensagensResumo.innerHTML = ultimas.map((item) => `
      <tr>
        <td>${item.id}</td>
        <td>${item.telefone}</td>
        <td>${item.mensagem_recebida}</td>
        <td>
          <span class="status-badge status-${item.status}">
            ${item.status}
          </span>
        </td>
      </tr>
    `).join("");
  } catch (erro) {
    if (listaMensagensResumo) {
      listaMensagensResumo.innerHTML = `
        <tr>
          <td colspan="4">Erro ao carregar mensagens.</td>
        </tr>
      `;
    }
  }
}

async function carregarMensagens() {
  const listaMensagens = document.getElementById("listaMensagens");

  if (!listaMensagens) return;

  try {
    const resposta = await fetch(`${API_URL}/mensagens`, {
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    if (!resposta.ok) {
      throw new Error("Erro ao carregar mensagens.");
    }

    const mensagens = await resposta.json();

    mensagensCache = mensagens;

    renderizarMensagens(mensagensCache);
  } catch (erro) {
    listaMensagens.innerHTML = `
      <tr>
        <td colspan="7">Erro ao carregar mensagens.</td>
      </tr>
    `;
  }
}

function renderizarMensagens(mensagens) {
  const listaMensagens = document.getElementById("listaMensagens");

  if (!listaMensagens) return;

  if (mensagens.length === 0) {
    listaMensagens.innerHTML = `
      <tr>
        <td colspan="7" class="empty-text">Nenhuma mensagem encontrada.</td>
      </tr>
    `;
    return;
  }

  listaMensagens.innerHTML = mensagens.map((item) => `
    <tr>
      <td>${item.id}</td>
      <td>${item.telefone}</td>
      <td>${item.mensagem_recebida}</td>
      <td>${item.resposta_enviada}</td>
      <td>
        <select 
          class="status-select status-${item.status}" 
          onchange="atualizarStatus(${item.id}, this.value)"
        >
          <option value="respondido" ${item.status === "respondido" ? "selected" : ""}>respondido</option>
          <option value="pendente" ${item.status === "pendente" ? "selected" : ""}>pendente</option>
          <option value="encaminhado" ${item.status === "encaminhado" ? "selected" : ""}>encaminhado</option>
          <option value="finalizado" ${item.status === "finalizado" ? "selected" : ""}>finalizado</option>
        </select>
      </td>
      <td class="data-text">${formatarData(item.criado_em)}</td>
      <td>
        <button class="btn-danger btn-small admin-only" onclick="excluirMensagem(${item.id})">
          Excluir
        </button>
      </td>
    </tr>
  `).join("");

  aplicarPermissoesFrontEnd();
}

function aplicarFiltrosMensagens() {
  const filtroBuscaInput = document.getElementById("filtroBusca");
  const filtroStatusInput = document.getElementById("filtroStatus");

  if (!filtroBuscaInput || !filtroStatusInput) return;

  const busca = filtroBuscaInput.value.toLowerCase().trim();
  const status = filtroStatusInput.value;

  const mensagensFiltradas = mensagensCache.filter((item) => {
    const telefone = String(item.telefone || "").toLowerCase();
    const mensagem = String(item.mensagem_recebida || "").toLowerCase();
    const resposta = String(item.resposta_enviada || "").toLowerCase();
    const statusMensagem = String(item.status || "").toLowerCase();

    const combinaBusca =
      telefone.includes(busca) ||
      mensagem.includes(busca) ||
      resposta.includes(busca);

    const combinaStatus =
      status === "todos" || statusMensagem === status;

    return combinaBusca && combinaStatus;
  });

  renderizarMensagens(mensagensFiltradas);
}

function limparFiltrosMensagens() {
  const filtroBuscaInput = document.getElementById("filtroBusca");
  const filtroStatusInput = document.getElementById("filtroStatus");

  if (filtroBuscaInput) {
    filtroBuscaInput.value = "";
  }

  if (filtroStatusInput) {
    filtroStatusInput.value = "todos";
  }

  renderizarMensagens(mensagensCache);
}

async function carregarResumoDashboard() {
  const listaMensagensResumo = document.getElementById("listaMensagensResumo");
  const totalMensagens = document.getElementById("totalMensagens");

  try {
    const resposta = await fetch(`${API_URL}/mensagens`, {
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    if (!resposta.ok) {
      throw new Error("Erro ao carregar resumo.");
    }

    const mensagens = await resposta.json();

    if (totalMensagens) {
      totalMensagens.innerText = mensagens.length;
    }

    if (!listaMensagensResumo) return;

    if (mensagens.length === 0) {
      listaMensagensResumo.innerHTML = `
        <tr>
          <td colspan="4" class="empty-text">Nenhuma mensagem cadastrada.</td>
        </tr>
      `;
      return;
    }

    const ultimas = mensagens.slice(0, 5);

    listaMensagensResumo.innerHTML = ultimas.map((item) => `
      <tr>
        <td>${item.id}</td>
        <td>${item.telefone}</td>
        <td>${item.mensagem_recebida}</td>
        <td>
          <span class="status-badge status-${item.status}">
            ${item.status}
          </span>
        </td>
      </tr>
    `).join("");
  } catch (erro) {
    if (listaMensagensResumo) {
      listaMensagensResumo.innerHTML = `
        <tr>
          <td colspan="4">Erro ao carregar mensagens.</td>
        </tr>
      `;
    }
  }
}

async function carregarFaqs() {
  const listaFaqs = document.getElementById("listaFaqs");
  const totalFaqs = document.getElementById("totalFaqs");

  try {
    const resposta = await fetch(`${API_URL}/faqs`, {
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    if (!resposta.ok) {
      throw new Error("Erro ao carregar FAQs.");
    }

    const faqs = await resposta.json();

    if (totalFaqs) {
      totalFaqs.innerText = faqs.length;
    }

    if (!listaFaqs) return;

    if (faqs.length === 0) {
      listaFaqs.innerHTML = "<p class='empty-text'>Nenhuma FAQ cadastrada.</p>";
      return;
    }

    listaFaqs.innerHTML = faqs.map((faq) => `
      <div class="faq-item">
        <span class="badge">${faq.palavra_chave}</span>
        <h4>${faq.pergunta}</h4>
        <p>${faq.resposta}</p>

        <button class="btn-danger btn-small admin-only" onclick="excluirFaq(${faq.id})">
          Excluir FAQ
        </button>
      </div>
    `).join("");

    aplicarPermissoesFrontEnd();
  } catch (erro) {
    if (listaFaqs) {
      listaFaqs.innerHTML = "<p>Erro ao carregar FAQs.</p>";
    }
  }
}

async function atualizarStatus(id, novoStatus) {
  try {
    const resposta = await fetch(`${API_URL}/mensagens/${id}/status`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        status: novoStatus
      })
    });

    if (verificarErroAuth(resposta)) return;

    if (!resposta.ok) {
      throw new Error("Erro ao atualizar status.");
    }

    await carregarMensagens();
    await carregarResumoDashboard();

    aplicarFiltrosMensagens();
  } catch (erro) {
    alert("Erro ao atualizar status. Verifique se a API está rodando.");
  }
}

async function excluirFaq(id) {
  const confirmar = confirm("Tem certeza que deseja excluir esta FAQ?");

  if (!confirmar) return;

  try {
    const resposta = await fetch(`${API_URL}/faqs/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alert(dados.detail || "Erro ao excluir FAQ.");
      return;
    }

    carregarFaqs();
    carregarResumoDashboard();
  } catch (erro) {
    alert("Erro ao excluir FAQ. Verifique se a API está rodando.");
  }
}

async function excluirMensagem(id) {
  const confirmar = confirm("Tem certeza que deseja excluir esta mensagem?");

  if (!confirmar) return;

  try {
    const resposta = await fetch(`${API_URL}/mensagens/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alert(dados.detail || "Erro ao excluir mensagem.");
      return;
    }

    await carregarMensagens();
    await carregarResumoDashboard();

    aplicarFiltrosMensagens();
  } catch (erro) {
    alert("Erro ao excluir mensagem. Verifique se a API está rodando.");
  }
}

async function limparHistorico() {
  const confirmar = confirm("Tem certeza que deseja apagar todo o histórico de mensagens?");

  if (!confirmar) return;

  try {
    const resposta = await fetch(`${API_URL}/mensagens`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alert(dados.detail || "Erro ao limpar histórico.");
      return;
    }

    await carregarMensagens();
    await carregarResumoDashboard();

    limparFiltrosMensagens();
  } catch (erro) {
    alert("Erro ao limpar histórico. Verifique se a API está rodando.");
  }
}

async function cadastrarUsuario() {
  const nomeInput = document.getElementById("nomeUsuario");
  const usernameInput = document.getElementById("usernameUsuario");
  const senhaInput = document.getElementById("senhaUsuario");
  const perfilInput = document.getElementById("perfilUsuario");
  const alertaUsuario = document.getElementById("alertaUsuario");

  if (!nomeInput || !usernameInput || !senhaInput || !perfilInput || !alertaUsuario) return;

  const nome = nomeInput.value.trim();
  const username = usernameInput.value.trim();
  const senha = senhaInput.value.trim();
  const perfil = perfilInput.value;

  if (!nome || !username || !senha || !perfil) {
    alertaUsuario.classList.remove("hidden");
    alertaUsuario.innerText = "Preencha todos os campos do usuário.";
    return;
  }

  if (senha.length < 6) {
    alertaUsuario.classList.remove("hidden");
    alertaUsuario.innerText = "A senha precisa ter pelo menos 6 caracteres.";
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/usuarios`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        nome: nome,
        username: username,
        senha: senha,
        perfil: perfil
      })
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alertaUsuario.classList.remove("hidden");
      alertaUsuario.innerText = dados.detail || "Erro ao cadastrar usuário.";
      return;
    }

    alertaUsuario.classList.remove("hidden");
    alertaUsuario.innerText = "Usuário cadastrado com sucesso!";

    nomeInput.value = "";
    usernameInput.value = "";
    senhaInput.value = "";
    perfilInput.value = "atendente";

    carregarUsuarios();
  } catch (erro) {
    alertaUsuario.classList.remove("hidden");
    alertaUsuario.innerText = "Erro ao cadastrar usuário. Verifique se a API está rodando.";
  }
}

async function carregarUsuarios() {
  const listaUsuarios = document.getElementById("listaUsuarios");

  if (!listaUsuarios) return;

  try {
    const resposta = await fetch(`${API_URL}/usuarios`, {
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    if (!resposta.ok) {
      throw new Error("Erro ao carregar usuários.");
    }

    const usuarios = await resposta.json();

    usuariosCache = usuarios;

    renderizarUsuarios(usuariosCache);
  } catch (erro) {
    listaUsuarios.innerHTML = `
      <tr>
        <td colspan="6">Erro ao carregar usuários.</td>
      </tr>
    `;
  }
}

function renderizarUsuarios(usuarios) {
  const listaUsuarios = document.getElementById("listaUsuarios");

  if (!listaUsuarios) return;

  if (usuarios.length === 0) {
    listaUsuarios.innerHTML = `
      <tr>
        <td colspan="6" class="empty-text">Nenhum usuário encontrado.</td>
      </tr>
    `;
    return;
  }

  listaUsuarios.innerHTML = usuarios.map((usuario) => `
    <tr>
      <td>${usuario.id}</td>
      <td>${usuario.nome}</td>
      <td>${usuario.username}</td>
      <td>
        <span class="user-role role-${usuario.perfil}">
          ${usuario.perfil}
        </span>
      </td>
      <td class="data-text">${formatarData(usuario.criado_em)}</td>
      <td>
        <button class="secondary btn-small admin-only" onclick="abrirEdicaoUsuario(${usuario.id}, '${usuario.nome}', '${usuario.username}', '${usuario.perfil}')">
          Editar
        </button>

        <button class="btn-danger btn-small admin-only" onclick="excluirUsuario(${usuario.id})">
          Excluir
        </button>

        <button class="secondary btn-small admin-only" onclick="alterarSenhaUsuario(${usuario.id})">
          Alterar senha
        </button>
      </td>
    </tr>
  `).join("");

  aplicarPermissoesFrontEnd();
}

async function excluirUsuario(id) {
  const confirmar = confirm("Tem certeza que deseja excluir este usuário?");

  if (!confirmar) return;

  try {
    const resposta = await fetch(`${API_URL}/usuarios/${id}`, {
      method: "DELETE",
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alert(dados.detail || "Erro ao excluir usuário.");
      return;
    }

    await carregarUsuarios();
    aplicarFiltrosUsuarios();
  } catch (erro) {
    alert("Erro ao excluir usuário. Verifique se a API está rodando.");
  }
}

async function alterarSenhaUsuario(id) {
  const novaSenha = prompt("Digite a nova senha para este usuário:");

  if (!novaSenha) return;

  if (novaSenha.length < 6) {
    alert("A senha precisa ter pelo menos 6 caracteres.");
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/usuarios/${id}/senha`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        nova_senha: novaSenha
      })
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alert(dados.detail || "Erro ao alterar senha.");
      return;
    }

    alert("Senha alterada com sucesso!");
  } catch (erro) {
    alert("Erro ao alterar senha. Verifique se a API está rodando.");
  }
}

async function carregarMeuPerfil() {
  const perfilNome = document.getElementById("perfilNome");
  const perfilUsername = document.getElementById("perfilUsername");
  const perfilTipo = document.getElementById("perfilTipo");
  const perfilId = document.getElementById("perfilId");
  const perfilCriadoEm = document.getElementById("perfilCriadoEm");
  const profileAvatar = document.getElementById("profileAvatar");

  if (!perfilNome) return;

  try {
    const resposta = await fetch(`${API_URL}/me`, {
      headers: authHeaders()
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      perfilNome.innerText = "Erro ao carregar perfil";
      return;
    }

    perfilNome.innerText = dados.nome;
    perfilUsername.innerText = `@${dados.username}`;
    perfilTipo.innerText = dados.perfil;
    perfilId.innerText = dados.id;
    perfilCriadoEm.innerText = formatarData(dados.criado_em);

    if (profileAvatar && dados.nome) {
      profileAvatar.innerText = dados.nome.charAt(0).toUpperCase();
    }
  } catch (erro) {
    perfilNome.innerText = "Erro ao conectar com a API";
  }
}


async function alterarMinhaSenha() {
  const senhaAtualInput = document.getElementById("senhaAtual");
  const novaSenhaInput = document.getElementById("novaSenhaPerfil");
  const alertaPerfil = document.getElementById("alertaPerfil");

  if (!senhaAtualInput || !novaSenhaInput || !alertaPerfil) return;

  const senhaAtual = senhaAtualInput.value.trim();
  const novaSenha = novaSenhaInput.value.trim();

  if (!senhaAtual || !novaSenha) {
    alertaPerfil.classList.remove("hidden");
    alertaPerfil.innerText = "Preencha a senha atual e a nova senha.";
    return;
  }

  if (novaSenha.length < 6) {
    alertaPerfil.classList.remove("hidden");
    alertaPerfil.innerText = "A nova senha precisa ter pelo menos 6 caracteres.";
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/me/senha`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        senha_atual: senhaAtual,
        nova_senha: novaSenha
      })
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alertaPerfil.classList.remove("hidden");
      alertaPerfil.innerText = dados.detail || "Erro ao alterar senha.";
      return;
    }

    alertaPerfil.classList.remove("hidden");
    alertaPerfil.innerText = "Senha alterada com sucesso!";

    senhaAtualInput.value = "";
    novaSenhaInput.value = "";
  } catch (erro) {
    alertaPerfil.classList.remove("hidden");
    alertaPerfil.innerText = "Erro ao alterar senha. Verifique se a API está rodando.";
  }
}

function abrirEdicaoUsuario(id, nome, username, perfil) {
  const cardEditarUsuario = document.getElementById("cardEditarUsuario");
  const editarUsuarioId = document.getElementById("editarUsuarioId");
  const editarNomeUsuario = document.getElementById("editarNomeUsuario");
  const editarUsernameUsuario = document.getElementById("editarUsernameUsuario");
  const editarPerfilUsuario = document.getElementById("editarPerfilUsuario");
  const alertaEditarUsuario = document.getElementById("alertaEditarUsuario");

  if (!cardEditarUsuario) return;

  cardEditarUsuario.classList.remove("hidden");

  editarUsuarioId.value = id;
  editarNomeUsuario.value = nome;
  editarUsernameUsuario.value = username;
  editarPerfilUsuario.value = perfil;

  if (alertaEditarUsuario) {
    alertaEditarUsuario.classList.add("hidden");
    alertaEditarUsuario.innerText = "";
  }

  cardEditarUsuario.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}


function cancelarEdicaoUsuario() {
  const cardEditarUsuario = document.getElementById("cardEditarUsuario");
  const alertaEditarUsuario = document.getElementById("alertaEditarUsuario");

  if (cardEditarUsuario) {
    cardEditarUsuario.classList.add("hidden");
  }

  if (alertaEditarUsuario) {
    alertaEditarUsuario.classList.add("hidden");
    alertaEditarUsuario.innerText = "";
  }
}


async function salvarEdicaoUsuario() {
  const editarUsuarioId = document.getElementById("editarUsuarioId");
  const editarNomeUsuario = document.getElementById("editarNomeUsuario");
  const editarUsernameUsuario = document.getElementById("editarUsernameUsuario");
  const editarPerfilUsuario = document.getElementById("editarPerfilUsuario");
  const alertaEditarUsuario = document.getElementById("alertaEditarUsuario");

  if (
    !editarUsuarioId ||
    !editarNomeUsuario ||
    !editarUsernameUsuario ||
    !editarPerfilUsuario ||
    !alertaEditarUsuario
  ) return;

  const id = editarUsuarioId.value;
  const nome = editarNomeUsuario.value.trim();
  const username = editarUsernameUsuario.value.trim();
  const perfil = editarPerfilUsuario.value;

  if (!nome || !username || !perfil) {
    alertaEditarUsuario.classList.remove("hidden");
    alertaEditarUsuario.innerText = "Preencha todos os campos para editar o usuário.";
    return;
  }

  try {
    const resposta = await fetch(`${API_URL}/usuarios/${id}`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({
        nome: nome,
        username: username,
        perfil: perfil
      })
    });

    if (verificarErroAuth(resposta)) return;

    const dados = await resposta.json();

    if (!resposta.ok) {
      alertaEditarUsuario.classList.remove("hidden");
      alertaEditarUsuario.innerText = dados.detail || "Erro ao editar usuário.";
      return;
    }

    alertaEditarUsuario.classList.remove("hidden");
    alertaEditarUsuario.innerText = "Usuário atualizado com sucesso!";

    await carregarUsuarios();
    aplicarFiltrosUsuarios();

    setTimeout(() => {
      cancelarEdicaoUsuario();
    }, 1000);
  } catch (erro) {
    alertaEditarUsuario.classList.remove("hidden");
    alertaEditarUsuario.innerText = "Erro ao editar usuário. Verifique se a API está rodando.";
  }
}

function aplicarFiltrosUsuarios() {
  const filtroBuscaInput = document.getElementById("filtroUsuarioBusca");
  const filtroPerfilInput = document.getElementById("filtroUsuarioPerfil");

  if (!filtroBuscaInput || !filtroPerfilInput) return;

  const busca = filtroBuscaInput.value.toLowerCase().trim();
  const perfil = filtroPerfilInput.value;

  const usuariosFiltrados = usuariosCache.filter((usuario) => {
    const nome = String(usuario.nome || "").toLowerCase();
    const username = String(usuario.username || "").toLowerCase();
    const perfilUsuario = String(usuario.perfil || "").toLowerCase();

    const combinaBusca =
      nome.includes(busca) ||
      username.includes(busca);

    const combinaPerfil =
      perfil === "todos" || perfilUsuario === perfil;

    return combinaBusca && combinaPerfil;
  });

  renderizarUsuarios(usuariosFiltrados);
}


function limparFiltrosUsuarios() {
  const filtroBuscaInput = document.getElementById("filtroUsuarioBusca");
  const filtroPerfilInput = document.getElementById("filtroUsuarioPerfil");

  if (filtroBuscaInput) {
    filtroBuscaInput.value = "";
  }

  if (filtroPerfilInput) {
    filtroPerfilInput.value = "todos";
  }

  renderizarUsuarios(usuariosCache);
}

function formatarData(dataTexto) {
  if (!dataTexto) return "Sem data";

  const data = new Date(dataTexto);

  if (isNaN(data.getTime())) {
    return dataTexto;
  }

  return data.toLocaleString("pt-BR");
}

document.addEventListener("DOMContentLoaded", () => {
  protegerPagina();

  const paginaAtual = window.location.pathname.split("/").pop();

  if (paginaAtual === "login.html") {
    return;
  }

  aplicarPermissoesFrontEnd();

  if (document.getElementById("listaMensagensResumo")) {
    carregarResumoDashboard();
  }

  if (document.getElementById("totalFaqs") || document.getElementById("listaFaqs")) {
    carregarFaqs();
  }

  if (document.getElementById("listaMensagens")) {
    carregarMensagens();
  }

  if (document.getElementById("listaUsuarios")) {
    carregarUsuarios();
  }

  if (document.getElementById("perfilNome")) {
    carregarMeuPerfil();
  }
});
