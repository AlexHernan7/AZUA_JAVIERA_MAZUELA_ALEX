import {
  Component, AfterViewInit, OnDestroy, ViewChild, ElementRef, signal, computed
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, ChartConfiguration } from 'chart.js/auto';

type Kpi = { label: string; value: number; prefix?: string; suffix?: string };

@Component({
  selector: 'app-reportes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reportes.component.html',
  styleUrls: ['./reportes.component.css']
})
export class ReportesComponent implements AfterViewInit, OnDestroy {

  // canvases
  @ViewChild('barCanvas') barCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('pieCanvas') pieCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('lineCanvas') lineCanvas!: ElementRef<HTMLCanvasElement>;

  private barChart?: Chart;
  private pieChart?: Chart;
  private lineChart?: Chart;

  // Filtro visual (mock)
  rango = signal<'7d' | '30d' | '90d'>('30d');

  // Datos mock
  private datos = {
    ingresosPorMes: [320000, 480000, 510000, 420000, 650000, 710000],
    meses: ['Nov', 'Dic', 'Ene', 'Feb', 'Mar', 'Abr'],
    reservasPorTipo: [
      { tipo: 'Cancha', cantidad: 86, monto: 430000 },
      { tipo: 'Sala 1', cantidad: 64, monto: 448000 },
      { tipo: 'Sala 2', cantidad: 52, monto: 364000 },
    ],
    certificados: { cantidad: 187, monto: 374000 },
    usuarios: { total: 524, nuevos: 41 },
  };

  kpis = computed<Kpi[]>(() => {
    const totalReservas = this.datos.reservasPorTipo.reduce((a, b) => a + b.cantidad, 0);
    const montoReservas = this.datos.reservasPorTipo.reduce((a, b) => a + b.monto, 0);
    const totalIngresos = montoReservas + this.datos.certificados.monto;
    return [
      { label: 'Espacios arrendados', value: totalReservas },
      { label: 'Certificados descargados', value: this.datos.certificados.cantidad },
      { label: 'Ingresos (CLP)', value: totalIngresos, prefix: '$' },
      { label: 'Usuarios en la Junta', value: this.datos.usuarios.total },
    ];
  });

  ngAfterViewInit(): void {
    this.makeBar();
    this.makePie();
    this.makeLine();
  }

  ngOnDestroy(): void {
    this.barChart?.destroy();
    this.pieChart?.destroy();
    this.lineChart?.destroy();
  }

  private makeBar() {
    const cfg: ChartConfiguration<'bar'> = {
      type: 'bar',
      data: {
        labels: this.datos.meses,
        datasets: [{
          label: 'Ingresos (CLP)',
          data: this.datos.ingresosPorMes,
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false }, tooltip: { enabled: true } },
        scales: {
          y: {
            ticks: {
              callback: (v: any) => `$${Number(v).toLocaleString('es-CL')}`
            }
          }
        }
      }
    };
    this.barChart = new Chart(this.barCanvas.nativeElement, cfg);
  }

  private makePie() {
    const cfg: ChartConfiguration<'pie'> = {
      type: 'pie',
      data: {
        labels: this.datos.reservasPorTipo.map(r => r.tipo),
        datasets: [{ data: this.datos.reservasPorTipo.map(r => r.cantidad) }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } }
      }
    };
    this.pieChart = new Chart(this.pieCanvas.nativeElement, cfg);
  }

  private makeLine() {
    const cfg: ChartConfiguration<'line'> = {
      type: 'line',
      data: {
        labels: this.datos.meses,
        datasets: [
          { label: 'Certificados', data: [22, 28, 30, 26, 40, 41], tension: 0.35, fill: false },
          { label: 'Reservas', data: [38, 40, 45, 42, 52, 56], tension: 0.35, fill: false },
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { beginAtZero: true } }
      }
    };
    this.lineChart = new Chart(this.lineCanvas.nativeElement, cfg);
  }

  formatoCLP(n: number) {
    return `$${n.toLocaleString('es-CL')}`;
  }
}
