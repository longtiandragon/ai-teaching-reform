<template>
  <div class="dashboard-container">
    <div class="dashboard-title">数据大屏控制系统</div>
    
    <!-- 数据概览卡片 -->
    <div class="overview-cards">
      <div class="card">
        <div class="card-title">补贴政策总数</div>
        <div class="card-value">{{ overview.policyCount }}</div>
        <div class="card-subtitle">个</div>
      </div>
      <div class="card">
        <div class="card-title">信贷产品总数</div>
        <div class="card-value">{{ overview.loanCount }}</div>
        <div class="card-subtitle">个</div>
      </div>
      <div class="card">
        <div class="card-title">农产品总数</div>
        <div class="card-value">{{ overview.produceCount }}</div>
        <div class="card-subtitle">个</div>
      </div>
      <div class="card">
        <div class="card-title">总浏览量</div>
        <div class="card-value">{{ overview.totalBrowse }}</div>
        <div class="card-subtitle">次</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <!-- 产品销量趋势图 -->
      <div class="chart-container">
        <div class="chart-header">
          <div class="chart-title">产品销量与浏览数</div>
          <div class="chart-actions">
            <el-button-group>
              <el-button :type="salesChartType === 'bar' ? 'primary' : ''" size="small" @click="switchSalesChart('bar')">柱状图</el-button>
              <el-button :type="salesChartType === 'line' ? 'primary' : ''" size="small" @click="switchSalesChart('line')">折线图</el-button>
            </el-button-group>
            <el-button size="small" @click="saveChartImage('sales')" style="margin-left: 10px;">
              <el-icon><Download /></el-icon> 保存图片
            </el-button>
            <el-button size="small" @click="showSalesData = !showSalesData" style="margin-left: 5px;">
              <el-icon><View /></el-icon> {{ showSalesData ? '隐藏' : '查看' }}数据
            </el-button>
          </div>
        </div>
        <div ref="salesChart" class="chart"></div>
        <!-- 详细数据表格 -->
        <el-table v-if="showSalesData" :data="salesTableData" style="margin-top: 15px;" size="small">
          <el-table-column prop="name" label="产品名称" align="center" />
          <el-table-column prop="sales" label="销题" align="center" />
          <el-table-column prop="browse" label="浏览数" align="center" />
        </el-table>
      </div>
      
      <!-- 数据分布饼图 -->
      <div class="chart-container">
        <div class="chart-header">
          <div class="chart-title">产品分类分布</div>
          <div class="chart-actions">
            <el-button size="small" @click="saveChartImage('pie')">
              <el-icon><Download /></el-icon> 保存图片
            </el-button>
            <el-button size="small" @click="showPieData = !showPieData" style="margin-left: 5px;">
              <el-icon><View /></el-icon> {{ showPieData ? '隐藏' : '查看' }}数据
            </el-button>
          </div>
        </div>
        <div ref="pieChart" class="chart"></div>
        <!-- 详细数据表格 -->
        <el-table v-if="showPieData" :data="pieTableData" style="margin-top: 15px;" size="small">
          <el-table-column prop="name" label="分类" align="center" />
          <el-table-column prop="value" label="数量" align="center" />
          <el-table-column label="占比" align="center">
            <template #default="scope">
              {{ ((scope.row.value / pieTotal) * 100).toFixed(1) }}%
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 月度趋势题-->
    <div class="trend-container">
      <div class="chart-header">
        <div class="chart-title">月增趋势</div>
        <div class="chart-actions">
          <el-button-group>
            <el-button :type="trendChartType === 'bar' ? 'primary' : ''" size="small" @click="switchTrendChart('bar')">柱状图</el-button>
            <el-button :type="trendChartType === 'line' ? 'primary' : ''" size="small" @click="switchTrendChart('line')">折线图</el-button>
          </el-button-group>
          <el-button size="small" @click="saveChartImage('trend')" style="margin-left: 10px;">
            <el-icon><Download /></el-icon> 保存图片
          </el-button>
          <el-button size="small" @click="showTrendData = !showTrendData" style="margin-left: 5px;">
            <el-icon><View /></el-icon> {{ showTrendData ? '隐藏' : '查看' }}数据
          </el-button>
        </div>
      </div>
      <div ref="trendChart" class="chart-large"></div>
      <!-- 详细数据表格 -->
      <el-table v-if="showTrendData" :data="trendTableData" style="margin-top: 15px;" size="small">
        <el-table-column prop="month" label="月份" align="center" />
        <el-table-column prop="sales" label="销题" align="center" />
        <el-table-column prop="browse" label="浏览数" align="center" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import request from '../../utils/request'
import { ElMessage } from 'element-plus'
import { Download, View } from '@element-plus/icons-vue'

// 数据概览
const overview = ref({
  policyCount: 0,
  loanCount: 0,
  produceCount: 0,
  totalBrowse: 0,
  totalSales: 0,
  monthlyIncrease: 0
})

// 图表实例
const salesChart = ref<HTMLElement>()
const pieChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()

let salesChartInstance: echarts.ECharts | null = null
let pieChartInstance: echarts.ECharts | null = null
let trendChartInstance: echarts.ECharts | null = null

// 图表类型和数据显示控题
const salesChartType = ref<'bar' | 'line'>('bar')
const trendChartType = ref<'bar' | 'line'>('line')
const showSalesData = ref(false)
const showPieData = ref(false)
const showTrendData = ref(false)

// 表格数据
const salesTableData = ref<any[]>([])
const pieTableData = ref<any[]>([])
const trendTableData = ref<any[]>([])
const pieTotal = ref(0)

// 获取数据概览
const fetchOverview = async () => {
  try {
    const res = await request.get('/dev-api/statistics/overview')
    if (res.code === 200) {
      overview.value = res.data
    }
  } catch (error) {
    console.error('获取概览数据失败:', error)
  }
}

// 初始化产品销量趋势图
const initSalesChart = async () => {
  if (!salesChart.value) return
  
  try {
    const res = await request.get('/dev-api/statistics/productStats')
    console.log('📊 产品销量数据响题', res)
    console.log('📊 salesData:', res.data?.salesData)
    if (res.code === 200 && res.data.salesData) {
      // 保存表格数据
      salesTableData.value = res.data.salesData
      console.log('📊 销量图表数据已设置:', salesTableData.value)
      
      if (!salesChartInstance) {
        salesChartInstance = echarts.init(salesChart.value)
      }
      
      renderSalesChart(res.data.salesData)
    } else {
      console.warn('⚠️ 销量数据格式不正确:', res)
    }
  } catch (error) {
    console.error('❌ 获取销量数据失败', error)
  }
}

// 渲染产品销量图表
const renderSalesChart = (data: any[]) => {
  if (!salesChartInstance) return
  
  const categories = data.map((item: any) => item.name)
  const salesData = data.map((item: any) => item.sales)
  const browseData = data.map((item: any) => item.browse)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: salesChartType.value === 'bar' ? 'shadow' : 'cross'
      }
    },
    legend: {
      data: ['销题', '浏览数'],
      top: '5%',
      left: 'center',
      textStyle: {
        color: '#5a4a3a'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        color: '#5a4a3a',
        interval: 0,
        rotate: 0  // 横向显示文字
      },
      axisLine: {
        lineStyle: {
          color: '#3b5b8f'
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '销量',
        min: 0,
        max: 50,
        nameTextStyle: {
          color: '#5a4a3a',
          align: 'left'
        },
        nameLocation: 'end',
        nameGap: 10,
        axisLabel: {
          color: '#5a4a3a'
        },
        splitLine: {
          lineStyle: {
            color: '#3b5b8f'
          }
        },
        axisLine: {
          lineStyle: {
            color: '#5470c6'
          }
        }
      },
      {
        type: 'value',
        name: '浏览数',
        min: 0,
        max: 500,
        nameTextStyle: {
          color: '#5a4a3a',
          align: 'right'
        },
        nameLocation: 'end',
        nameGap: 10,
        axisLabel: {
          color: '#5a4a3a'
        },
        splitLine: {
          show: false
        },
        axisLine: {
          lineStyle: {
            color: '#ee6666'
          }
        }
      }
    ],
    series: [
      {
        name: '销量',
        type: salesChartType.value,  // 根据切换按钮
        data: salesData,
        smooth: false,
        yAxisIndex: 0,  // 使用第一个Y轴（左侧题
        itemStyle: {
          color: '#5470c6'
        },
        barWidth: salesChartType.value === 'bar' ? '40%' : undefined,
        lineStyle: salesChartType.value === 'line' ? {
          width: 3
        } : undefined
      },
      {
        name: '浏览数',
        type: salesChartType.value,  // 根据切换按钮
        data: browseData,
        smooth: false,
        yAxisIndex: 1,  // 使用第二个Y轴（右侧题
        itemStyle: {
          color: '#ee6666'
        },
        barWidth: salesChartType.value === 'bar' ? '40%' : undefined,
        lineStyle: salesChartType.value === 'line' ? {
          width: 3
        } : undefined
      }
    ]
  }
  
  salesChartInstance.setOption(option, true)
}

// 切换销量图表类题
const switchSalesChart = (type: 'bar' | 'line') => {
  salesChartType.value = type
  if (salesTableData.value.length > 0) {
    renderSalesChart(salesTableData.value)
  }
}

// 初始化数据分布饼题
const initPieChart = async () => {
  if (!pieChart.value) return
  
  try {
    const res = await request.get('/dev-api/statistics/distribution')
    if (res.code === 200 && res.data.categoryData) {
      // 保存表格数据
      pieTableData.value = res.data.categoryData
      pieTotal.value = res.data.categoryData.reduce((sum: number, item: any) => sum + item.value, 0)
      
      pieChartInstance = echarts.init(pieChart.value)
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          right: '10%',
          top: 'center',
          textStyle: {
            color: '#5a4a3a'
          }
        },
        series: [
          {
            name: '产品分类',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            label: {
              show: true,
              color: '#5a4a3a',
              formatter: '{b}\n{d}%'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 16,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: true,
              lineStyle: {
                color: '#5a4a3a'
              }
            },
            data: res.data.categoryData
          }
        ]
      }
      
      pieChartInstance.setOption(option)
    }
  } catch (error) {
    console.error('获取分布数据失败:', error)
  }
}

// 初始化月度趋势图
const initTrendChart = async () => {
  if (!trendChart.value) return
  
  try {
    const res = await request.get('/dev-api/statistics/monthlyTrend')
    if (res.code === 200 && res.data.months) {
      // 保存表格数据
      trendTableData.value = res.data.months.map((month: string, index: number) => ({
        month,
        sales: res.data.sales[index],
        browse: res.data.browse[index]
      }))
      
      if (!trendChartInstance) {
        trendChartInstance = echarts.init(trendChart.value)
      }
      
      renderTrendChart({
        months: res.data.months,
        sales: res.data.sales,
        browse: res.data.browse
      })
    }
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

// 渲染月度趋势图表
const renderTrendChart = (data: any) => {
  if (!trendChartInstance) return
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: trendChartType.value === 'bar' ? 'shadow' : 'cross'
      }
    },
    legend: {
      data: ['销题', '浏览数'],
      top: '5%',
      left: 'center',
      textStyle: {
        color: '#5a4a3a'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: trendChartType.value === 'bar',
      data: data.months,
      axisLabel: {
        color: '#5a4a3a'
      },
      axisLine: {
        lineStyle: {
          color: '#3b5b8f'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#5a4a3a'
      },
      splitLine: {
        lineStyle: {
          color: '#3b5b8f'
        }
      }
    },
    series: [
      {
        name: '销量',
        type: trendChartType.value,
        smooth: false,
        data: data.sales,
        lineStyle: trendChartType.value === 'line' ? {
          color: '#ee6666',
          width: 3
        } : undefined,
        itemStyle: {
          color: '#ee6666'
        },
        areaStyle: trendChartType.value === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(238, 102, 102, 0.3)'
            }, {
              offset: 1, color: 'rgba(238, 102, 102, 0.05)'
            }]
          }
        } : undefined
      },
      {
        name: '浏览数',
        type: trendChartType.value,
        smooth: false,
        data: data.browse,
        lineStyle: trendChartType.value === 'line' ? {
          color: '#5470c6',
          width: 3
        } : undefined,
        itemStyle: {
          color: '#5470c6'
        },
        areaStyle: trendChartType.value === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(84, 112, 198, 0.3)'
            }, {
              offset: 1, color: 'rgba(84, 112, 198, 0.05)'
            }]
          }
        } : undefined
      }
    ]
  }
  
  trendChartInstance.setOption(option, true)
}

// 切换月度趋势图表类型
const switchTrendChart = (type: 'bar' | 'line') => {
  trendChartType.value = type
  if (trendTableData.value.length > 0) {
    const months = trendTableData.value.map(item => item.month)
    const sales = trendTableData.value.map(item => item.sales)
    const browse = trendTableData.value.map(item => item.browse)
    renderTrendChart({ months, sales, browse })
  }
}

// 保存图表为图片
const saveChartImage = (chartType: 'sales' | 'pie' | 'trend') => {
  let chartInstance: echarts.ECharts | null = null
  let fileName = ''
  
  switch (chartType) {
    case 'sales':
      chartInstance = salesChartInstance
      fileName = `产品销量与浏览数-${salesChartType.value === 'bar' ? '柱状图' : '折线图'}.png`
      break
    case 'pie':
      chartInstance = pieChartInstance
      fileName = '产品分类分布-饼图.png'
      break
    case 'trend':
      chartInstance = trendChartInstance
      fileName = `月增趋势-${trendChartType.value === 'bar' ? '柱状图' : '折线图'}.png`
      break
  }
  
  if (!chartInstance) {
    ElMessage.error('图表未加载完成')
    return
  }
  
  try {
    // 获取图表的base64图片
    const imageUrl = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,  // 提高清晰题
      backgroundColor: '#ffffff'  // 设置背景题
    })
    
    // 创建下载链接
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('图片已保存')
  } catch (error) {
    console.error('保存图片失败:', error)
    ElMessage.error('保存图片失败')
  }
}

// 窗口大小改变时重新渲染图表
const handleResize = () => {
  salesChartInstance?.resize()
  pieChartInstance?.resize()
  trendChartInstance?.resize()
}

// 组件挂载时初始化
onMounted(() => {
  fetchOverview()
  initSalesChart()
  initPieChart()
  initTrendChart()
  
  window.addEventListener('resize', handleResize)
})

// 组件卸载时销毁图表实现
onUnmounted(() => {
  salesChartInstance?.dispose()
  pieChartInstance?.dispose()
  trendChartInstance?.dispose()
  
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
  min-height: 100vh;
  background: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.dashboard-title {
  text-align: center;
  font-size: 32px;
  font-weight: bold;
  color: #5a4a3a;
  margin-bottom: 30px;
  text-shadow: none;
  letter-spacing: 2px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 2px solid #e8e8e8;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(212, 165, 116, 0.2);
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(212, 165, 116, 0.3);
}

.card-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  font-weight: 500;
}

.card-value {
  font-size: 36px;
  font-weight: bold;
  color: #1890ff;
  margin-bottom: 5px;
}

.card-subtitle {
  font-size: 12px;
  color: #999;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.trend-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-title {
  font-size: 18px;
  font-weight: bold;
  color: #5a4a3a;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: 5px;
}

.chart {
  width: 100%;
  height: 300px;
}

.chart-large {
  width: 100%;
  height: 350px;
}

/* Element Plus 按钮样式覆盖 */
:deep(.el-button) {
  border-color: #e8e8e8;
  background-color: white;
  color: #5a4a3a;
}

:deep(.el-button:hover) {
  border-color: #1890ff;
  background-color: #f5f5f5;
  color: #1890ff;
}

:deep(.el-button--primary) {
  background-color: #1890ff;
  border-color: #1890ff;
  color: white;
}

:deep(.el-button--primary:hover) {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

/* Element Plus 表格样式覆盖 */
:deep(.el-table) {
  background-color: white;
  color: #5a4a3a;
}

:deep(.el-table th.el-table__cell) {
  background-color: #1890ff;
  color: #fff;
  border-color: #e8dcc8;
}

:deep(.el-table tr) {
  background-color: white;
}

:deep(.el-table td.el-table__cell) {
  border-color: #e8dcc8;
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: #f5f5f5;
}

/* 响应式设题*/
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .dashboard-title {
    font-size: 24px;
  }
  
  .chart-actions {
    flex-wrap: wrap;
  }
}
</style>

