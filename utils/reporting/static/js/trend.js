// 测试趋势报告 JavaScript

// 处理时间标签
function formatTimestamps(timestamps) {
    return timestamps.map(t => {
        const date = new Date(t);
        return date.toLocaleString('zh-CN', {
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    });
}

// 初始化图表
function initCharts(chartData) {
    console.log('initCharts函数被调用');
    console.log('chartData:', chartData);
    
    const formattedLabels = formatTimestamps(chartData.timestamps);
    console.log('格式化后的标签:', formattedLabels);
    
    // 检查Chart对象是否存在
    if (typeof Chart === 'undefined') {
        console.error('Chart对象未加载');
        return;
    }
    
    // 通过率趋势图
    const passRateCanvas = document.getElementById('passRateChart');
    console.log('passRateCanvas:', passRateCanvas);
    if (passRateCanvas) {
        const passRateCtx = passRateCanvas.getContext('2d');
        console.log('passRateCtx:', passRateCtx);
        if (passRateCtx) {
            try {
                new Chart(passRateCtx, {
                    type: 'line',
                    data: {
                        labels: formattedLabels,
                        datasets: [{
                            label: '通过率 (%)',
                            data: chartData.pass_rates,
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.3,
                            fill: true,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: '测试通过率趋势'
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100,
                                title: {
                                    display: true,
                                    text: '通过率 (%)'
                                }
                            }
                        }
                    }
                });
                console.log('通过率趋势图创建成功');
            } catch (error) {
                console.error('创建通过率趋势图时出错:', error);
            }
        }
    }

    // 测试数量趋势图
    const testCountCanvas = document.getElementById('testCountChart');
    console.log('testCountCanvas:', testCountCanvas);
    if (testCountCanvas) {
        const testCountCtx = testCountCanvas.getContext('2d');
        console.log('testCountCtx:', testCountCtx);
        if (testCountCtx) {
            try {
                new Chart(testCountCtx, {
                    type: 'bar',
                    data: {
                        labels: formattedLabels,
                        datasets: [{
                            label: '总测试数',
                            data: chartData.total_tests,
                            backgroundColor: '#17a2b8'
                        }, {
                            label: '失败测试数',
                            data: chartData.failed_tests,
                            backgroundColor: '#dc3545'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: '测试数量趋势'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '测试数量'
                                }
                            }
                        }
                    }
                });
                console.log('测试数量趋势图创建成功');
            } catch (error) {
                console.error('创建测试数量趋势图时出错:', error);
            }
        }
    }

    // 执行时长趋势图
    const durationCanvas = document.getElementById('durationChart');
    console.log('durationCanvas:', durationCanvas);
    if (durationCanvas) {
        const durationCtx = durationCanvas.getContext('2d');
        console.log('durationCtx:', durationCtx);
        if (durationCtx) {
            try {
                new Chart(durationCtx, {
                    type: 'line',
                    data: {
                        labels: formattedLabels,
                        datasets: [{
                            label: '执行时长 (秒)',
                            data: chartData.durations,
                            borderColor: '#ffc107',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
                            tension: 0.3,
                            fill: true,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: '执行时长趋势'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '执行时长 (秒)'
                                }
                            }
                        }
                    }
                });
                console.log('执行时长趋势图创建成功');
            } catch (error) {
                console.error('创建执行时长趋势图时出错:', error);
            }
        }
    }

    // 测试状态分布
    const statusCanvas = document.getElementById('statusChart');
    console.log('statusCanvas:', statusCanvas);
    if (statusCanvas) {
        const statusCtx = statusCanvas.getContext('2d');
        console.log('statusCtx:', statusCtx);
        if (statusCtx) {
            try {
                const lastIndex = chartData.pass_rates.length - 1;
                const lastPassed = chartData.total_tests[lastIndex] - chartData.failed_tests[lastIndex] - chartData.skipped_tests[lastIndex];
                console.log('lastPassed:', lastPassed);
                
                new Chart(statusCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['通过', '失败', '跳过'],
                        datasets: [{
                            data: [lastPassed, chartData.failed_tests[lastIndex], chartData.skipped_tests[lastIndex]],
                            backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: '最近测试状态分布'
                            },
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
                console.log('测试状态分布图创建成功');
            } catch (error) {
                console.error('创建测试状态分布图时出错:', error);
            }
        }
    }
}

// 初始化模块图表
function initModuleCharts(chartData, moduleData) {
    const formattedLabels = formatTimestamps(chartData.timestamps);
    
    Object.entries(moduleData).forEach(([module, data], index) => {
        // 模块通过率趋势
        const modulePassRateCtx = document.getElementById(`module-pass-rate-${index}`).getContext('2d');
        new Chart(modulePassRateCtx, {
            type: 'line',
            data: {
                labels: formattedLabels,
                datasets: [{
                    label: '通过率 (%)',
                    data: data.pass_rates,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${module} 通过率趋势`
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '通过率 (%)'
                        }
                    }
                }
            }
        });

        // 模块执行时长趋势
        const moduleDurationCtx = document.getElementById(`module-duration-${index}`).getContext('2d');
        new Chart(moduleDurationCtx, {
            type: 'line',
            data: {
                labels: formattedLabels,
                datasets: [{
                    label: '执行时长 (秒)',
                    data: data.durations,
                    borderColor: '#ffc107',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${module} 执行时长趋势`
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '执行时长 (秒)'
                        }
                    }
                }
            }
        });
    });
}

// 初始化标签切换功能
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // 移除所有active类
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // 添加active类到当前标签
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // 初始化第一个标签为active
    document.querySelector('.tab')?.classList.add('active');
    document.querySelector('.tab-content')?.classList.add('active');
}

// 等待Chart.js加载完成后再初始化图表
function initWhenChartLoaded() {
    if (typeof Chart !== 'undefined') {
        console.log('Chart.js加载完成，开始初始化图表');
        console.log('chartData:', window.chartData);
        
        if (window.chartData) {
            console.log('开始初始化核心指标趋势图表');
            initCharts(window.chartData);
            console.log('开始初始化模块级分析图表');
            initModuleCharts(window.chartData, window.chartData.module_data);
        } else {
            console.error('chartData不存在');
        }
        
        console.log('开始初始化标签页');
        initTabs();
        console.log('初始化完成');
    } else {
        console.log('等待Chart.js加载...');
        setTimeout(initWhenChartLoaded, 100);
    }
}

// 开始初始化
initWhenChartLoaded();
