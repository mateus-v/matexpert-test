# 🎨 Compressor de Imagens - Streamlit App

Uma aplicação web moderna e intuitiva para compressão de imagens, construída com Streamlit e PIL (Pillow). Oferece compressão especializada para GIFs animados e conversão otimizada para WebP.

## ✨ Características Principais

- 🎯 **Compressão Inteligente**: GIFs mantêm formato original, outras imagens convertidas para WebP
- 🎬 **Suporte a GIF Animado**: Preserva animações com otimização avançada
- 📊 **Estatísticas Detalhadas**: Métricas completas de compressão
- 📦 **Download em Lote**: ZIP com todas as imagens processadas
- 🎨 **Interface Moderna**: Design responsivo com gradientes e efeitos visuais
- ⚙️ **Configurações Flexíveis**: Controle de qualidade e compressão sem perdas

## 🚀 Instalação Rápida

### Pré-requisitos

```bash
Python 3.7+
```

### Instalar Dependências

```bash
pip install streamlit pillow
```

### Executar Aplicação

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

## 📋 Dependências

```txt
streamlit>=1.28.0
Pillow>=10.0.0
```

## 🎯 Formatos Suportados

### Entrada
- **PNG** - Portable Network Graphics
- **JPG/JPEG** - Joint Photographic Experts Group
- **GIF** - Graphics Interchange Format (incluindo animados)
- **WebP** - Formato moderno do Google
- **BMP** - Bitmap

### Saída
- **GIF** - Para arquivos GIF (comprimidos mas mantendo formato)
- **WebP** - Para todos os outros formatos

## 🛠️ Como Usar

### 1. Upload de Arquivos
- Arraste e solte arquivos na área designada
- Ou clique para selecionar múltiplos arquivos
- Suporte a seleção múltipla

### 2. Configurações (Sidebar)
- **Qualidade**: Slider de 1-100% (para conversão WebP)
- **Sem Perdas**: Checkbox para compressão lossless WebP
- **Informações**: Guia sobre tipos de processamento

### 3. Processamento
- Clique em "🚀 Comprimir Imagens"
- Acompanhe o progresso em tempo real
- Visualize estatísticas detalhadas

### 4. Download
- **Individual**: Botão de download para cada arquivo
- **Em Lote**: ZIP com todas as imagens comprimidas

## 📊 Métricas Exibidas

### Por Arquivo
- 📁 **Formato Original**: Tipo do arquivo de entrada
- 📏 **Tamanho Original**: Tamanho antes da compressão
- 📦 **Novo Tamanho**: Tamanho após compressão
- 📉 **Redução**: Percentual de redução/aumento
- 📐 **Dimensões**: Largura x Altura em pixels
- 🔧 **Tipo de Compressão**: Método utilizado

### Para GIFs Adicionalmente
- 🎬 **Frames**: Número de quadros
- 🎭 **Animado**: Se é animado ou estático
- 👻 **Transparência**: Se possui transparência

### Totais
- 📁 **Arquivos Processados**: Quantidade total
- 📏 **Tamanho Total Original**: Soma de todos os arquivos
- 📦 **Tamanho Total Comprimido**: Soma após compressão
- 📉 **Redução Total**: Economia total obtida

## 🎨 Características Técnicas

### Compressão de GIF
- Preserva animações e timing original
- Otimização de paleta de cores (modo P)
- Configuração anti-artefatos (disposal=2)
- Manutenção de transparência

### Conversão WebP
- Controle de qualidade ajustável
- Suporte a compressão sem perdas
- Preservação de canal alfa (transparência)
- Otimização automática

### Interface
- Design responsivo e moderno
- Gradientes e efeitos glassmorphism
- Feedback visual em tempo real
- CSS customizado para melhor UX

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Porta personalizada
STREAMLIT_SERVER_PORT=8501

# Tema escuro
STREAMLIT_THEME_BASE=dark
```

### Configuração via arquivo

Crie `.streamlit/config.toml`:

```toml
[server]
port = 8501
headless = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#f0f2f6"
```

## 📱 Deploy

### Streamlit Cloud
1. Fork este repositório
2. Conecte com Streamlit Cloud
3. Deploy automático

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Heroku
```bash
echo "streamlit>=1.28.0" > requirements.txt
echo "Pillow>=10.0.0" >> requirements.txt
echo "web: streamlit run app.py --server.port=$PORT" > Procfile
```

## 🐛 Solução de Problemas

### Erro de Memória
Para arquivos muito grandes, ajuste as configurações do Streamlit:

```toml
[server]
maxUploadSize = 200
maxMessageSize = 200
```

### PIL/Pillow Issues
```bash
pip uninstall PIL Pillow
pip install Pillow
```

### Streamlit não abre no navegador
```bash
streamlit run app.py --server.headless false
```

## 📈 Performance

### Otimizações Implementadas
- Processamento em lote eficiente
- Buffers de memória otimizados
- Compressão adaptativa baseada no tipo
- Cache de resultados quando possível

### Benchmarks Típicos
- **GIF Estático**: 20-60% de redução
- **GIF Animado**: 10-40% de redução
- **PNG → WebP**: 30-80% de redução
- **JPG → WebP**: 10-50% de redução

## 🤝 Contribuindo

### Estrutura do Projeto
```
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── README.md             # Este arquivo
└── .streamlit/
    └── config.toml       # Configurações
```

### Como Contribuir
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

### Problemas Conhecidos
- Arquivos muito grandes (>200MB) podem causar timeout
- GIFs com muitos frames podem demorar para processar
- Alguns formatos exóticos podem não ser suportados

### Contato
- 🐛 **Issues**: Use o GitHub Issues
- 📧 **Email**: Adicione seu email aqui
- 💬 **Discussões**: Use GitHub Discussions

## 🎉 Agradecimentos

- **Streamlit** - Framework web incrível
- **Pillow** - Biblioteca de processamento de imagens
- **PIL** - Python Imaging Library
- Comunidade Python e desenvolvedores que contribuíram

---

<div align="center">
  <strong>Feito com ❤️ e Python</strong><br>
  <em>Comprimindo o mundo, uma imagem por vez</em>
</div>