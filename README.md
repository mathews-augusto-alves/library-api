# API Library - Sistema de Gerenciamento de Livros e Empréstimos    


teste

Uma API REST para gerenciamento de livros, usuários, pessoas e empréstimos de livros, construída com FastAPI seguindo princípios de Clean Architecture.

## 📚 **Informações Importantes**

> **💡 Decisões Técnicas e Justificativas**: consulte o arquivo [`docs/DECISOES_TECNICAS.md`](./docs/DECISOES_TECNICAS.md).

> **🚀 Plano de Evolução**: consulte o arquivo [`docs/PLANO_EVOLUCAO.md`](./docs/PLANO_EVOLUCAO.md).

> **🎯 Liderança e Coordenação**: consulte o arquivo [`docs/LIDERANCA_COORDENACAO.md`](./docs/LIDERANCA_COORDENACAO.md).

## 🚀 **Tecnologias**

### **Backend & Framework**
- **Python 3.13+** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM com tipagem estática
- **PostgreSQL 16** - Banco de dados relacional
- **Redis 7** - Cache em memória
- **Poetry** - Gerenciamento de dependências
- **Docker & Docker Compose** - Containerização
- **JWT** - Autenticação baseada em tokens
- **Pydantic 2** - Validação de dados e serialização

### **Monitoramento & Observabilidade**
- **Prometheus** - Coleta e armazenamento de métricas
- **Grafana** - Visualização de dashboards e alertas
- **Métricas HTTP** - Requisições, latência e erros
- **Métricas de Cache** - Performance do Redis
- **Métricas de Banco** - Conexões e queries
- **Métricas de Aplicação** - Memória e CPU

## 📋 **Pré-requisitos**

- Python 3.13 ou superior
- Docker e Docker Compose
- Poetry (instalação: `pip install poetry`)

## 🏗️ **Estrutura do Projeto**

```
src/
├── domain/                 # Camada de domínio (entidades, regras de negócio)
│   ├── model/             # Modelos de domínio
│   ├── ports/             # Contratos/Protocolos
│   └── exceptions.py      # Exceções de domínio
├── application/            # Camada de aplicação
│   ├── service/           # Serviços de aplicação
│   └── usecase/           # Casos de uso
├── infrastructure/         # Camada de infraestrutura
│   ├── config/            # Configurações e factories
│   ├── repository/        # Implementações de repositório
│   ├── security/          # Autenticação e segurança
│   ├── cache/             # Cliente Redis
│   └── monitoring/        # Métricas Prometheus
└── presentation/           # Camada de apresentação
    ├── controllers/       # Controladores
    ├── routes/            # Rotas FastAPI
    └── dto/               # Objetos de transferência de dados
```

## 🏛️ **Arquitetura da Aplicação**

### **Diagrama de Arquitetura Completa**

```mermaid
graph TB
    %% Usuários e Clientes
    Client[🌐 Cliente/API Consumer]
    Admin[👨‍💼 Administrador]
    
    %% Camada de Apresentação
    subgraph "🎨 Camada de Apresentação (Presentation)"
        Routes[🚦 FastAPI Routes]
        Controllers[🎮 Controllers]
        Middleware[🔧 Middleware]
        DTOs[📋 DTOs]
    end
    
    %% Camada de Aplicação
    subgraph "⚙️ Camada de Aplicação (Application)"
        UseCases[🧠 Use Cases]
        Services[🔧 Services]
        Validators[✅ Validators]
    end
    
    %% Camada de Domínio
    subgraph "🏛️ Camada de Domínio (Domain)"
        Models[📦 Domain Models]
        Ports[🔌 Ports/Protocols]
        Exceptions[⚠️ Exceptions]
        Enums[🔢 Enums]
    end
    
    %% Camada de Infraestrutura
    subgraph "🏗️ Camada de Infraestrutura (Infrastructure)"
        Repositories[🗄️ Repositories]
        Database[🐘 PostgreSQL]
        Cache[🔴 Redis Cache]
        Security[🔐 JWT Auth]
        Monitoring[📊 Prometheus Metrics]
        Logging[📝 Logging System]
    end
    
    %% Sistema de Monitoramento
    subgraph "📈 Sistema de Monitoramento"
        Prometheus[📊 Prometheus]
        Grafana[📊 Grafana]
        Metrics[📈 Métricas HTTP/Cache/DB]
    end
    
    %% Containers e Orquestração
    subgraph "🐳 Containerização"
        Docker[🐳 Docker]
        Compose[📦 Docker Compose]
    end
    
    %% Fluxo de Dados
    Client --> Routes
    Admin --> Routes
    
    Routes --> Controllers
    Controllers --> UseCases
    UseCases --> Services
    Services --> Repositories
    
    Repositories --> Database
    Repositories --> Cache
    
    Controllers --> DTOs
    DTOs --> Models
    
    %% Middleware e Validação
    Routes --> Middleware
    Middleware --> Controllers
    
    UseCases --> Validators
    Validators --> Models
    
    %% Segurança
    Routes --> Security
    Security --> Controllers
    
    %% Monitoramento
    Middleware --> Monitoring
    Monitoring --> Prometheus
    Prometheus --> Grafana
    
    %% Logging
    Controllers --> Logging
    Services --> Logging
    Repositories --> Logging
    
    %% Containerização
    Database --> Docker
    Cache --> Docker
    Prometheus --> Docker
    Grafana --> Docker
    
    %% Estilos
    classDef presentation fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef application fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef domain fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef infrastructure fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef monitoring fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef containerization fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    
    class Routes,Controllers,DTOs,Middleware presentation
    class UseCases,Services,Validators application
    class Models,Ports,Exceptions,Enums domain
    class Repositories,Database,Cache,Security,Monitoring,Logging infrastructure
    class Prometheus,Grafana,Metrics monitoring
    class Docker,Compose containerization
```

### **Fluxo de Requisição Detalhado**

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Routes
    participant M as Middleware
    participant CT as Controller
    participant UC as UseCase
    participant S as Service
    participant REP as Repository
    participant DB as Database
    participant CA as Cache
    participant MON as Monitoring
    
    C->>R: POST /api/v1/usuarios
    R->>M: Validação e Autenticação
    M->>MON: Registra Métricas HTTP
    
    alt Cache Hit
        M->>CA: Busca dados
        CA-->>M: Retorna dados
        M-->>C: Resposta com dados do cache
    else Cache Miss
        M->>CT: Delega para Controller
        CT->>UC: Executa regra de negócio
        UC->>S: Chama Service
        S->>REP: Acessa Repository
        REP->>DB: Query no banco
        DB-->>REP: Resultado
        REP-->>S: Dados do domínio
        S-->>UC: Dados processados
        UC-->>CT: Resposta do UseCase
        CT-->>M: Resposta do Controller
        
        M->>CA: Armazena no cache
        M->>MON: Registra métricas de cache
        M-->>C: Resposta final
    end
    
    Note over MON: Métricas coletadas:<br/>- HTTP requests<br/>- Latência<br/>- Cache hits/misses<br/>- DB queries
```

### **Componentes e Responsabilidades**

| Camada | Componente | Responsabilidade | Tecnologia |
|---------|------------|------------------|------------|
| **🎨 Presentation** | Routes | Endpoints HTTP, validação | FastAPI |
| **🎨 Presentation** | Controllers | Orquestração, DTOs | Python Classes |
| **🎨 Presentation** | Middleware | Métricas, logs, CORS | Custom Middleware |
| **⚙️ Application** | UseCases | Regras de negócio | Python Classes |
| **⚙️ Application** | Services | Operações atômicas | Python Classes |
| **🏛️ Domain** | Models | Entidades de negócio | Python Dataclasses |
| **🏛️ Domain** | Ports | Contratos/Protocolos | Python Protocols |
| **🏗️ Infrastructure** | Repositories | Persistência de dados | SQLAlchemy |
| **🏗️ Infrastructure** | Database | Armazenamento | PostgreSQL |
| **🏗️ Infrastructure** | Cache | Performance | Redis |
| **🏗️ Infrastructure** | Security | Autenticação | JWT |
| **📈 Monitoring** | Prometheus | Coleta de métricas | Prometheus |
| **📈 Monitoring** | Grafana | Visualização | Grafana |

### **Padrões Arquiteturais Aplicados**

- **🏗️ Clean Architecture**: Separação clara de responsabilidades
- **🔌 Dependency Inversion**: Dependências de alto nível não dependem de baixo nível
- **🏭 Factory Pattern**: Criação centralizada de dependências
- **📋 Repository Pattern**: Abstração da persistência
- **🎯 Use Case Pattern**: Regras de negócio isoladas
- **🔧 Service Layer**: Operações atômicas de negócio
- **📊 Observer Pattern**: Métricas e logs automáticos

## 🚀 **Como Executar**

### **🐳 Opção 1: Com Docker (Recomendado)**

#### 1. Clone e Configure
```bash
git clone <repository-url>
cd api-library
cp env.example .env
```

#### 2. Execute com Docker Compose
```bash
# Iniciar todos os serviços (API, PostgreSQL, Redis, Prometheus, Grafana)
docker-compose up -d

# Verificar status
docker-compose ps
```

#### 3. Acesse os Serviços
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

---

### **💻 Opção 2: Desenvolvimento Local**

#### 1. Clone e Instale Dependências
```bash
git clone <repository-url>
cd api-library
poetry install
```

#### 2. Configure Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword
DATABASE_URL=postgresql+psycopg://appuser:apppassword@localhost:5432/appdb

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true

# JWT
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Timezone
APP_TZ=America/Sao_Paulo
```

#### 3. Inicie os Serviços Locais
```bash
# Iniciar apenas PostgreSQL e Redis
docker-compose up -d postgres redis

# Verificar status
docker-compose ps
```

#### 4. Execute a Aplicação
```bash
# Desenvolvimento (com reload automático)
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: http://localhost:8000

### 5. Documentação da API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testes

```bash
# Executar todos os testes
poetry run pytest

# Executar com coverage
poetry run pytest --cov=src
```

## 🔍 **Monitoramento e Observabilidade**

### **Acessar Dashboards**

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### **Verificar Métricas da Aplicação**

```bash
# Endpoint de métricas Prometheus
curl http://localhost:8000/metrics

# Ver logs dos containers
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis
```

### **Dashboard Grafana**

O projeto inclui um dashboard pré-configurado **"API Library - Dashboard Técnico"** com:
- **Requisições por minuto** e **latência**
- **Status das requisições** (2xx, 4xx, 5xx)
- **Performance do cache Redis** (hits/misses)
- **Métricas de banco de dados**
- **Performance da aplicação** (memória/CPU)

## 📞 **Dúvidas**

Para dúvidas, entre em contato:
- **Email**: mathews.alves.job@outlook.com
