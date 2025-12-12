🔥 Como configurar o Banco de Dados Grátis (Firebase)

Para que seus dados (agendamentos, produtos, financeiro) não sumam quando você fechar o app, siga estes passos:

1. Criar Projeto no Google Firebase

Acesse console.firebase.google.com.

Clique em "Adicionar projeto" e dê um nome (ex: BarberManager).

Desative o Google Analytics (não precisa agora) e clique em Criar.

2. Criar o Banco de Dados

No menu lateral esquerdo, clique em Criação > Firestore Database.

Clique em Criar banco de dados.

Escolha o local (pode ser nam5 (us-central) ou sao-paulo se disponível).

IMPORTANTE: Nas regras de segurança, selecione "Iniciar no modo de teste" (depois podemos mudar, mas para começar é mais fácil).

3. Gerar a Chave de Acesso (JSON)

Clique na engrenagem ⚙️ (Configurações do projeto) no menu lateral esquerdo (topo).

Vá na aba Contas de serviço.

Em "SDK Admin do Firebase", clique em Gerar nova chave privada.

Um arquivo .json será baixado no seu computador.

Renomeie esse arquivo para firestore_key.json.

Coloque esse arquivo na pasta principal do seu projeto (junto com o app.py).

4. Pronto!

Agora, no seu código, basta importar as funções do arquivo database.py que criei.

Exemplo de como usar no pages/4_cadastros.py:
Em vez de st.session_state.catalogo_extras.append(...), você usará:
database.salvar_produto({...})