import {
  Component, AfterViewInit, OnDestroy, ViewChild, ViewChildren, ElementRef, signal, computed, OnInit, QueryList
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, ChartConfiguration } from 'chart.js/auto';
import { ReporteService, DashboardResponse, KPI, IngresoMensual, DistribucionReserva, EspacioStats } from '../../services/reporte.service';
import { Subject, takeUntil } from 'rxjs';

type Kpi = { label: string; value: number; prefix?: string; suffix?: string };

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reportes.component.html',
  styleUrls: ['./reportes.component.css']
})
export class ReportesComponent implements OnInit, AfterViewInit, OnDestroy {

  // Usaremos querySelector en lugar de ViewChild para mayor flexibilidad

  private barChart?: Chart;
  private pieChart?: Chart;
  private lineChart?: Chart;
  private destroy$ = new Subject<void>();

  // Variable para controlar el filtro por meses (selección múltiple)
  selectedMonths: string[] = [];

  // Estados
  loading = signal(false);
  error = signal<string | null>(null);

  // Datos del dashboard como signal para reactividad
  dashboardData = signal<DashboardResponse | null>(null);

  kpis = computed<Kpi[]>(() => {
    const data = this.dashboardData();
    if (!data) return [];
    return data.kpis.map(kpi => ({
      label: kpi.label,
      value: kpi.value,
      prefix: kpi.prefix,
      suffix: kpi.suffix
    }));
  });

  constructor(private reporteService: ReporteService) {}

  ngOnInit(): void {
    this.cargarDashboard();
  }

  ngAfterViewInit(): void {
    console.log('🔍 ngAfterViewInit - Inicializado');
    
    // Si ya tenemos datos, crear los gráficos
    if (this.dashboardData()) {
      this.crearGraficosSiDisponibles();
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    this.barChart?.destroy();
    this.pieChart?.destroy();
    this.lineChart?.destroy();
  }

  cargarDashboard(): void {
    this.loading.set(true);
    this.error.set(null);

    // Debug: Verificar token
    const token = localStorage.getItem('vecindapp_token');
    console.log('🔍 Token encontrado:', token ? 'Sí' : 'No');
    console.log('🔍 Token value:', token);

    // Usar los últimos 6 meses para mostrar más datos
    const ahora = new Date();
    const fechaDesde = new Date(ahora.getFullYear(), ahora.getMonth() - 6, 1); // 6 meses atrás
    const fechaHasta = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0); // Último día del mes actual

    const fechaDesdeStr = fechaDesde.toISOString().split('T')[0];
    const fechaHastaStr = fechaHasta.toISOString().split('T')[0];

    console.log('🔍 Fechas:', { fechaDesdeStr, fechaHastaStr });

    this.reporteService.getDashboard(fechaDesdeStr, fechaHastaStr)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.dashboardData.set(data);
          this.loading.set(false);
          // Crear gráficos después de cargar los datos
          // Usar ngAfterViewInit para asegurar que los ViewChild estén disponibles
          this.crearGraficosSiDisponibles();
        },
        error: (error) => {
          console.error('❌ Error details:', error.error);
          this.error.set(`Error al cargar los report: ${error.msage || error.status || 'Error dconocido'}`);
          this.loading.set(false);
        }
      });
  }

  private crearGraficosSiDisponibles(): void {
    if (!this.dashboardData()) {
      return;
    }
    
    // Usar setTimeout para asegurar que el DOM esté actualizado
    setTimeout(() => {
      try {
        this.makeBar();
        this.makePie();
        this.makeLine();
      } catch (error) {
        console.error('❌ Error creando gráficos:', error);
        // Intentar crear gráficos individualmente para identificar cuál falla
        this.crearGraficosIndividualmente();
      }
    }, 100);
  }

  private crearGraficosIndividualmente(): void {
    try {
      this.makeBar();
    } catch (error) {
      console.error('❌ Error creando gráfico de barras:', error);
    }
    
    try {
      this.makePie();
    } catch (error) {
      console.error('❌ Error creando gráfico de torta:', error);
    }
    
    try {
      this.makeLine();
    } catch (error) {
      console.error('❌ Error creando gráfico de línea:', error);
    }
  }

  public resetFilter(): void {
    console.log('🔄 Reseteando filtro');
    this.selectedMonths = [];
    
    // Recargar datos del dashboard sin filtros
    this.cargarDashboardConFiltros();
  }

  private cargarDashboardConFiltros(): void {
    this.loading.set(true);
    this.error.set(null);

    // Siempre usar el rango de los últimos 6 meses
    const ahora = new Date();
    const fechaDesde = new Date(ahora.getFullYear(), ahora.getMonth() - 6, 1);
    const fechaHasta = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0);

    const fechaDesdeStr = fechaDesde.toISOString().split('T')[0];
    const fechaHastaStr = fechaHasta.toISOString().split('T')[0];

    // Usar selectedMonths (array de meses seleccionados)
    const meses = this.selectedMonths.length > 0 ? this.selectedMonths : undefined;

    console.log('🔍 Cargando dashboard con filtros:', {
      fechaDesde: fechaDesdeStr,
      fechaHasta: fechaHastaStr,
      meses: this.selectedMonths
    });

    this.reporteService.getDashboard(fechaDesdeStr, fechaHastaStr, meses)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          console.log('✅ Dashboard cargado con filtros:', data);
          console.log('🔍 Debug - KPIs recibidos:', data.kpis);
          console.log('🔍 Debug - KPI Espacios Arrendados:', data.kpis[0]);
          this.dashboardData.set(data);
          this.loading.set(false);
          // Crear gráficos después de cargar los datos
          setTimeout(() => {
            this.makeBar();
            this.makePie();
            this.makeLine();
          }, 100);
        },
        error: (error) => {
          console.error('❌ Error cargando dashboard con filtros:', error);
          this.error.set(`Error al cargar los reportes: ${error.message || 'Error desconocido'}`);
          this.loading.set(false);
        }
      });
  }

  private makeBar() {
    const data = this.dashboardData();
    if (!data) {
      return;
    }

    // Destruir gráfico anterior si existe
    this.barChart?.destroy();

    // Verificar si hay datos
    if (!data.ingresos_mensuales || data.ingresos_mensuales.length === 0) {
      return;
    }

    // Buscar el canvas en el DOM
    const canvas = document.querySelector('canvas[data-chart="bar"]') as HTMLCanvasElement;
    if (!canvas) {
      return;
    }

    // Los datos ya vienen filtrados del backend
    const labels = data.ingresos_mensuales.map(item => 
      this.formatearFecha(item.mes)
    );
    
    const chartData = data.ingresos_mensuales.map(item => item.ingresos);

    const cfg: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ingresos (CLP)',
          data: chartData,
          backgroundColor: 'rgba(20, 184, 166, 0.8)',
          borderColor: 'rgba(20, 184, 166, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        // Removido el onClick ya que ahora usamos checkboxes
        plugins: { 
          legend: { display: false }, 
          tooltip: { 
            enabled: true,
            callbacks: {
              label: (context) => `$${this.formatearNumero(Number(context.parsed.y))}`
            }
          } 
        },
        scales: {
          y: {
            ticks: {
              callback: (v: any) => `$${this.formatearNumero(Number(v))}`
            }
          }
        }
      }
    };
    
    this.barChart = new Chart(canvas, cfg);
  }

  private makePie() {
    const data = this.dashboardData();
    if (!data) {
      return;
    }

    // Destruir gráfico anterior si existe
    this.pieChart?.destroy();

    // Verificar si hay datos
    if (!data.distribucion_reservas || data.distribucion_reservas.length === 0) {
      return;
    }

    // Buscar el canvas en el DOM
    const canvas = document.querySelector('canvas[data-chart="pie"]') as HTMLCanvasElement;
    if (!canvas) {
      return;
    }

    const labels = data.distribucion_reservas.map(item => item.espacio);
    const chartData = data.distribucion_reservas.map(item => item.cantidad);

    const cfg: ChartConfiguration<'pie'> = {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{ 
          data: chartData,
          backgroundColor: [
            'rgba(20, 184, 166, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)'
          ],
          borderColor: [
            'rgba(20, 184, 166, 1)',
            'rgba(59, 130, 246, 1)',
            'rgba(16, 185, 129, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(239, 68, 68, 1)',
            'rgba(139, 92, 246, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { 
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: (context) => `${context.label}: ${context.parsed} reservas`
            }
          }
        }
      }
    };
    
    this.pieChart = new Chart(canvas, cfg);
  }

  private makeLine() {
    console.log('🔍 makeLine - Iniciando creación del gráfico de línea');
    
    const data = this.dashboardData();
    if (!data) {
      console.log('❌ makeLine - No hay datos del dashboard');
      return;
    }

    // Destruir gráfico anterior si existe
    this.lineChart?.destroy();

    // Buscar el canvas en el DOM
    const canvas = document.querySelector('canvas[data-chart="line"]') as HTMLCanvasElement;
    if (!canvas) {
      console.log('❌ makeLine - Canvas no encontrado en el DOM');
      return;
    }
    
    console.log('✅ makeLine - Canvas encontrado:', canvas);

    // Los datos ya vienen filtrados del backend
    const labels = data.ingresos_mensuales.map(item => 
      this.formatearFecha(item.mes)
    );

    console.log('🔍 makeLine - Labels:', labels);
    console.log('🔍 makeLine - Ingresos mensuales:', data.ingresos_mensuales);
    console.log('🔍 makeLine - Certificados mensuales:', data.certificados_mensuales);

    // Para el gráfico de línea, usaremos datos reales de certificados vs reservas
    // Sincronizar datos de certificados con los meses de ingresos
    const certificadosMap = new Map(data.certificados_mensuales.map(item => [item.mes, item.cantidad]));
    
    const certificadosData = data.ingresos_mensuales.map(item => 
      certificadosMap.get(item.mes) || 0
    );
    
    // Para reservas, usaremos el número de reservas en lugar de ingresos
    // Primero intentemos obtener datos de reservas reales
    const reservasData = data.ingresos_mensuales.map(item => {
      // Si no hay datos de reservas específicos, usar un valor basado en ingresos
      return Math.floor(item.ingresos / 1000); // Convertir ingresos a miles para mejor visualización
    });

    console.log('🔍 makeLine - Certificados data:', certificadosData);
    console.log('🔍 makeLine - Reservas data:', reservasData);

    const cfg: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { 
            label: 'Certificados', 
            data: certificadosData, 
            tension: 0.2, 
            fill: false,
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            pointRadius: 6,
            pointHoverRadius: 8,
            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
          },
          { 
            label: 'Reservas (miles CLP)', 
            data: reservasData, 
            tension: 0.2, 
            fill: false,
            borderColor: 'rgba(20, 184, 166, 1)',
            backgroundColor: 'rgba(20, 184, 166, 0.1)',
            borderWidth: 3,
            pointRadius: 6,
            pointHoverRadius: 8,
            pointBackgroundColor: 'rgba(20, 184, 166, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        aspectRatio: 2.5, // Hacer el gráfico más ancho
        plugins: { 
          legend: { 
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 20
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: (context) => {
                if (context.dataset.label === 'Certificados') {
                  return `${context.dataset.label}: ${context.parsed.y} certificados`;
                } else {
                  return `${context.dataset.label}: $${this.formatearNumero(context.parsed.y)}K`;
                }
              }
            }
          }
        },
        scales: { 
          x: {
            display: true,
            title: {
              display: true,
              text: 'Mes',
              font: {
                size: 14,
                weight: 'bold'
              }
            },
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
              font: {
                size: 12
              }
            }
          },
          y: { 
            beginAtZero: true,
            display: true,
            title: {
              display: true,
              text: 'Cantidad',
              font: {
                size: 14,
                weight: 'bold'
              }
            },
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.1)'
            },
            ticks: {
              font: {
                size: 12
              },
              callback: (v: any) => {
                const value = Number(v);
                return value.toString();
              }
            }
          } 
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        }
      }
    };
    
    console.log('🔍 makeLine - Configuración del gráfico:', cfg);
    this.lineChart = new Chart(canvas, cfg);
    console.log('✅ makeLine - Gráfico de línea creado:', this.lineChart);
  }

  // Métodos utilitarios para formateo
  private readonly LOCALE = 'es-CL';

  formatoCLP(n: number): string {
    return `$${n.toLocaleString(this.LOCALE)}`;
  }

  public formatearFecha(mes: string): string {
    try {
      const fecha = new Date(mes + '-01');
      return fecha.toLocaleDateString(this.LOCALE, { month: 'short', year: 'numeric' });
    } catch (error) {
      console.error('Error formateando fecha:', error);
      return mes;
    }
  }

  public getTituloReporte(): string {
    if (this.selectedMonths.length > 0) {
      if (this.selectedMonths.length === 1) {
        return 'Reporte de ' + this.formatearFecha(this.selectedMonths[0]);
      } else {
        return 'Reporte de ' + this.selectedMonths.length + ' meses seleccionados';
      }
    }
    return 'Reporte de Todos los Meses';
  }

  public getMesesDisponibles(): string[] {
    const data = this.dashboardData();
    if (!data || !data.ingresos_mensuales) {
      return [];
    }
    return data.ingresos_mensuales.map(item => item.mes);
  }



  public isMesSeleccionado(mes: string): boolean {
    return this.selectedMonths.includes(mes);
  }

  public toggleMes(mes: string): void {
    console.log('🔍 Toggleando mes:', mes);
    const index = this.selectedMonths.indexOf(mes);
    if (index > -1) {
      this.selectedMonths.splice(index, 1);
    } else {
      this.selectedMonths.push(mes);
    }
    // No cargar automáticamente, solo actualizar la selección
  }

  public seleccionarTodosLosMeses(): void {
    console.log('🔍 Seleccionando todos los meses');
    this.selectedMonths = [...this.getMesesDisponibles()];
    // No cargar automáticamente, solo actualizar la selección
  }

  public deseleccionarTodosLosMeses(): void {
    console.log('🔍 Deseleccionando todos los meses');
    this.selectedMonths = [];
    // No cargar automáticamente, solo actualizar la selección
  }

  public aplicarFiltros(): void {
    console.log('🔍 Aplicando filtros para meses:', this.selectedMonths);
    this.cargarDashboardConFiltros();
  }

  public verTodosLosMeses(): void {
    console.log('🔍 Viendo todos los meses');
    this.selectedMonths = [];
    this.cargarDashboardConFiltros();
  }

  private formatearNumero(n: number): string {
    try {
      return n.toLocaleString(this.LOCALE);
    } catch (error) {
      console.error('Error formateando número:', error);
      return n.toString();
    }
  }

  getTotalReservas(): number {
    const data = this.dashboardData();
    if (!data) return 0;
    return data.resumen_espacios.reduce((sum, e) => sum + e.total_reservas, 0) + data.kpis[1].value;
  }

  getTotalIngresos(): number {
    const data = this.dashboardData();
    if (!data) return 0;
    return data.kpis[2].value;
  }
}
