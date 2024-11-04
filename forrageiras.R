# Carregar a biblioteca plotly
library(plotly)

# Função para calcular a Taxa de Crescimento da Cultura (TCC)
calcular_TCC <- function(TAL, IAF) {
  TCC <- TAL * IAF
  return(TCC)
}

# Função para calcular a Taxa de Crescimento Relativo (TCR)
calcular_TCR <- function(TAL, RAF) {
  TCR <- TAL * RAF
  return(TCR)
}

# Função para calcular a Razão de Área Foliar (RAF)
calcular_RAF <- function(AFE, RPF) {
  RAF <- AFE * RPF
  return(RAF)
}

# Solicitação dos parâmetros de entrada
#TAL <- as.numeric(readline(prompt = "Digite a Taxa de Assimilação Líquida (exemplo: 0.5): "))
#IAF <- as.numeric(readline(prompt = "Digite o Índice de Área Foliar (exemplo: 0.8): "))
#AFE <- as.numeric(readline(prompt = "Digite a Área Foliar Específica (exemplo: 0.2): "))
#RPF <- as.numeric(readline(prompt = "Digite a Razão de Peso Foliar (exemplo: 0.6): "))

TAL <- 0.5
IAF <- 0.8
AFE <- 0.2
RPF <- 0.6
duracao <- as.numeric(readline(prompt = "Digite em dias quanto tempo você que analizar "))
# Simulação do crescimento da planta
tempo <- seq(0, duracao, by = 1) # Período de tempo em dias

# Cálculo dos parâmetros de crescimento
TCC <- calcular_TCC(TAL, IAF)
RAF <- calcular_RAF(AFE, RPF)
TCR <- calcular_TCR(TAL, RAF)

# Cálculo da biomassa acumulada
biomassa <- numeric(length(tempo))
biomassa[1] <- 1 # Biomassa inicial100

for (i in 2:length(tempo)) {
  biomassa[i] <- biomassa[i-1] * exp(TCR)
}
fig <- plot_ly(x = ~tempo, y = ~biomassa, type = 'scatter', mode = 'lines') %>%
  layout(title = "Crescimento da Planta Forrageira",
         xaxis = list(title = "Tempo (dias)"),
         yaxis = list(title = "Biomassa acumulada"))

fig
