// Variáveis globais para os gráficos
let creationChart = null;
let uploadChart = null;
let viewsChart = null;
let machineChart = null;

// Configuração do tema escuro para os gráficos
const darkTheme = {
    color: '#ffffff',
    grid: {
        borderColor: '#444',
        color: '#333'
    },
    text: {
        color: '#ffffff'
    }
};

// Função para renderizar o gráfico de criação
function renderCreationChart(metrics) {
    const ctx = document.getElementById('creationChart').getContext('2d');

    // Destruir o gráfico existente, se houver
    if (creationChart) {
        creationChart.destroy();
    }

    const labels = metrics.map(metric => metric.data);
    const dataPoints = metrics.map(metric => metric.cortes);
    const systemInfo = metrics.map(metric => `${metric.processador}, RAM: ${metric.ram}, GPU: ${metric.gpu}`);

    creationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cortes Criados',
                data: dataPoints,
                backgroundColor: 'rgba(0, 179, 0, 0.6)',
                borderColor: 'rgba(0, 179, 0, 1)',
                borderWidth: 1,
                barThickness: 'flex',
                maxBarThickness: 35
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(tooltipItem) {
                            const index = tooltipItem.dataIndex;
                            return [
                                `Cortes: ${tooltipItem.raw}`,
                                `Sistema: ${systemInfo[index]}`
                            ];
                        }
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}

// Função para renderizar o gráfico de upload
function renderUploadChart(uploadMetrics) {
    const ctx = document.getElementById('uploadChart').getContext('2d');

    // Destruir o gráfico existente, se houver
    if (uploadChart) {
        uploadChart.destroy();
    }

    const labels = uploadMetrics.map(metric => metric.data);
    const cortesTikTokData = uploadMetrics.map(metric => metric.Cortes_tiktok);
    const cortesKwaiData = uploadMetrics.map(metric => metric.Cortes_kwai);

    uploadChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Cortes TikTok',
                    data: cortesTikTokData,
                    backgroundColor: 'rgba(0, 179, 0, 0.6)',
                    borderColor: 'rgba(0, 179, 0, 1)',
                    borderWidth: 1,
                    barThickness: 'flex',
                    maxBarThickness: 35
                },
                {
                    label: 'Cortes Kwai',
                    data: cortesKwaiData,
                    backgroundColor: 'rgba(0, 102, 204, 0.6)',
                    borderColor: 'rgba(0, 102, 204, 1)',
                    borderWidth: 1,
                    barThickness: 'flex',
                    maxBarThickness: 35
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}
function renderViewsChart(data) {
    console.log("Renderizando gráfico de views:", data);

    // Verificar se o elemento canvas existe
    const canvas = document.getElementById('viewsChart');
    if (!canvas) {
        console.error("Elemento <canvas> com ID 'viewsChart' não encontrado.");
        return;
    }

    // Verificar se há dados disponíveis
    if (!data || data.length === 0) {
        console.warn("Nenhum dado disponível para renderizar o gráfico.");
        // Exibir uma mensagem ou limpar o gráfico existente
        if (window.viewsChart) {
            window.viewsChart.destroy(); // Limpa o gráfico existente, se necessário
        }
        return;
    }

    const ctx = canvas.getContext('2d');

    // Destruir gráfico existente (se necessário)
    if (window.viewsChart) {
        window.viewsChart.destroy();
    }

    // Criar um novo gráfico
    window.viewsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(metric => metric.date),
            datasets: [{
                label: 'Views',
                data: data.map(metric => metric.value),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                },
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Data',
                    },
                },
                y: {
                    title: {
                        display: true,
                        text: 'Views',
                    },
                },
            },
        },
    });
}
// Função para renderizar o gráfico de métricas da máquina
function renderMachineChart(machineMetrics) {
    const ctx = document.getElementById('machineChart').getContext('2d');

    // Destruir o gráfico existente, se houver
    if (machineChart) {
        machineChart.destroy();
    }

    const labels = machineMetrics.map(metric => metric.Timestampp);
    
    // Remover '%' e converter para número
    const cpuUtilization = machineMetrics.map(metric => {
        return parseFloat(metric.CPUUtilization.replace('%', ''));
    });
    
    const gpuUtilization = machineMetrics.map(metric => {
        return parseFloat(metric.GPUUtilization.replace('%', ''));
    });
    
    // Remover 'MB' e converter para número
    const memoryUsage = machineMetrics.map(metric => {
        return parseFloat(metric.MemóriaPercent.replace('MB', '').trim());
    });

    machineChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'CPU Utilização',
                    data: cpuUtilization,
                    backgroundColor: 'rgba(0, 179, 0, 0.6)',
                    borderColor: 'rgba(0, 179, 0, 1)',
                    borderWidth: 1
                },
                {
                    label: 'GPU Utilização',
                    data: gpuUtilization,
                    backgroundColor: 'rgba(0, 102, 204, 0.6)',
                    borderColor: 'rgba(0, 102, 204, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Memória Utilizada',
                    data: memoryUsage,
                    backgroundColor: 'rgba(255, 165, 0, 0.6)',
                    borderColor: 'rgba(255, 165, 0, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            }
        }
    });
}

// Função para atualizar as métricas na página inicial
function updateDashboardMetrics(creationMetrics, uploadMetrics) {
    // Cálculos totais
    const totalCuts = creationMetrics.reduce((sum, metric) => sum + (parseInt(metric.cortes) || 0), 0);
    const totalTikTok = uploadMetrics.reduce((sum, metric) => sum + (parseInt(metric.Cortes_tiktok) || 0), 0);
    const totalKwai = uploadMetrics.reduce((sum, metric) => sum + (parseInt(metric.Cortes_kwai) || 0), 0);

    // Atualizar os cards de métricas
    document.querySelectorAll('.metric-value')[0].textContent = totalCuts.toLocaleString();
    document.querySelectorAll('.metric-value')[1].textContent = totalTikTok.toLocaleString();
    document.querySelectorAll('.metric-value')[2].textContent = totalKwai.toLocaleString();
}

// Função para atualizar todas as visualizações
async function updateDashboard() {
    try {
        const { creationMetrics, uploadMetrics, views_metrics, machine_metrics  } = await fetchMetrics();
        console.log("Métricas carregadas:", metrics);

        // Atualizar métricas gerais
        updateDashboardMetrics(creationMetrics, uploadMetrics);
        
        // Atualizar gráficos
        renderCreationChart(creationMetrics);
        renderUploadChart(uploadMetrics);
  
        renderMachineChart(machine_metrics);
        
        // Atualizar tabelas
        updateTables(creationMetrics, uploadMetrics, views_metrics, machine_metrics);

        // Atualizar gráfico de views
        const viewsMetrics = metrics.views_metrics || [];
        console.log("Métricas de views recebidas:", viewsMetrics);
        renderViewsChart(viewsMetrics);

    } catch (error) {
        console.error('Erro ao atualizar o dashboard:', error);
    }
}

// Função para atualizar as tabelas
function updateTables(creationMetrics, uploadMetrics, views_metrics, machine_metrics) {

    // Ordenar os dados de métricas de criação por data (mais recente primeiro)
    creationMetrics.sort((a, b) => new Date(b.data) - new Date(a.data));

    // Ordenar os dados de métricas de upload por data (mais recente primeiro)
    uploadMetrics.sort((a, b) => new Date(b.data) - new Date(a.data));

    // Ordenar os dados de métricas de views por data (mais recente primeiro)
    views_metrics.sort((a, b) => new Date(b.Data) - new Date(a.Data));

    // Ordenar os dados de métricas de máquina por timestamp (mais recente primeiro)
    machine_metrics.sort((a, b) => new Date(b.Data) - new Date(a.Data));

    // Atualizar tabela de métricas de machine
    const machineMetricsTable = document.querySelector('#machineMetricsTable tbody');
    machineMetricsTable.innerHTML = machine_metrics.map(metric => `
        <tr>
            <td>${metric.Timestampp || 'N/A'}</td>
            <td>${metric.CPUUtilization || 'N/A'}</td>
            <td>${metric.GPUUtilization || 'N/A'}</td>
            <td>${metric.GPUCUDA || 'N/A'}</td>
            <td>${metric.GPUVideoEncode || 'N/A'}</td>
            <td>${metric.GPUVideoDecode || 'N/A'}</td>
            <td>${metric.GPUClockVídeo || 'N/A'}</td>
            <td>${metric.GPUClockMemória || 'N/A'}</td>
            <td>${metric.GPUTemperature || 'N/A'}</td>
            <td>${metric.MemóriaUsada || 'N/A'}</td>
            <td>${metric.MemóriaTotal || 'N/A'}</td>
            <td>${metric.MemóriaFree || 'N/A'}</td>
            <td>${metric.MemóriaPercent || 'N/A'}</td>
        </tr>
    `).join('');

    // Atualizar tabela de métricas de criação
    const creationTable = document.querySelector('#creationMetricsTable tbody');
    creationTable.innerHTML = creationMetrics.map(metric => `
        <tr>
            <td>${metric.data || 'N/A'}</td>
            <td>${metric.cortes || '0'}</td>
            <td>${metric.processador || 'N/A'}</td>
            <td>${metric.ram || 'N/A'}</td>
            <td>${metric.gpu || 'N/A'}</td>
        </tr>
    `).join('');

    // Atualizar tabela de métricas de upload
    const uploadTable = document.querySelector('#uploadMetricsTable tbody');
    uploadTable.innerHTML = uploadMetrics.map(metric => `
        <tr>
            <td>${metric.data || 'N/A'}</td>
            <td>${metric.Cortes_tiktok || '0'}</td>
            <td>${metric.Cortes_kwai || '0'}</td>
            <td>${metric.machine || 'N/A'}</td>
        </tr>
    `).join('');

    // Atualizar tabela de métricas de views
    const viewsTable = document.querySelector('#viewsMetricsTable tbody');
    viewsTable.innerHTML = views_metrics.map(metric => `
        <tr>
            <td>${metric.Tiktok || 'N/A'}</td>
            <td>${metric.Data || 'N/A'}</td>
            <td>${metric.Views_Tiktok || 'N/A'}</td>
            <td>${metric.Curtidas_Tiktok || 'N/A'}</td>
            <td>${metric.Kwai || 'N/A'}</td>
            <td>${metric.Views_Kwai || 'N/A'}</td>
            <td>${metric.Curtidas_Kwai || 'N/A'}</td>
        </tr>
    `).join('');

}



// Inicialização e atualizações periódicas
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
    // Atualizar a cada minuto
    setInterval(updateDashboard, 60000);
});