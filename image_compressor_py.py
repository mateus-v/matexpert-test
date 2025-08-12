import streamlit as st
import io
from PIL import Image
from typing import Tuple
import zipfile
import base64

# Configuração da página
st.set_page_config(
    page_title="🎨 Compressor de Imagens",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    .upload-section {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background: rgba(102, 126, 234, 0.05);
    }
    
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid #eee;
        margin: 1rem 0;
    }
    
    .metric-container {
        background: rgba(102, 126, 234, 0.05);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .gif-badge {
        background: #ff6b6b;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    
    .animated-badge {
        background: #4ecdc4 !important;
    }
    
    .success-metric {
        color: #28a745;
        font-weight: bold;
    }
    
    .error-metric {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def compress_gif(image_data: bytes, filename: str) -> Tuple[bytes, dict]:
    """
    Comprime um GIF (estático ou animado) mantendo o formato GIF.
    """
    try:
        gif_image = Image.open(io.BytesIO(image_data))
        is_animated = getattr(gif_image, "is_animated", False)
        n_frames = getattr(gif_image, "n_frames", 1)

        output_buffer = io.BytesIO()

        if is_animated and n_frames > 1:
            # Para GIF animado, salvar com otimização
            frames = []
            durations = []
            for frame_index in range(n_frames):
                gif_image.seek(frame_index)
                frame = gif_image.copy()

                # converter para P para melhor compressão, se possível
                if frame.mode != 'P':
                    frame = frame.convert('P', palette=Image.ADAPTIVE)

                frames.append(frame)
                durations.append(frame.info.get('duration', 100))

            frames[0].save(
                output_buffer,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                loop=0,
                duration=durations,
                optimize=True,
                disposal=2  # evita artefatos
            )
        else:
            # GIF estático
            # converter para P para reduzir tamanho
            if gif_image.mode != 'P':
                gif_image = gif_image.convert('P', palette=Image.ADAPTIVE)
            gif_image.save(output_buffer, format='GIF', optimize=True)

        compressed_data = output_buffer.getvalue()

        original_size = len(image_data)
        new_size = len(compressed_data)
        reduction = (1 - new_size / original_size) * 100

        stats = {
            'filename': filename,
            'original_format': 'GIF',
            'original_size': original_size,
            'new_size': new_size,
            'reduction': reduction,
            'compression_type': 'GIF Comprimido',
            'dimensions': f"{gif_image.size[0]}x{gif_image.size[1]}",
            'has_transparency': gif_image.info.get("transparency") is not None,
            'frames': n_frames,
            'animated': is_animated,
            'output_type': 'GIF Comprimido'
        }

        return compressed_data, stats

    except Exception as e:
        st.error(f"Erro ao comprimir GIF {filename}: {str(e)}")
        return None, None


def convert_image_to_webp(image_data: bytes, filename: str, quality: int, lossless: bool) -> Tuple[bytes, dict]:
    """
    Modificado para GIF: comprimir GIF em vez de converter para WEBP
    """
    try:
        file_ext = filename.lower().split('.')[-1]

        if file_ext == 'gif':
            # Ao invés de converter para webp, comprimir gif
            return compress_gif(image_data, filename)

        # resto do código para png, jpg, etc continua igual
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode == 'RGBA':
            if file_ext == 'png':
                pass
            else:
                background = Image.new('RGB', image.size, (255,255,255))
                background.paste(image, mask=image.split()[-1])
                image = background
        elif image.mode == 'P':
            if 'transparency' in image.info:
                image = image.convert('RGBA')
            else:
                image = image.convert('RGB')
        elif image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')

        output_buffer = io.BytesIO()
        if lossless:
            image.save(output_buffer, 'WEBP', lossless=True)
            compression_type = "Sem perdas"
        else:
            if image.mode == 'RGBA':
                image.save(output_buffer, 'WEBP', quality=min(quality + 5, 100), optimize=True)
            else:
                image.save(output_buffer, 'WEBP', quality=quality, optimize=True)
            compression_type = f"Qualidade {quality}"

        webp_data = output_buffer.getvalue()

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
            'has_transparency': image.mode == 'RGBA',
            'output_type': 'WEBP'
        }

        return webp_data, stats

    except Exception as e:
        st.error(f"Erro ao converter {filename}: {str(e)}")
        return None, None


def format_file_size(bytes_size):
    """Formata tamanho do arquivo em formato legível"""
    if bytes_size == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def create_download_link(data, filename, text):
    """Cria link de download para arquivo"""
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="text-decoration: none; background: #28a745; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">📥 {text}</a>'
    return href


def create_zip_download(results, original_files):
    """Cria arquivo ZIP com todas as imagens comprimidas"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i, (compressed_data, stats) in enumerate(results):
            if compressed_data and stats:
                # Determinar extensão baseada no tipo
                if stats.get('output_type') == 'GIF Comprimido':
                    extension = '.gif'
                else:
                    extension = '.webp'
                
                # Nome do arquivo comprimido
                base_name = stats['filename'].rsplit('.', 1)[0]
                compressed_filename = f"{base_name}_compressed{extension}"
                
                zip_file.writestr(compressed_filename, compressed_data)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def main():
    # Título principal
    st.markdown("<h1 style='text-align: center; color: #333; margin-bottom: 2rem; font-size: 3rem;'>🎨 Compressor de Imagens</h1>", unsafe_allow_html=True)
    
    # Sidebar com configurações
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        
        # Configurações de qualidade
        quality = st.slider(
            "Qualidade (para não-GIF)", 
            min_value=1, 
            max_value=100, 
            value=80,
            help="Qualidade da compressão para imagens convertidas para WebP"
        )
        
        lossless = st.checkbox(
            "Compressão sem perdas (WebP)", 
            value=False,
            help="Ativa compressão sem perdas para imagens WebP"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Informações")
        st.info("🎯 **GIFs** mantêm formato original\n\n📸 **Outras imagens** são convertidas para WebP")
    
    # Área de upload
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📁 Selecione suas imagens")
    uploaded_files = st.file_uploader(
        "Arraste e solte ou clique para selecionar",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'],
        accept_multiple_files=True,
        help="Suporta PNG, JPG, JPEG, GIF (incluindo animados), WebP e BMP"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.markdown(f"### 📊 Arquivos selecionados: {len(uploaded_files)}")
        
        # Botão de processar
        if st.button("🚀 Comprimir Imagens", type="primary", use_container_width=True):
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            # Processar cada arquivo
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processando {uploaded_file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Ler dados do arquivo
                file_data = uploaded_file.read()
                
                # Processar imagem
                compressed_data, stats = convert_image_to_webp(
                    file_data, 
                    uploaded_file.name, 
                    quality, 
                    lossless
                )
                
                results.append((compressed_data, stats))
            
            # Limpar progress bar
            progress_bar.empty()
            status_text.empty()
            
            # Exibir resultados
            st.markdown("## 📈 Resultados da Compressão")
            
            # Estatísticas gerais
            total_original = sum(stats['original_size'] for _, stats in results if stats)
            total_compressed = sum(stats['new_size'] for _, stats in results if stats)
            total_reduction = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📁 Arquivos processados", len([r for r in results if r[1]]))
            with col2:
                st.metric("📏 Tamanho original", format_file_size(total_original))
            with col3:
                st.metric("📦 Tamanho comprimido", format_file_size(total_compressed))
            with col4:
                reduction_color = "success-metric" if total_reduction > 0 else "error-metric"
                st.metric(
                    "📉 Redução total", 
                    f"{total_reduction:.1f}%",
                    delta=f"{format_file_size(total_original - total_compressed)} economizados" if total_reduction > 0 else None
                )
            
            # Download em lote
            if any(r[0] for r in results):
                zip_data = create_zip_download(results, uploaded_files)
                st.markdown("### 📦 Download em Lote")
                st.markdown(
                    create_download_link(zip_data, "imagens_comprimidas.zip", "Baixar todas as imagens (ZIP)"),
                    unsafe_allow_html=True
                )
            
            st.markdown("---")
            
            # Resultados individuais
            for i, (compressed_data, stats) in enumerate(results):
                if not stats:
                    continue
                    
                st.markdown('<div class="stats-card">', unsafe_allow_html=True)
                
                # Header do arquivo
                col1, col2 = st.columns([3, 1])
                with col1:
                    badge_class = "animated-badge" if stats.get('animated') else ""
                    gif_indicator = f'<span class="gif-badge {badge_class}">{"GIF Animado" if stats.get("animated") else "GIF"}</span>' if stats['original_format'] == 'GIF' else ""
                    st.markdown(f"#### 📄 {stats['filename']} {gif_indicator}", unsafe_allow_html=True)
                
                with col2:
                    if compressed_data:
                        # Determinar extensão do arquivo de saída
                        output_ext = '.gif' if stats.get('output_type') == 'GIF Comprimido' else '.webp'
                        base_name = stats['filename'].rsplit('.', 1)[0]
                        download_filename = f"{base_name}_compressed{output_ext}"
                        
                        st.markdown(
                            create_download_link(compressed_data, download_filename, "Download"),
                            unsafe_allow_html=True
                        )
                
                # Métricas em colunas
                metric_cols = st.columns(6)
                
                with metric_cols[0]:
                    st.markdown(f'<div class="metric-container"><strong>{stats["original_format"]}</strong><br><small>Formato Original</small></div>', unsafe_allow_html=True)
                
                with metric_cols[1]:
                    st.markdown(f'<div class="metric-container"><strong>{format_file_size(stats["original_size"])}</strong><br><small>Tamanho Original</small></div>', unsafe_allow_html=True)
                
                with metric_cols[2]:
                    st.markdown(f'<div class="metric-container"><strong>{format_file_size(stats["new_size"])}</strong><br><small>Novo Tamanho</small></div>', unsafe_allow_html=True)
                
                with metric_cols[3]:
                    reduction_class = "success-metric" if stats['reduction'] > 0 else "error-metric"
                    reduction_icon = "↓" if stats['reduction'] > 0 else "↑"
                    st.markdown(f'<div class="metric-container"><strong class="{reduction_class}">{reduction_icon} {abs(stats["reduction"]):.1f}%</strong><br><small>{"Redução" if stats["reduction"] > 0 else "Aumento"}</small></div>', unsafe_allow_html=True)
                
                with metric_cols[4]:
                    st.markdown(f'<div class="metric-container"><strong>{stats["dimensions"]}</strong><br><small>Dimensões</small></div>', unsafe_allow_html=True)
                
                with metric_cols[5]:
                    st.markdown(f'<div class="metric-container"><strong>{stats["compression_type"]}</strong><br><small>Tipo de Compressão</small></div>', unsafe_allow_html=True)
                
                # Informações adicionais para GIFs
                if stats['original_format'] == 'GIF':
                    st.markdown("---")
                    info_cols = st.columns(3)
                    with info_cols[0]:
                        st.markdown(f"🎬 **Frames:** {stats.get('frames', 'N/A')}")
                    with info_cols[1]:
                        st.markdown(f"🎭 **Animado:** {'Sim' if stats.get('animated') else 'Não'}")
                    with info_cols[2]:
                        st.markdown(f"👻 **Transparência:** {'Sim' if stats.get('has_transparency') else 'Não'}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
    
    else:
        # Instruções quando não há arquivos
        st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #666;'>
            <h3>🎯 Como usar:</h3>
            <p><strong>1.</strong> Selecione suas imagens usando o botão acima</p>
            <p><strong>2.</strong> Configure a qualidade e opções na barra lateral</p>
            <p><strong>3.</strong> Clique em "Comprimir Imagens"</p>
            <p><strong>4.</strong> Baixe os arquivos individualmente ou em lote</p>
            
            <br>
            
            <h4>📝 Formatos suportados:</h4>
            <p>PNG • JPG • JPEG • GIF (incluindo animados) • WebP • BMP</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
