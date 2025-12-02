import { Component, OnInit, OnDestroy, ViewChild, ElementRef, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import SignaturePad from 'signature_pad';

@Component({
  selector: 'app-signature-pad',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './signature-pad.component.html',
  styleUrls: ['./signature-pad.component.css']
})
export class SignaturePadComponent implements OnInit, OnDestroy {
  @ViewChild('canvas', { static: true }) canvasRef!: ElementRef<HTMLCanvasElement>;
  @Input() width: number = 400;
  @Input() height: number = 200;
  @Input() existingSignature: string | null = null; // Base64 de firma existente
  @Output() signatureChange = new EventEmitter<string | null>();
  @Output() cleared = new EventEmitter<void>();

  private signaturePad!: SignaturePad;
  signatureData: string | null = null;

  ngOnInit(): void {
    this.initSignaturePad();
    if (this.existingSignature) {
      this.loadExistingSignature();
    }
  }

  ngOnDestroy(): void {
    if (this.signaturePad) {
      this.signaturePad.off();
    }
  }

  private initSignaturePad(): void {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = this.width;
    canvas.height = this.height;

    this.signaturePad = new SignaturePad(canvas, {
      backgroundColor: 'rgb(255, 255, 255)',
      penColor: 'rgb(0, 0, 0)',
      minWidth: 1,
      maxWidth: 3,
      throttle: 16,
      minDistance: 5
    });

    // Ajustar para pantallas de alta densidad
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = this.width * ratio;
    canvas.height = this.height * ratio;
    canvas.getContext('2d')?.scale(ratio, ratio);
    this.signaturePad.clear();

    // Escuchar cambios
    this.signaturePad.addEventListener('endStroke', () => {
      this.updateSignature();
    });
  }

  private loadExistingSignature(): void {
    if (this.existingSignature) {
      const img = new Image();
      img.onload = () => {
        const ctx = this.canvasRef.nativeElement.getContext('2d');
        if (ctx) {
          ctx.clearRect(0, 0, this.width, this.height);
          ctx.drawImage(img, 0, 0, this.width, this.height);
          this.updateSignature();
        }
      };
      img.src = this.existingSignature;
    }
  }

  clear(): void {
    this.signaturePad.clear();
    this.signatureData = null;
    this.signatureChange.emit(null);
    this.cleared.emit();
  }

  private updateSignature(): void {
    if (!this.signaturePad.isEmpty()) {
      this.signatureData = this.signaturePad.toDataURL('image/png');
      this.signatureChange.emit(this.signatureData);
    } else {
      this.signatureData = null;
      this.signatureChange.emit(null);
    }
  }

  isEmpty(): boolean {
    return this.signaturePad.isEmpty();
  }

  getSignature(): string | null {
    return this.signatureData;
  }
}

