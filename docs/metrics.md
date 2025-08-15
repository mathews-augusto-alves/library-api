# 📊 Sistema de Monitoramento - API Library

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      API        │    │   Prometheus    │    │     Grafana     │
│   (Porta 8000)  │    │   (Porta 9090)  │    │   (Porta 3000)  │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │  Métricas │  │    │  │  Coleta   │  │    │  │Dashboard  │  │
│  │  HTTP     │  │    │  │  Métricas │  │    │  │  Visual   │  │
│  │  Cache    │  │    │  │  Storage  │  │    │  │  Alertas  │  │
│  │  Database │  │    │  │  Query    │  │    │  │  Reports  │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Redis      │    │    PostgreSQL   │    │                 │
│   (Porta 6379)  │    │   (Porta 5432)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Componentes do Sistema

### 1. **Prometheus** - Coletor de Métricas
- **Porta**: 9090
- **Função**: Coleta e armazena métricas de tempo
- **Configuração**: `docker/monitoring/prometheus/prometheus.yml`
- **Targets**: API, PostgreSQL, Redis

### 2. **Grafana** - Visualização e Dashboards
- **Porta**: 3000
- **Credenciais**: admin/admin
- **Função**: Criação de dashboards e alertas
- **Configuração**: `docker/monitoring/grafana/`

### 3. **Redis** - Cache e Métricas
- **Porta**: 6379
- **Função**: Cache de dados e métricas de performance
- **Configuração**: `src/infrastructure/cache/redis_client.py`

## 🎨 Dashboard Disponível

### 📊 **Dashboard: "API Library - Dashboard Técnico"**

#### **Painel 1: Requisições por Minuto**
- **Métrica**: `rate(http_requests_total[1m])`
- **Visualização**: Time Series
- **Descrição**: Quantas requisições a API recebe por minuto
- **Como interpretar**: 
  - Linha estável = tráfego constante
  - Picos = picos de tráfego
  - Vales = períodos de baixa atividade

#### **Painel 2: Latência das Requisições (95º percentil)**
- **Métrica**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **Visualização**: Time Series
- **Descrição**: 95º percentil de latência das requisições
- **Como interpretar**:
  - < 100ms = Excelente
  - 100-500ms = Bom
  - 500ms-1s = Aceitável
  - > 1s = Problema

#### **Painel 3: Status das Requisições**
- **Métrica**: `sum(rate(http_requests_total[5m])) by (status_code)`
- **Visualização**: Pie Chart
- **Descrição**: Distribuição de códigos de status HTTP
- **Como interpretar**:
  - 2xx (verde) = Sucesso
  - 4xx (amarelo) = Erro do cliente
  - 5xx (vermelho) = Erro do servidor

#### **Painel 4: Erros HTTP por Tipo**
- **Métrica**: `rate(http_errors_total[5m])`
- **Visualização**: Time Series
- **Descrição**: Taxa de erros por tipo (client_error, server_error)
- **Como interpretar**:
  - Linha alta = Muitos erros
  - Linha baixa = Poucos erros
  - Picos = Problemas temporários

#### **Painel 5: Uso de Cache Redis**
- **Métrica**: `rate(redis_commands_total[5m])`, `rate(redis_cache_hits_total[5m])`, `rate(redis_cache_misses_total[5m])`
- **Visualização**: Time Series
- **Descrição**: Comandos Redis, hits e misses por segundo
- **Como interpretar**:
  - Alto = Muito uso de cache
  - Baixo = Pouco uso de cache
  - Zero = Redis pode estar offline

#### **Painel 6: Performance da Aplicação**
- **Métrica**: `app_memory_usage_bytes`, `app_cpu_usage_percent`
- **Visualização**: Time Series
- **Descrição**: Uso de memória e CPU da aplicação
- **Como interpretar**:
  - Memória alta = Possível vazamento
  - CPU alta = Processamento intensivo
  - Valores estáveis = Aplicação saudável

## 🚀 Como Testar o Sistema

### **1. Verificar se os Containers Estão Rodando**
```bash
docker-compose ps
```
**Deve mostrar**: Todos os serviços como "Up"

### **2. Testar Endpoint de Métricas**
```bash
curl http://localhost:8000/metrics
```
**Resposta esperada**: Texto com métricas Prometheus

### **3. Verificar Prometheus**
- Acesse: http://localhost:9090
- Vá em **Status > Targets**
- **Deve mostrar**: Todos os targets como "UP"

### **4. Verificar Grafana**
- Acesse: http://localhost:3000
- Login: `admin/admin`
- Vá em **Dashboards**
- **Deve mostrar**: "API Library - Dashboard Técnico"

### **5. Gerar Dados de Teste**
```bash
# Cadastrar usuário
curl -X POST "http://localhost:8000/api/v1/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{"nome":"Usuário Teste","email":"teste@teste.com","senha":"123456"}'

# Fazer login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@teste.com","senha":"123456"}'

# Listar usuários
curl "http://localhost:8000/api/v1/usuarios/?page=1&size=10"
```

## 🔍 Indicadores de Funcionamento

### ✅ **Sistema Funcionando Corretamente**
- Endpoint `/metrics` retorna dados Prometheus
- Prometheus mostra targets como "UP"
- Grafana carrega dashboard automaticamente
- Dashboard mostra números > 0
- Métricas aumentam com atividade