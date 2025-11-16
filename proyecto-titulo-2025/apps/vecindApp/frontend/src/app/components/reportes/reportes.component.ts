import {
  Component,
  AfterViewInit,
  OnDestroy,
  signal,
  computed,
  OnInit
} from '@angular/core';
import { CommonModule } from '@angular/common';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Chart, ChartConfiguration } from 'chart.js/auto';
import {
  ReporteService,
  DashboardResponse
} from '../../services/reporte.service';
import { Subject, takeUntil } from 'rxjs';

// 👇 Agregamos "type" para saber si es money o count
type Kpi = {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  type?: 'money' | 'count';
};

@Component({
  selector: 'app-report',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reportes.component.html',
  styleUrls: ['./reportes.component.css']
})
export class ReportesComponent implements OnInit, AfterViewInit, OnDestroy {

  // Charts
  private barChart?: Chart;
  private pieChart?: Chart;
  private lineChart?: Chart;
  private certMoneyChart?: Chart; // 👈 NUEVO gráfico de ingresos por certificados

  private destroy$ = new Subject<void>();

  // Filtro de meses (selección múltiple)
  selectedMonths: string[] = [];

  // Estado para el modo del gráfico de línea (certificados vs reservas)
  viewLineMode: 'cantidad' | 'monto' = 'cantidad';

  // Estados
  loading = signal(false);
  error = signal<string | null>(null);

  // Datos del dashboard como signal
  dashboardData = signal<DashboardResponse | null>(null);

  // 👇 Aquí marcamos qué KPI es de dinero (index === 2 -> Ingresos Totales)
  kpis = computed<Kpi[]>(() => {
    const data = this.dashboardData();
    if (!data) return [];

    return data.kpis.map((kpi, index) => ({
      label: kpi.label,
      value: kpi.value,
      prefix: kpi.prefix,
      suffix: kpi.suffix,
      type: index === 2 ? 'money' : 'count' // 👈 sólo el 3er KPI es de dinero
    }));
  });

  constructor(private reporteService: ReporteService) { Chart.defaults.devicePixelRatio = 3;}

  ngOnInit(): void {
    this.cargarDashboard();
  }

  ngAfterViewInit(): void {
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
    this.certMoneyChart?.destroy();
  }

  // ==========================
  //  CARGA DE DATOS
  // ==========================

  cargarDashboard(): void {
    this.loading.set(true);
    this.error.set(null);

    const token = localStorage.getItem('vecindapp_token');

    // Últimos 6 meses
    const ahora = new Date();
    const fechaDesde = new Date(ahora.getFullYear(), ahora.getMonth() - 6, 1);
    const fechaHasta = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0);

    const fechaDesdeStr = fechaDesde.toISOString().split('T')[0];
    const fechaHastaStr = fechaHasta.toISOString().split('T')[0];

    this.reporteService.getDashboard(fechaDesdeStr, fechaHastaStr)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.dashboardData.set(data);
          this.loading.set(false);
          this.crearGraficosSiDisponibles();
        },
        error: (error) => {
          this.error.set(`Error al cargar los reportes: ${error.message || error.status || 'Error desconocido'}`);
          this.loading.set(false);
        }
      });
  }

  private crearGraficosSiDisponibles(): void {
    if (!this.dashboardData()) return;

    setTimeout(() => {
      try {
        this.makeBar();
        this.makePie();
        this.makeLine();
        this.makeCertificadosMoney(); // 👈 nuevo gráfico
      } catch (error) {
        this.crearGraficosIndividualmente();
      }
    }, 100);
  }

  private crearGraficosIndividualmente(): void {
    try {
      this.makeBar();
    } catch (error) {
      // Error silencioso
    }

    try {
      this.makePie();
    } catch (error) {
      // Error silencioso
    }

    try {
      this.makeLine();
    } catch (error) {
      // Error silencioso
    }

    try {
      this.makeCertificadosMoney();
    } catch (error) {
      // Error silencioso
    }
  }

  // ==========================
  //  FILTRO POR MESES
  // ==========================

  public resetFilter(): void {
    this.selectedMonths = [];
    this.cargarDashboardConFiltros();
  }

  private cargarDashboardConFiltros(): void {
    this.loading.set(true);
    this.error.set(null);

    const ahora = new Date();
    const fechaDesde = new Date(ahora.getFullYear(), ahora.getMonth() - 6, 1);
    const fechaHasta = new Date(ahora.getFullYear(), ahora.getMonth() + 1, 0);

    const fechaDesdeStr = fechaDesde.toISOString().split('T')[0];
    const fechaHastaStr = fechaHasta.toISOString().split('T')[0];

    const meses = this.selectedMonths.length > 0 ? this.selectedMonths : undefined;

    this.reporteService.getDashboard(fechaDesdeStr, fechaHastaStr, meses)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.dashboardData.set(data);
          this.loading.set(false);

          setTimeout(() => {
            this.makeBar();
            this.makePie();
            this.makeLine();
            this.makeCertificadosMoney(); // 👈 también al filtrar
          }, 100);
        },
        error: (error) => {
          this.error.set(`Error al cargar los reportes: ${error.message || 'Error desconocido'}`);
          this.loading.set(false);
        }
      });
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
    const index = this.selectedMonths.indexOf(mes);
    if (index > -1) {
      this.selectedMonths.splice(index, 1);
    } else {
      this.selectedMonths.push(mes);
    }
  }

  public seleccionarTodosLosMeses(): void {
    this.selectedMonths = [...this.getMesesDisponibles()];
  }

  public deseleccionarTodosLosMeses(): void {
    this.selectedMonths = [];
  }

  public aplicarFiltros(): void {
    this.cargarDashboardConFiltros();
  }

  public verTodosLosMeses(): void {
    this.selectedMonths = [];
    this.cargarDashboardConFiltros();
  }

  // ==========================
  //  CONTROL MODO GRÁFICO LÍNEA
  // ==========================

  public setLineMode(mode: 'cantidad' | 'monto') {
    if (this.viewLineMode === mode) return;
    this.viewLineMode = mode;
    this.makeLine();
  }

  // ==========================
  //  GRÁFICOS
  // ==========================

  private makeBar() {
    const data = this.dashboardData();
    if (!data) return;

    this.barChart?.destroy();

    if (!data.ingresos_mensuales || data.ingresos_mensuales.length === 0) {
      return;
    }

    const canvas = document.querySelector('canvas[data-chart="bar"]') as HTMLCanvasElement;
    if (!canvas) return;

    const labels = data.ingresos_mensuales.map(item =>
      this.formatearFecha(item.mes)
    );

    const chartData = data.ingresos_mensuales.map(item => item.ingresos);

    const cfg: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Ingresos por reservas (CLP)',
          data: chartData,
          backgroundColor: 'rgba(20, 184, 166, 0.8)',
          borderColor: 'rgba(20, 184, 166, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            callbacks: {
              label: (context) => {
                const value = typeof context.parsed.y === 'number' ? context.parsed.y : 0;
                return `$${this.formatearNumero(value)}`;
              }
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
    if (!data) return;

    this.pieChart?.destroy();

    if (!data.distribucion_reservas || data.distribucion_reservas.length === 0) {
      return;
    }

    const canvas = document.querySelector('canvas[data-chart="pie"]') as HTMLCanvasElement;
    if (!canvas) return;

    const labels = data.distribucion_reservas.map(item => item.espacio);
    const chartData = data.distribucion_reservas.map(item => item.cantidad);

    const cfg: ChartConfiguration<'pie'> = {
      type: 'pie',
      data: {
        labels,
        datasets: [{
          data: chartData,
          backgroundColor: [
            'rgba(20, 184, 166, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)'
          ],
          borderColor: [
            'rgba(20, 184, 166, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(59, 130, 246, 1)',
            'rgba(239, 68, 68, 1)',
            'rgba(139, 92, 246, 1)',
            'rgba(16, 185, 129, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
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
    const data = this.dashboardData();
    if (!data) {
      return;
    }

    this.lineChart?.destroy();

    const canvas = document.querySelector('canvas[data-chart="line"]') as HTMLCanvasElement;
    if (!canvas) {
      return;
    }

    const labels = data.ingresos_mensuales.map(item =>
      this.formatearFecha(item.mes)
    );

    const certificadosMap = new Map(
      data.certificados_mensuales.map(item => [item.mes, item.cantidad])
    );

    const certificadosData = data.ingresos_mensuales.map(item =>
      certificadosMap.get(item.mes) || 0
    );

    const isCantidad = this.viewLineMode === 'cantidad';

    // Calcular datos de reservas según el modo
    let reservasData: number[];
    if (isCantidad) {
      // En modo cantidad: usar la cantidad real de reservas por mes del backend
      reservasData = data.ingresos_mensuales.map(item => 
        item.cantidad_reservas || 0
      );
    } else {
      // En modo dinero: mostrar miles de CLP
      reservasData = data.ingresos_mensuales.map(item =>
        Math.floor(item.ingresos / 1000) // miles CLP
      );
    }

    const cfg: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: isCantidad ? 'Certificados (cantidad)' : 'Certificados (aprox. CLP)',
            data: certificadosData,
            tension: 0.2,
            fill: false,
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
          },
          {
            label: isCantidad ? 'Reservas (cantidad)' : 'Reservas (miles CLP)',
            data: reservasData,
            tension: 0.2,
            fill: false,
            borderColor: 'rgba(20, 184, 166, 1)',
            backgroundColor: 'rgba(20, 184, 166, 0.1)',
            borderWidth: 3,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: 'rgba(20, 184, 166, 1)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        aspectRatio: 2.3,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 18
            }
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: (context) => {
                const rawLabel = (context.dataset?.label ?? '') as string;
                const value = typeof context.parsed.y === 'number' ? context.parsed.y : 0;

                if (isCantidad) {
                  return rawLabel
                    ? `${rawLabel}: ${value}`
                    : `${value}`;
                } else {
                  const isMiles = rawLabel.includes('miles');
                  const base = `$${this.formatearNumero(value)}${isMiles ? 'K' : ''}`;
                  return rawLabel
                    ? `${rawLabel}: ${base}`
                    : base;
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
              color: 'rgba(0, 0, 0, 0.06)'
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
              text: isCantidad ? 'Cantidad' : 'Monto (aprox.)',
              font: {
                size: 14,
                weight: 'bold'
              }
            },
            grid: {
              display: true,
              color: 'rgba(0, 0, 0, 0.06)'
            },
            ticks: {
              font: {
                size: 12
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

    this.lineChart = new Chart(canvas, cfg);
  }

  // ===== NUEVO GRÁFICO: INGRESOS POR CERTIFICADOS (DINERO) =====
  private makeCertificadosMoney() {
    const data = this.dashboardData();
    if (!data) return;

    this.certMoneyChart?.destroy();

    if (!data.certificados_mensuales || data.certificados_mensuales.length === 0) {
      return;
    }

    const canvas = document.querySelector('canvas[data-chart="cert-money"]') as HTMLCanvasElement;
    if (!canvas) return;

    const labels = data.certificados_mensuales.map(item =>
      this.formatearFecha(item.mes)
    );

    const ingresos = data.certificados_mensuales.map(item =>
      item.cantidad * 2000 // 2000 CLP por certificado (puedes parametrizarlo si quieres)
    );

    const cfg: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Ingresos por certificados (CLP)',
          data: ingresos,
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgba(59, 130, 246, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                const value = typeof context.parsed.y === 'number' ? context.parsed.y : 0;
                return `$${this.formatearNumero(value)}`;
              }
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

    this.certMoneyChart = new Chart(canvas, cfg);
  }

  // ==========================
  //  UTILITARIOS DE FORMATO
  // ==========================

  private readonly LOCALE = 'es-CL';

  formatoCLP(n: number): string {
    return `$${n.toLocaleString(this.LOCALE)}`;
  }

  public formatearFecha(mes: string): string {
    try {
      const fecha = new Date(mes + '-01');
      return fecha.toLocaleDateString(this.LOCALE, { month: 'short', year: 'numeric' });
    } catch (error) {
      return mes;
    }
  }

  private formatearNumero(n: number): string {
    try {
      return n.toLocaleString(this.LOCALE);
    } catch (error) {
      return n.toString();
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
    // ==========================
  //  EXPORTAR RESUMEN A CSV
  // ==========================
  public exportarResumenCSV(): void {
    const data = this.dashboardData();
    if (!data) {
      return;
    }

    // Encabezados
    const filas: string[] = [];
    filas.push('Espacio / Tipo,Cantidad,Ingresos (CLP)');

    // Filas por cada espacio
    data.resumen_espacios.forEach(espacio => {
      const nombre = espacio.nombre?.replace(/"/g, '""') ?? '';
      const cantidad = espacio.total_reservas ?? 0;
      const ingresos = espacio.ingresos ?? 0;
      filas.push(`"${nombre}",${cantidad},${ingresos}`);
    });

    // Fila de certificados (igual que en la tabla)
    const certificadosCantidad = data.kpis[1]?.value ?? 0;
    const certificadosIngresos = certificadosCantidad * 2000; // mismo cálculo que usas en la tabla
    filas.push(`"Certificados emitidos",${certificadosCantidad},${certificadosIngresos}`);

    // Fila total general
    const totalCantidad = this.getTotalReservas();
    const totalIngresos = this.getTotalIngresos();
    filas.push(`"Total general",${totalCantidad},${totalIngresos}`);

    // Unir todo en un string CSV
    const csvContent = '\uFEFF' + filas.join('\n'); // \uFEFF = BOM para que Excel respete UTF-8

    // Crear Blob y disparar descarga
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'resumen_reportes.csv';
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  }
    // ==========================
  //  EXPORTAR RESUMEN A PDF (PRO + GRÁFICOS)
  // ==========================
  public exportarResumenPDF(): void {
    const data = this.dashboardData();
    if (!data) {
      return;
    }

    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    // ====== ENCABEZADO ======
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.text('Resumen de espacios y certificados', 14, 20);

    // Subtítulo con el periodo del reporte
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    const tituloReporte = this.getTituloReporte();
    doc.text(tituloReporte, 14, 26);

    // Fecha de generación (lado derecho)
    const fecha = new Date().toLocaleString('es-CL');
    doc.setFontSize(9);
    doc.setTextColor(100);
    doc.text(`Generado: ${fecha}`, pageWidth - 14, 10, { align: 'right' });

    // Línea separadora
    doc.setDrawColor(220);
    doc.line(14, 30, pageWidth - 14, 30);

    // ====== CONSTRUIR TABLA ======
    const filas: any[] = [];

    data.resumen_espacios.forEach(espacio => {
      filas.push([
        espacio.nombre ?? '',
        espacio.total_reservas ?? 0,
        `$${(espacio.ingresos ?? 0).toLocaleString('es-CL')}`
      ]);
    });

    const certificadosCantidad = data.kpis[1]?.value ?? 0;
    const certificadosIngresos = certificadosCantidad * 2000;

    filas.push([
      'Certificados emitidos',
      certificadosCantidad,
      `$${certificadosIngresos.toLocaleString('es-CL')}`
    ]);

    filas.push([
      'Total general',
      this.getTotalReservas(),
      `$${this.getTotalIngresos().toLocaleString('es-CL')}`
    ]);

    autoTable(doc, {
      startY: 34,
      head: [['Espacio / Tipo', 'Cantidad', 'Ingresos (CLP)']],
      body: filas,
      styles: {
        font: 'helvetica',
        fontSize: 10,
        cellPadding: 3
      },
      headStyles: {
        fillColor: [15, 118, 110], // teal
        textColor: 255,
        fontStyle: 'bold'
      },
      columnStyles: {
        0: { cellWidth: 90 },
        1: { cellWidth: 30, halign: 'right' },
        2: { cellWidth: 50, halign: 'right' }
      },
      alternateRowStyles: {
        fillColor: [248, 250, 252]
      },
      margin: { left: 14, right: 14 }
    });

    let currentY = (doc as any).lastAutoTable?.finalY ?? 34;

    // ========= SECCIÓN GRÁFICOS =========
    doc.setTextColor(0);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);

    // Espacio antes de los gráficos
    currentY += 10;

    // Tamaño estándar para todos los gráficos
    const chartMarginX = 14;
    const chartWidth = pageWidth - chartMarginX * 2;
    const chartHeight = 70;

    const addNewPageIfNeeded = () => {
      if (currentY + chartHeight + 20 > pageHeight) {
        doc.addPage();
        currentY = 20;
      }
    };

    // ====== 1) Ingresos mensuales por reservas (barChart) ======
    if (this.barChart && typeof this.barChart.toBase64Image === 'function') {
      addNewPageIfNeeded();
      doc.setFontSize(12);
      doc.text('Ingresos mensuales por reservas', chartMarginX, currentY);
      currentY += 4;

      const barImg = this.barChart.toBase64Image();
      doc.addImage(barImg, 'PNG', chartMarginX, currentY, chartWidth, chartHeight);
      currentY += chartHeight + 8;
    }

  // ====== 2) Distribución de reservas por espacio (pieChart) ======
if (this.pieChart && typeof this.pieChart.toBase64Image === 'function') {
  addNewPageIfNeeded();

  doc.setFontSize(12);
  doc.setTextColor(0);
  const titleY = currentY;
  doc.text('Distribución de reservas por espacio', chartMarginX, titleY);

  // Posición del gráfico
  const chartY = titleY + 4;
  const pieImg = this.pieChart.toBase64Image();
  doc.addImage(pieImg, 'PNG', chartMarginX, chartY, chartWidth, chartHeight);

  // ==== Porcentajes debajo del gráfico ====
  const data = this.dashboardData();
  if (data && data.distribucion_reservas && data.distribucion_reservas.length > 0) {
    const total = data.distribucion_reservas
      .reduce((sum, item) => sum + (item.cantidad ?? 0), 0);

    if (total > 0) {
      let percY = chartY + chartHeight + 6; // empieza justo bajo el gráfico

      doc.setFontSize(9);
      doc.setTextColor(80);

      data.distribucion_reservas.forEach((item) => {
        const cantidad = item.cantidad ?? 0;
        const porcentaje = (cantidad / total) * 100;
        const linea = `${item.espacio}: ${porcentaje.toFixed(1)}% (${cantidad} reservas)`;

        // Si nos acercamos al final de la página, agregamos otra
        if (percY > pageHeight - 20) {
          doc.addPage();
          percY = 20;
        }

        doc.text(linea, chartMarginX + 2, percY);
        percY += 4;
      });

      currentY = percY + 4; // dejamos currentY después de la lista
    } else {
      currentY = chartY + chartHeight + 8;
    }
  } else {
    currentY = chartY + chartHeight + 8;
  }
}


    // ====== 3) Ingresos mensuales por certificados (certMoneyChart) ======
    if (this.certMoneyChart && typeof this.certMoneyChart.toBase64Image === 'function') {
      addNewPageIfNeeded();
      doc.setFontSize(12);
      doc.text('Ingresos mensuales por certificados', chartMarginX, currentY);
      currentY += 4;

      const certImg = this.certMoneyChart.toBase64Image();
      doc.addImage(certImg, 'PNG', chartMarginX, currentY, chartWidth, chartHeight);
      currentY += chartHeight + 8;
    }

    // // ====== 4) Certificados vs reservas (lineChart) ======
    // if (this.lineChart && typeof this.lineChart.toBase64Image === 'function') {
    //   addNewPageIfNeeded();
    //   doc.setFontSize(12);
    //   doc.text('Certificados vs reservas', chartMarginX, currentY);
    //   currentY += 4;

    //   const lineImg = this.lineChart.toBase64Image();
    //   doc.addImage(lineImg, 'PNG', chartMarginX, currentY, chartWidth, chartHeight);
    //   currentY += chartHeight + 8;
    // }

    // ====== NOTA / PIE ======
    addNewPageIfNeeded();
    doc.setFontSize(9);
    doc.setTextColor(120);
    doc.text(
      'Este reporte fue generado automáticamente desde la plataforma de la junta de vecinos.',
      chartMarginX,
      currentY + 4
    );

    // ====== FOOTER CON NÚMERO DE PÁGINA ======
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      const footerText = `Página ${i} de ${totalPages}`;
      doc.setFontSize(9);
      doc.setTextColor(130);
      doc.text(
        footerText,
        pageWidth / 2,
        pageHeight - 10,
        { align: 'center' }
      );
    }

    // Descargar
    doc.save('resumen_reportes.pdf');
  }


}
