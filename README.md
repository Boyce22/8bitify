# 8-Bitify

<p align="center">
  <strong>Conversor de imagens para pixel art desenvolvido com PyQt6</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PyQt6-6.0+-41CD52?logo=qt&logoColor=white" alt="PyQt6" />
  <img src="https://img.shields.io/badge/Pillow-10.0+-FF6B6B" alt="Pillow" />
  <img src="https://img.shields.io/badge/Licença-Educacional-blue" alt="License" />
</p>

---

## Descrição

8-Bitify é uma aplicação desktop para conversão de imagens em pixel art, com suporte a múltiplos presets de consoles clássicos, parâmetros personalizáveis e processamento em segundo plano para manter a interface sempre responsiva.

---

## Funcionalidades

- Carregamento de imagens por arrastar e soltar
- Múltiplos presets pré-configurados (Game Boy, NES, VGA Retrô, etc.)
- Parâmetros de pixelização totalmente personalizáveis
- Pré-visualização em tempo real
- Processamento em segundo plano com indicação de progresso
- Exportação das imagens convertidas

---

## Estrutura do Projeto

```
8_bitify/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências Python
├── README.md               # Este arquivo
├── config/
│   └── constants.py        # Presets, constantes de tema e estilos
├── core/
│   ├── image_processor.py  # Funções de processamento de imagem
│   └── worker.py           # Thread de processamento em segundo plano
└── ui/
    ├── components.py       # Componentes de UI reutilizáveis
    └── main_window.py      # Janela principal da aplicação
```

---

## Instalação

1. Clone o repositório
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Uso

Execute a aplicação:

```bash
python main.py
```

### Como Usar

1. **Carregar uma imagem**: Arraste e solte um arquivo de imagem na área indicada, ou clique para navegar pelos arquivos
2. **Selecionar um preset**: Escolha entre as configurações predefinidas (Game Boy, NES, etc.)
3. **Ajustar parâmetros**: Refine o tamanho do pixel, número de cores, nível de detalhe e outras configurações
4. **Converter**: Clique no botão **"CONVERTER"** para processar a imagem
5. **Salvar**: Exporte o pixel art convertido para um arquivo

### Presets Disponíveis

| Preset | Descrição |
|---|---|
| **Personagem Principal** | Otimizado para sprites de personagens |
| **Inimigo** | Adequado para sprites de inimigos e NPCs |
| **Item / Objeto** | Para objetos e itens pequenos |
| **Cenário** | Para imagens de fundo e cenários |
| **Game Boy** | Paleta clássica de 4 cores em tons de verde |
| **NES** | Paleta estilo NES com 16 cores |
| **VGA Retrô** | Paleta VGA com 256 cores |
| **Ultra Detalhe** | Preservação máxima de detalhes |
| **Pixel Grande** | Pixels grandes e marcantes |

---

## Arquitetura

O projeto segue princípios de código limpo, com separação clara entre camadas:

```
Separação de Responsabilidades  →  UI, lógica de negócio e processamento isolados
Responsabilidade Única          →  Cada módulo tem um propósito claro e focado
Reusabilidade                   →  Componentes de UI modulares e reutilizáveis
Manutenibilidade                →  Nomenclatura clara, documentação e estrutura consistente
```

### Decisões de Design

1. **Processamento em Segundo Plano**: O processamento de imagens roda em uma thread separada para manter a UI responsiva
2. **Sistema de Presets**: Configurações predefinidas para os casos de uso mais comuns
3. **UI Customizável**: Constantes de tema permitem alterações de estilo com facilidade
4. **Tratamento de Erros**: Erros tratados de forma elegante com feedback visual ao usuário

---

## Tecnologias

| Categoria | Tecnologia |
|---|---|
| Interface Gráfica | PyQt6 |
| Processamento de Imagem | Pillow |

---
