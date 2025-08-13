st.info("""
        👆 **Como usar:**
        1. **Faça upload** das suas imagens (PNG, JPEG, GIF)
        2. **Ajuste as configurações** na barra lateral se necessário
        3. **Clique em "Processar"** e aguarde
        4. **Faça download** dos arquivos otimizados
        
        💡    # Informação sobre processamento
    with st.sidebar.expander("🔄 Como Funciona"):
        st.write("""
        **Processamento por Tipo:**
        
         **PNG/JPEG**:
        - ✅ **Converte para WEBP**
        - ✅ Até 35% menor (PNG)
        - ✅ Até 25% menor (JPEG)
        - ✅ Transparência preservada (PNG)
        
        🎬 **GIF**:
        - ✅ **Mantém formato GIF**
        - ✅ **Apenas compressão/otimização**
        - ✅ Animações preservadas
        - ✅ Transparência mantida
        - ✅ Compatibilidade total
        """)
    
    # Informações sobre o formato WEBP
    with st.sidebar.expander("ℹ️ Vantagens do WEBP"):
        st.write("""
        **Por que WEBP para PNG/JPEG:**
        - 📉 Arquivos muito menores
        - ✨ Suporte a transparência
        - #!/usr/bin/env python3
"""
Conversor Universal → WEBP
Aplicação Streamlit para converter PNG, JPEG e GIF para WEBP
"""

import streamlit as st
import io
import zipfile
from PIL import Image, ImageSequence
import base64
from typing import List, Tuple

# Configuração da página
st.set_page_config(
    page_title="Conversor Universal → WEBP",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .stats-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def convert_image_to_webp(image_data: bytes, filename: str, quality: int, lossless: bool) -> Tuple[bytes, dict]:
    """
    Converte PNG/JPEG para WEBP, ou comprime GIF mantendo formato original
    
    Args:
        image_data: Dados da imagem em bytes
        filename: Nome do arquivo original
        quality: Qualidade da compressão (0-100)
        lossless: Se usar compressão sem perdas
    
    Returns:
        Tuple com os dados da imagem convertida/comprimida e estatísticas
    """
    try:
        # Detectar tipo de arquivo
        file_ext = filename.lower().split('.')[-1]
        
        # Tratar GIF (apenas compressão, mantém formato GIF)
        if file_ext == 'gif':
            return compress_gif(image_data, filename, quality, lossless)
        
        # Abrir imagem
        image = Image.open(io.BytesIO(image_data))
        
        # Converter para modo RGB se necessário
        if image.mode == 'RGBA':
            # Preservar transparência para PNG
            if file_ext == 'png':
                # Manter RGBA para preservar transparência
                pass
            else:
                # Para JPEG, criar fundo branco
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
        elif image.mode == 'P':
            # Converter paleta para RGBA se tiver transparência
            if 'transparency' in image.info:
                image = image.convert('RGBA')
            else:
                image = image.convert('RGB')
        elif image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        
        # Converter para WEBP
        output_buffer = io.BytesIO()
        
        if lossless:
            image.save(output_buffer, 'WEBP', lossless=True)
            compression_type = "Sem perdas"
        else:
            if image.mode == 'RGBA':
                # Para imagens com transparência, usar qualidade ligeiramente mais alta
                image.save(output_buffer, 'WEBP', quality=min(quality + 5, 100), optimize=True)
            else:
                image.save(output_buffer, 'WEBP', quality=quality, optimize=True)
            compression_type = f"Qualidade {quality}"
        
        webp_data = output_buffer.getvalue()
        
        # Calcular estatísticas
        original_size = len(image_data)
        new_size = len(webp_data)
        reduction = (1 - new_size / original_size) * 100
        
        stats = {
            'filename': filename,
            'original_format': file_ext.upper(),
            'original_size': original_size,
            'new_size': new_size,
            'reduction': reduction,
            'compression_type': compression_type,
            'dimensions': f"{image.size[0]}x{image.size[1]}",
            'has_transparency': image.mode == 'RGBA'
        }
        
        return webp_data, stats
        
    except Exception as e:
        st.error(f"Erro ao converter {filename}: {str(e)}")
        return None, None

def compress_gif(image_data: bytes, filename: str, quality: int, lossless: bool) -> Tuple[bytes, dict]:
    """
    Comprime GIF mantendo o formato original (não converte para WEBP)
    """
    try:
        gif_image = Image.open(io.BytesIO(image_data))
        
        # Verificar se é animado
        is_animated = getattr(gif_image, 'is_animated', False)
        n_frames = getattr(gif_image, 'n_frames', 1)
        
        output_buffer = io.BytesIO()
        
        if is_animated and n_frames > 1:
            # GIF animado - comprimir mantendo animação
            frames = []
            durations = []
            
            for frame_index in range(gif_image.n_frames):
                gif_image.seek(frame_index)
                frame = gif_image.copy()
                
                # Otimizar paleta se necessário
                if frame.mode == 'RGBA':
                    # Manter RGBA para transparência
                    pass
                elif frame.mode == 'P':
                    # Otimizar paleta
                    pass
                
                frames.append(frame)
                duration = frame.info.get('duration', 100)
                durations.append(duration)
            
            # Salvar GIF comprimido
            frames[0].save(
                output_buffer,
                'GIF',
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                optimize=True
            )
            compression_type = "GIF Animado Comprimido"
            output_format = "GIF"
            
        else:
            # GIF estático - comprimir como GIF simples
            if gif_image.mode == 'P':
                # Manter modo paleta para GIF
                pass
            elif gif_image.mode == 'RGBA':
                # Converter para paleta com transparência
                gif_image = gif_image.quantize(method=Image.Quantize.MEDIANCUT)
            
            gif_image.save(output_buffer, 'GIF', optimize=True)
            compression_type = "GIF Estático Comprimido"
            output_format = "GIF"
        
        gif_data = output_buffer.getvalue()
        
        # Calcular estatísticas
        original_size = len(image_data)
        new_size = len(gif_data)
        reduction = (1 - new_size / original_size) * 100
        
        stats = {
            'filename': filename,
            'original_format': 'GIF',
            'original_size': original_size,
            'new_size': new_size,
            'reduction': reduction,
            'compression_type': compression_type,
            'dimensions': f"{gif_image.size[0]}x{gif_image.size[1]}",
            'has_transparency': gif_image.mode in ['RGBA', 'P'],
            'frames': n_frames,
            'animated': is_animated and n_frames > 1,
            'output_type': output_format,
            'output_format': 'GIF'
        }
        
        return gif_data, stats
        
    except Exception as e:
        st.error(f"Erro ao comprimir GIF {filename}: {str(e)}")
        return None, None

def create_download_link(data: bytes, filename: str, text: str) -> str:
    """Cria um link de download para os dados"""
    b64_data = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64_data}" download="{filename}">{text}</a>'
    return href

def format_bytes(bytes_value: int) -> str:
    """Formata bytes em unidades legíveis"""
    for unit in ['B', 'KB', 'MB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} GB"

def main():
    # Título principal
    st.markdown('<h1 class="main-header">🖼️ Conversor PNG/JPEG → WEBP + Compressor GIF</h1>', unsafe_allow_html=True)
    
    # Sidebar com configurações
    st.sidebar.header("⚙️ Configurações")
    
    # Opções de compressão
    compression_mode = st.sidebar.radio(
        "Modo de compressão:",
        ["Com perdas (menor tamanho)", "Sem perdas (melhor qualidade)"]
    )
    
    lossless = compression_mode == "Sem perdas (melhor qualidade)"
    
    if not lossless:
        quality = st.sidebar.slider("Qualidade da compressão:", 10, 100, 85, 5)
    else:
        quality = 100
    
    # Informações sobre formatos suportados
    with st.sidebar.expander("📁 Formatos Suportados"):
        st.write("""
        **Entrada:** 
        - 🖼️ **PNG** - Converte para WEBP
        - 📷 **JPEG/JPG** - Converte para WEBP
        - 🎬 **GIF** - Comprime mantendo formato GIF
        
        **Saída:**
        - 🚀 **WEBP** - Para PNG/JPEG
        - 🎬 **GIF Comprimido** - Para arquivos GIF
        """)
    
    # Informações sobre o formato WEBP
    with st.sidebar.expander("ℹ️ Vantagens do WEBP"):
        st.write("""
        **Por que converter para WEBP:**
        - 📉 Até 35% menor que PNG
        - 📉 Até 25% menor que JPEG
        - 📉 Até 50% menor que GIF
        - ✨ Suporte a transparência
        - 🎬 Suporte a animações (melhor que GIF)
        - 🌐 Suportado por navegadores modernos
        - ⚡ Carregamento mais rápido
        
        **Por que GIF mantém formato:**
        - 🎬 **Animações sempre funcionam**
        - 🔄 **100% compatibilidade**
        - 📱 **Funciona em qualquer lugar**
        - 🗜️ **Ainda consegue comprimir**
        
        **Qualidade recomendada:**
        - 📷 **Fotos**: 80-85
        - 🎨 **Gráficos**: 90-95  
        - 💾 **Economia**: 70-80
        """)
    
    # Informação sobre GIFs removida (já que agora só comprime)
    
    # Upload de arquivos
    st.header("📁 Enviar Imagens")
    uploaded_files = st.file_uploader(
        "Escolha as imagens para processar:",
        type=['png', 'jpg', 'jpeg', 'gif'],
        accept_multiple_files=True,
        help="PNG/JPEG → WEBP | GIF → GIF Comprimido"
    )
    
    if uploaded_files:
        # Mostrar tipos de arquivo detectados
        file_types = {}
        for file in uploaded_files:
            ext = file.name.lower().split('.')[-1]
            if ext == 'jpg':
                ext = 'jpeg'
            file_types[ext.upper()] = file_types.get(ext.upper(), 0) + 1
        
        types_text = ", ".join([f"{count} {ftype}" for ftype, count in file_types.items()])
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s): {types_text}")
        
        # Mostrar preview dos arquivos
        with st.expander("🔍 Visualizar arquivos carregados"):
            cols = st.columns(min(4, len(uploaded_files)))
            for i, file in enumerate(uploaded_files):
                with cols[i % 4]:
                    try:
                        if file.type.startswith('image'):
                            st.image(file, caption=file.name, width=150)
                        else:
                            st.write(f"📁 {file.name}")
                    except:
                        st.write(f"📁 {file.name}")
        
        # Botão de conversão
        if st.button("🚀 Processar Imagens", type="primary"):
            
            # Barra de progresso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            converted_files = []
            all_stats = []
            total_original_size = 0
            total_new_size = 0
            
            # Processar cada arquivo
            for i, uploaded_file in enumerate(uploaded_files):
                file_ext = uploaded_file.name.lower().split('.')[-1]
                if file_ext == 'gif':
                    action = "Comprimindo"
                else:
                    action = "Convertendo"
                status_text.text(f"{action} {file_ext.upper()}: {uploaded_file.name}")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Ler dados do arquivo
                file_data = uploaded_file.read()
                
                # Processar
                webp_data, stats = convert_image_to_webp(
                    file_data, 
                    uploaded_file.name, 
                    quality, 
                    lossless
                )
                
                if webp_data and stats:
                    # Nome do arquivo convertido
                    if stats.get('output_format') == 'GIF':
                        # Manter extensão .gif para GIFs comprimidos
                        output_filename = uploaded_file.name
                    else:
                        # Converter para .webp para PNG/JPEG
                        output_filename = uploaded_file.name.rsplit('.', 1)[0] + '.webp'
                    
                    converted_files.append((webp_data, output_filename))
                    all_stats.append(stats)
                    total_original_size += stats['original_size']
                    total_new_size += stats['new_size']
            
            # Limpar barra de progresso
            progress_bar.empty()
            status_text.empty()
            
            if converted_files:
                st.success("🎉 Processamento concluído com sucesso!")
                
                # Estatísticas gerais
                total_reduction = (1 - total_new_size / total_original_size) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Arquivos processados", len(converted_files))
                with col2:
                    st.metric("Tamanho original", format_bytes(total_original_size))
                with col3:
                    st.metric("Tamanho final", format_bytes(total_new_size))
                with col4:
                    st.metric("Redução total", f"{total_reduction:.1f}%")
                
                # Tabela com detalhes de cada arquivo
                st.header("📊 Detalhes do Processamento")
                
                stats_data = []
                for stats in all_stats:
                    row = {
                        "Arquivo": stats['filename'],
                        "Formato": stats['original_format'],
                        "Dimensões": stats['dimensions'],
                        "Tamanho Original": format_bytes(stats['original_size']),
                        "Tamanho Final": format_bytes(stats['new_size']),
                        "Redução": f"{stats['reduction']:.1f}%",
                        "Processamento": stats['compression_type']
                    }
                    
                    # Adicionar informações específicas para GIFs
                    if 'frames' in stats:
                        row["Frames"] = stats['frames']
                        row["Animado"] = "Sim" if stats.get('animated', False) else "Não"
                        if 'output_type' in stats:
                            row["Tipo Saída"] = stats['output_type']
                    
                    # Adicionar informação sobre transparência
                    if stats.get('has_transparency'):
                        row["Transparência"] = "Sim"
                    
                    stats_data.append(row)
                
                st.dataframe(stats_data, use_container_width=True)
                
                # Downloads
                st.header("💾 Fazer Download")
                
                if len(converted_files) == 1:
                    # Download individual
                    file_data, output_filename = converted_files[0]
                    # Definir MIME type baseado na extensão
                    if output_filename.lower().endswith('.gif'):
                        mime_type = "image/gif"
                    else:
                        mime_type = "image/webp"
                    
                    st.download_button(
                        label=f"📥 Baixar {output_filename}",
                        data=file_data,
                        file_name=output_filename,
                        mime=mime_type
                    )
                else:
                    # Download em ZIP
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for file_data, output_filename in converted_files:
                            zip_file.writestr(output_filename, file_data)
                    
                    st.download_button(
                        label=f"📦 Baixar todos os arquivos ({len(converted_files)} arquivos em ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="imagens_processadas.zip",
                        mime="application/zip"
                    )
                
                # Preview das imagens processadas
                with st.expander("🔍 Visualizar Imagens Processadas"):
                    cols = st.columns(min(3, len(converted_files)))
                    for i, (file_data, output_filename) in enumerate(converted_files):
                        with cols[i % 3]:
                            st.image(file_data, caption=output_filename, width=200)
    
    else:
        # Instruções quando não há arquivos
        st.info("""
        👆 **Como usar:**
        1. **Faça upload** das suas imagens (PNG, JPEG, GIF)
        2. **Ajuste as configurações** na barra lateral se necessário
        3. **Clique em "Processar"** e aguarde
        4. **Faça download** dos arquivos otimizados
        
        💡 **Processamento por tipo:**
        - 🖼️ **PNG/JPEG** → **WEBP** (menor e mais rápido)
        - 🎬 **GIF** → **GIF Comprimido** (mantém animações)
        
        ⚡ **Benefícios:**
        - **PNG/JPEG**: Até **35% menores** como WEBP
        - **GIF**: **Compressão otimizada** mantendo compatibilidade
        - **Transparência preservada** em todos os formatos
        - **Animações mantidas** nos GIFs
        """)
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        "🚀 **Conversor Inteligente** | "
        "PNG/JPEG → WEBP • GIF → GIF Comprimido | "
        "🎬 **Animações sempre preservadas!**"
    )

if __name__ == "__main__":
    main()
